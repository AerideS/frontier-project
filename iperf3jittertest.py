import subprocess
import time
import logging
import os

class Iperf3UDPClient:
    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.log_file = None
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # 로그 파일 이름 생성
        current_time = time.strftime('%Y-%m-%d_%H-%M-%S')
        log_filename = f"iperf3_{self.server_ip}_{current_time}.log"

        # 로그 파일 핸들러 설정
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        self.log_file = log_filename
        return logger

    def run_test(self):
        while True:
            cmd = f"iperf3 -c {self.server_ip} -u"
            self.logger.info("Starting iperf3 UDP test...")
            self.logger.info("Command: %s", cmd)

            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # 테스트가 시작되면 로그를 저장
            with open(self.log_file, 'a') as log:
                log.write(f"Iperf3 UDP Test Started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

            while True:
                output = process.stdout.readline().strip()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.logger.info(output)

            # 테스트가 종료되면 로그를 저장
            with open(self.log_file, 'a') as log:
                log.write(f"Iperf3 UDP Test Ended at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

            self.logger.info("Iperf3 UDP test completed.")
            time.sleep(1)  # 테스트 간 간격을 설정하여 지나치게 자주 테스트를 실행하지 않도록 합니다.

if __name__ == "__main__":
    server_ip = "192.168.0.20"
    client = Iperf3UDPClient(server_ip)
    client.run_test()
