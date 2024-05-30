import subprocess
import threading
from datetime import datetime

def run_iperf_test(server_ip, log_file):
    iperf_command = ["iperf3", "-c", server_ip, "-t", "0", "-i", "1"]
    with open(log_file, "w") as f:
        process = subprocess.Popen(iperf_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            f.write(line)        # 로그 파일에 저장
        process.stdout.close()
        process.wait()

def main():
    # 추가할 서버의 개수 입력 받기
    num_servers = int(input("추가할 서버의 개수를 입력하세요: "))
    
    # 서버 IP 주소 입력 받기
    server_ips = []
    for i in range(num_servers):
        server_ip = input(f"{i+1}번째 서버의 IP 주소를 입력하세요: ")
        server_ips.append(server_ip)
    
    threads = []

    try:
        for server_ip in server_ips:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # 현재 시간을 타임스탬프 형식으로 가져오기
            log_file = f"iperf_log_{server_ip}_{timestamp}.txt"  # 각 서버 IP 주소별로 고유한 로그 파일 생성
            print(f"{server_ip}에 대한 네트워크 성능 측정을 시작합니다... 로그 파일: {log_file}")
            thread = threading.Thread(target=run_iperf_test, args=(server_ip, log_file))
            thread.start()
            threads.append(thread)

        # 모든 스레드가 종료될 때까지 대기
        for thread in threads:
            thread.join()
    
    except KeyboardInterrupt:
        print("\n전체 테스트가 사용자에 의해 중단되었습니다.")
        # 모든 스레드를 종료하기 위한 로직 추가가 필요할 수 있습니다.

if __name__ == "__main__":
    main()
