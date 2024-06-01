import subprocess
import re
from datetime import datetime

class IperfRunner:
    def __init__(self, server_ip, port):
        self.server_ip = server_ip
        self.port = port
        self.start_time = datetime.now()

    # iperf3 명령어를 실행하여 출력 결과를 받아오는 함수
    def run_iperf3(self, bandwidth, duration):
        command = [
            'iperf3',
            '-c', self.server_ip,
            '-p', str(self.port),  # 포트 번호 추가
            '-u',
            '-b', bandwidth,
            '-t', str(duration),  # duration을 '-t' 옵션을 통해 설정
            '--get-server-output'
        ]

        try:
            # subprocess.run을 사용하여 명령어 실행 및 출력 캡처
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running iperf3: {e}")
            return None

    # iperf3 출력 결과에서 지터와 비트레이트를 파싱하는 함수
    @staticmethod
    def parse_iperf3_output(output):
        total_bitrate = 0.0
        total_jitter = 0.0
        count = 0

        regex = re.compile(r'\[\s*\d+\]\s*\d+\.\d+-\d+\.\d+\s+sec\s+(\d+\.?\d*)\s+MBytes\s+(\d+\.?\d*)\s+Mbits/sec\s+(\d+\.?\d*)\s+ms')

        for line in output.split('\n'):
            match = regex.search(line)
            if match:
                count += 1
                total_bitrate += float(match.group(2))
                total_jitter += float(match.group(3))

        if count == 0:
            return None

        average_bitrate = total_bitrate / count
        average_jitter = total_jitter / count

        return round(average_bitrate, 3), round(average_jitter, 3)  # 소수점 3자리까지 반올림

    # iperf3를 실행하고 결과를 파일에 저장하는 코드
    def run_and_log(self, bandwidth, duration, log_filename):
        # 결과를 로그 파일에 저장
        with open(log_filename, 'w') as f:
            while True:
                # iperf3 실행 결과 가져오기
                output = self.run_iperf3(bandwidth, duration)
                if output:
                    # 타임스탬프 생성
                    timestamp = datetime.now()

                    parsed_data = self.parse_iperf3_output(output)
                    if parsed_data:
                        average_bitrate, average_jitter = parsed_data
                        timestamp_str = timestamp.strftime('%Y%m%d%H%M%S')  # 새로운 타임스탬프 생성
                        log_line = f"Bitrate: {average_bitrate:.3f} Mbits/sec, Jitter: {average_jitter:.3f} ms, Timestamp: {timestamp_str}\n"
                        f.write(log_line)
                        print(log_line.strip())  # 터미널에 출력

# 서버 IP 주소와 포트 번호 리스트
servers = [
    ('192.168.0.20', 5201)
]

# Bandwidth 및 Duration 설정
bandwidth = '100M'
duration = 1

for server_ip, port in servers:
    # 로그 파일 이름에 추가할 문자열 생성
    timestamp_str = datetime.now().strftime('%Y%m%d%H%M%S')
    log_filename = f"parsed_output_{server_ip}_{port}_{timestamp_str}.log"

    # IperfRunner 인스턴스 생성
    iperf_runner = IperfRunner(server_ip, port)
    # 실행 및 로그
    iperf_runner.run_and_log(bandwidth, duration, log_filename)
