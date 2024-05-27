import subprocess

def run_iperf_test(server_ip, test_duration):
    # iperf3 명령어 생성
    iperf_command = f"iperf3 -c {server_ip} -t {test_duration}"
    
    # 명령어 실행
    process = subprocess.Popen(iperf_command, shell=True)
    
    # 테스트가 완료될 때까지 대기
    process.wait()
    
    # 테스트가 완료되면 메시지 출력
    print("네트워크 성능 측정이 완료되었습니다.")

# 테스트 서버 IP 주소
server_ip = input("테스트할 서버의 IP 주소를 입력하세요: ")

while True:
    # 사용자로부터 테스트 지속 시간 입력 받기
    test_duration = int(input("테스트 지속 시간(초)를 입력하세요: "))
    
    # 테스트 실행
    run_iperf_test(server_ip, test_duration)
    
    # 계속할지 여부 확인
    continue_test = input("더 테스트를 진행하시겠습니까? (y/n): ")
    if continue_test.lower() != 'y':
        break
