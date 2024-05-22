#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/socket.h>
#include <net/sock.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/net.h>
#include <linux/string.h>
#include <linux/in.h>
#include <linux/time.h>
#include <net/tcp.h>
#include <linux/udp.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>
#include <linux/inet.h>

#define MAX_NAT_ENTRIES 65535
#define SET_ENTRY 133
#define RWPERM 0644

/* NAT table entry*/
struct nat_entry {
    __be32 lan_ipaddr;
    __be16 lan_port;
    unsigned long sec; /*timestamp in seconds*/
    u_int8_t valid;
};

/* the NAT table is indexed by the translated port i.e. source port after NAT for outgoing packet */
static struct nat_entry nat_table[MAX_NAT_ENTRIES];

static __be32 myip;
static __be32 priv_ip_mask;
static __be32 priv_ip_first;
static int start = 0;
static int timeout = 60;
static char lanstr[20] = "192.168.56.0/24";
static u_int16_t port = 10000;
module_param(start, int, S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP);

/* proc fs entries */
static struct proc_dir_entry *knat;
static struct proc_dir_entry *proc_ip, *proc_lan, *proc_timeout;

unsigned long ip_asc_to_int(char *strip)
{
    unsigned long ip;
    unsigned int a[4];

    sscanf(strip, "%u.%u.%u.%u", &a[0], &a[1], &a[2], &a[3]);
    ip = (a[0] << 24) + (a[1] << 16) + (a[2] << 8) + a[3];
    return ip;
}

void inet_ntoa(char *tmp, u_int32_t int_ip)
{
    sprintf(tmp, "%d.%d.%d.%d",
            (int_ip) & 0xFF,
            (int_ip >> 8) & 0xFF,
            (int_ip >> 16) & 0xFF,
            (int_ip >> 24) & 0xFF);
    return;
}

/* proc fs read write */

static ssize_t proc_read_ip(struct file *file, char __user *buf, size_t count, loff_t *off)
{
    char tmp[16];
    int len;

    // 함수 입구에 로그 추가
    printk(KERN_INFO "proc_read_ip: Entered\n");

    if (*off > 0)
    {
        // 오프셋이 0보다 큰 경우에도 로그 추가
        printk(KERN_INFO "proc_read_ip: Offset greater than 0, returning 0\n");
        return 0;
    }

    inet_ntoa(tmp, myip);
    len = sprintf(buf, "%s\n", tmp);
    *off += len;

    // IP 주소가 성공적으로 읽힌 경우에 대한 로그 추가
    printk(KERN_INFO "proc_read_ip: Successfully read IP\n");

    return len;
}

static ssize_t proc_write_ip(struct file *file, const char __user *buffer, size_t count, loff_t *off)
{
    char tmp[16];
    if (count > 15)
    {
        return -ENOSPC;
    }

    if (copy_from_user(tmp, buffer, count))
    {
        return -EFAULT;
    }
    tmp[count] = '\0';
    myip = htonl(ip_asc_to_int(tmp));
    return count;
}

static ssize_t proc_read_timeout(struct file *file, char __user *buf, size_t count, loff_t *off)
{
    int len;
    if (*off > 0)
    {
        return 0;
    }
    len = sprintf(buf, "%u\n", timeout);
    *off += len;
    return len;
}

static ssize_t proc_write_timeout(struct file *file, const char __user *buffer, size_t count, loff_t *off)
{
#define MAX_TIMEOUT_LEN_CHARS 6
    char tmp[10];
    if (count > MAX_TIMEOUT_LEN_CHARS)
    {
        return -EFAULT;
    }

    if (copy_from_user(tmp, buffer, count))
    {
        return -EFAULT;
    }
    tmp[count] = '\0';
    timeout = simple_strtoul(tmp, NULL, 10);
    return count;
}

static ssize_t proc_read_lan(struct file *file, char __user *buf, size_t count, loff_t *off)
{
    int len;
    if (*off > 0)
    {
        return 0;
    }
    len = sprintf(buf, "%s\n", lanstr);
    *off += len;
    return len;
}

static ssize_t proc_write_lan(struct file *file, const char __user *buffer, size_t count, loff_t *off)
{
    int mask, i;
    char tmp[20];
    char *s;
    u_int32_t le_mask = 0;
    if (count > 20)
    {
        return -EFAULT;
    }

    if (copy_from_user(lanstr, buffer, count))
    {
        return -EFAULT;
    }
    lanstr[count] = '\0';
    strncpy(tmp, lanstr, count + 1);
    s = strstr(tmp, "/");
    if (s == NULL)
    {
        return -EFAULT;
    }
    *s = '\0';
    s++;

    priv_ip_first = htonl(ip_asc_to_int(tmp));
    mask = (simple_strtoul(s, NULL, 10));
    for (i = 0; i < mask; i++)
    {
        le_mask = le_mask << 1;
        le_mask = le_mask | 1;
    }
    priv_ip_mask = le_mask;
    return count;
}

