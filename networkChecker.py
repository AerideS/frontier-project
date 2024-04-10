import asyncio
import asyncio.selector_events
import subprocess

class networkChecker:
    '''
    주기적으로 서버에 ping을 보내어 서버와의 연결을 확인함
    period 기준으로 ping 보냄
    '''
    def __init__(self, ip_addr, period) -> None:
        self.server_ip_addr = ip_addr
        self.period = period
        self.keep_ping = True
        
    async def ping(self):
        '''
        서버주소 : server_ip_addr 에 ping
        '''
        while self.keep_ping:
            try:
                # ping 명령어 실행
                process = await asyncio.create_subprocess_shell(
                    f"ping -c 1 {self.server_ip_addr}",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                _, stderr = await process.communicate()
                # ping 결과 확인
                if process.returncode == 0:  # ping 성공
                    print(f"{self.server_ip_addr} is reachable.")
                    yield True
                else:  # ping 실패
                    f"{self.server_ip_addr} is not reachable."
                    yield False

                # 대기 시간 설정
                await asyncio.sleep(self.period)
            except asyncio.CancelledError:
                print("task canceled")

        
    async def start(self):
        self.keep_ping = True
        async for result in self.ping():
            print(result)
            
    async def stopPing(self):
        self.keep_ping = False
            
        
async def work_organiser(network_checker):
    '''
    비동기 task의 배치를 위함.
    '''
    task1 = asyncio.create_task(network_checker.start())  
    task2 = asyncio.create_task(network_checker.stopPing())
    await asyncio.wait(
        [
            task1, task2
        ]
    )

if __name__ == '__main__':
    network_checker = networkChecker('localhost', 5)
    asyncio.run(work_organiser(network_checker))
    
    
    