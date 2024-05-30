import subprocess

def run_iperf_server():
    iperf_command = ["iperf3", "-s"]
    process = subprocess.Popen(iperf_command)
    return process

def main():
    try:
        print("iperf3 서버를 시작합니다...")
        server_process = run_iperf_server()

        # 서버 프로세스가 종료될 때까지 대기
        server_process.wait()
    
    except KeyboardInterrupt:
        print("\n서버가 사용자에 의해 중단되었습니다.")
        server_process.terminate()
        print("서버가 종료되었습니다.")

if __name__ == "__main__":
    main()