/* update the checksums for tcp and ip */
void update_tcp_ip_checksum(struct sk_buff *skb, struct tcphdr *tcph, struct iphdr *iph)
{
    int len;
    if (!skb || !iph || !tcph)
        return;
    len = skb->len;

    /* update ip checksum */
    iph->check = 0;
    iph->check = ip_fast_csum((unsigned char *)iph, iph->ihl);
    /* update tcp checksum */
    tcph->check = 0;
    tcph->check = tcp_v4_check(
        len - 4 * iph->ihl,
        iph->saddr, iph->daddr,
        csum_partial((char *)tcph, len - 4 * iph->ihl,
                     0));
    return;
}

void update_udp_ip_checksum(struct sk_buff *skb, struct udphdr *udph, struct iphdr *iph)
{
    int len;
    if (!skb || !iph || !udph)
        return;
    len = skb->len;

    /* update ip checksum */
    iph->check = 0;
    iph->check = ip_fast_csum((unsigned char *)iph, iph->ihl);
    /* update udp checksum */
    udph->check = 0;
    udph->check = csum_tcpudp_magic(
        iph->saddr, iph->daddr,
        len - 4 * iph->ihl, IPPROTO_UDP,
        csum_partial((char *)udph, len - 4 * iph->ihl,
                     0));
    return;
}

/* find the nat table entry for given lan port.
@sport = source port as obtained from packet from lan */
__be16 find_nat_entry(__be32 saddr, __be16 sport)
{
    int i = 0;
    unsigned int t = 0;
    for (i = 0; i < MAX_NAT_ENTRIES; i++)
    {
        if ((nat_table[i].lan_ipaddr == saddr) && (nat_table[i].lan_port == sport) && nat_table[i].valid)
        {
            t = (ktime_get_seconds() - nat_table[i].sec);
            if (t > timeout)
            {
                printk("NAT Entry timeout\n");
                nat_table[i].valid = 0;
                return 0;
            }
            return i;
        }
    }
    return 0;
}

/* NAT pre-routing hook: handles packets coming from LAN to be sent to WAN */
static unsigned int main_hook_pre(void *priv, struct sk_buff *skb, const struct nf_hook_state *state)
{
    struct iphdr *iph;
    struct tcphdr *tcph;
    struct udphdr *udph;
    __be16 index;
    __be16 sport;

    if (!skb)
        return NF_ACCEPT;

    iph = ip_hdr(skb);
    if (!iph)
        return NF_ACCEPT;

    if (iph->saddr == myip)
        return NF_ACCEPT;

    /* handle TCP packets */
    if (iph->protocol == IPPROTO_TCP)
    {
        tcph = (struct tcphdr *)((__u32 *)iph + iph->ihl);
        sport = ntohs(tcph->source);
        index = find_nat_entry(iph->saddr, sport);
        if (!index)
        {
            printk(KERN_INFO "NAT: creating new TCP entry for %pI4:%u\n", &iph->saddr, sport);
            index = port++;
            nat_table[index].lan_ipaddr = iph->saddr;
            nat_table[index].lan_port = tcph->source;
            nat_table[index].sec = ktime_get_seconds();
            nat_table[index].valid = 1;
        }

        iph->saddr = myip;
        tcph->source = htons(index);
        update_tcp_ip_checksum(skb, tcph, iph);
        return NF_ACCEPT;
    }

    /* handle UDP packets */
    if (iph->protocol == IPPROTO_UDP)
    {
        udph = (struct udphdr *)((__u32 *)iph + iph->ihl);
        sport = ntohs(udph->source);
        index = find_nat_entry(iph->saddr, sport);
        if (!index)
        {
            printk(KERN_INFO "NAT: creating new UDP entry for %pI4:%u\n", &iph->saddr, sport);
            index = port++;
            nat_table[index].lan_ipaddr = iph->saddr;
            nat_table[index].lan_port = udph->source;
            nat_table[index].sec = ktime_get_seconds();
            nat_table[index].valid = 1;
        }

        iph->saddr = myip;
        udph->source = htons(index);
        update_udp_ip_checksum(skb, udph, iph);
        return NF_ACCEPT;
    }

    return NF_ACCEPT;
}

/* NAT post-routing hook: handles packets coming from WAN to be sent to LAN */
static unsigned int main_hook_post(void *priv, struct sk_buff *skb, const struct nf_hook_state *state)
{
    struct iphdr *iph;
    struct tcphdr *tcph;
    struct udphdr *udph;
    __be16 index;
    struct nat_entry entry;

    if (!skb)
        return NF_ACCEPT;

    iph = ip_hdr(skb);
    if (!iph)
        return NF_ACCEPT;

    if (iph->daddr == myip)
    {
        /* handle TCP packets */
        if (iph->protocol == IPPROTO_TCP)
        {
            tcph = (struct tcphdr *)((__u32 *)iph + iph->ihl);
            index = ntohs(tcph->dest);
            entry = nat_table[index];
            if (!entry.valid)
                return NF_DROP;

            iph->daddr = entry.lan_ipaddr;
            tcph->dest = entry.lan_port;
            update_tcp_ip_checksum(skb, tcph, iph);
            return NF_ACCEPT;
        }

        /* handle UDP packets */
        if (iph->protocol == IPPROTO_UDP)
        {
            udph = (struct udphdr *)((__u32 *)iph + iph->ihl);
            index = ntohs(udph->dest);
            entry = nat_table[index];
            if (!entry.valid)
                return NF_DROP;

            iph->daddr = entry.lan_ipaddr;
            udph->dest = entry.lan_port;
            update_udp_ip_checksum(skb, udph, iph);
            return NF_ACCEPT;
        }
    }

    return NF_ACCEPT;
}

/* Netfilter hooks structures */
static struct nf_hook_ops netfilter_ops_pre = {
    .hook = main_hook_pre,
    .pf = NFPROTO_IPV4,
    .hooknum = NF_INET_PRE_ROUTING,
    .priority = NF_IP_PRI_FIRST,
};

static struct nf_hook_ops netfilter_ops_post = {
    .hook = main_hook_post,
    .pf = NFPROTO_IPV4,
    .hooknum = NF_INET_POST_ROUTING,
    .priority = NF_IP_PRI_FIRST,
};

/* Proc operations structures */
static const struct proc_ops proc_fops_ip = {
    .proc_read = proc_read_ip,
    .proc_write = proc_write_ip,
};

static const struct proc_ops proc_fops_timeout = {
    .proc_read = proc_read_timeout,
    .proc_write = proc_write_timeout,
};

static const struct proc_ops proc_fops_lan = {
    .proc_read = proc_read_lan,
    .proc_write = proc_write_lan,
};

/* Module init function */
static int __init init(void)
{
    int ret;
    printk(KERN_INFO "Registering NAT module\n");

    knat = proc_mkdir("knat", NULL);
    if (!knat)
    {
        printk(KERN_ERR "Failed to create /proc/knat directory\n");
        return -ENOMEM;
    }

    proc_ip = proc_create("ip", RWPERM, knat, &proc_fops_ip);
    if (!proc_ip)
    {
        printk(KERN_ERR "Failed to create /proc/knat/ip entry\n");
        remove_proc_entry("knat", NULL);
        return -ENOMEM;
    }

    proc_timeout = proc_create("timeout", RWPERM, knat, &proc_fops_timeout);
    if (!proc_timeout)
    {
        printk(KERN_ERR "Failed to create /proc/knat/timeout entry\n");
        remove_proc_entry("ip", knat);
        remove_proc_entry("knat", NULL);
        return -ENOMEM;
    }

    proc_lan = proc_create("lan", RWPERM, knat, &proc_fops_lan);
    if (!proc_lan)
    {
        printk(KERN_ERR "Failed to create /proc/knat/lan entry\n");
        remove_proc_entry("timeout", knat);
        remove_proc_entry("ip", knat);
        remove_proc_entry("knat", NULL);
        return -ENOMEM;
    }

    ret = nf_register_net_hook(&init_net, &netfilter_ops_pre);
    if (ret)
    {
        printk(KERN_ERR "Failed to register netfilter pre-routing hook\n");
        remove_proc_entry("lan", knat);
        remove_proc_entry("timeout", knat);
        remove_proc_entry("ip", knat);
        remove_proc_entry("knat", NULL);
        return ret;
    }

    ret = nf_register_net_hook(&init_net, &netfilter_ops_post);
    if (ret)
    {
        printk(KERN_ERR "Failed to register netfilter post-routing hook\n");
        nf_unregister_net_hook(&init_net, &netfilter_ops_pre);
        remove_proc_entry("lan", knat);
        remove_proc_entry("timeout", knat);
        remove_proc_entry("ip", knat);
        remove_proc_entry("knat", NULL);
        return ret;
    }

    return 0;
}

/* Module cleanup function */
static void __exit cleanup(void)
{
    printk(KERN_INFO "Unregistering NAT module\n");

    remove_proc_entry("lan", knat);
    remove_proc_entry("timeout", knat);
    remove_proc_entry("ip", knat);
    remove_proc_entry("knat", NULL);

    nf_unregister_net_hook(&init_net, &netfilter_ops_pre);
    nf_unregister_net_hook(&init_net, &netfilter_ops_post);
}

module_init(init);
module_exit(cleanup);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("NAT module supporting TCP and UDP");







   







