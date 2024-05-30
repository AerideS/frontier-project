import serial
import Jetson.GPIO as GPIO
import time

class LidarModule:
    def __init__(self) -> None:
        # UART 포트 설정
        self.serial_port = '/dev/ttyTHS1'
        self.baud_rate = 115200
        self.HEADER = 89  # (89 = 0x59)
        self.DATA_LENGTH = 9
        # UART 초기화
        self.uart = serial.Serial(self.serial_port, self.baud_rate, timeout=1)

    def getAltitude(self):
        try:
            buf = [_ for _ in range(9)]
            while True:
                # 시리얼 포트로부터 읽기
                data = self.uart.read()
                if data:
                    if int(data[0]) == self.HEADER:
                        buf[0] = self.HEADER
                        if int(self.uart.read()[0]) == self.HEADER:
                            buf[1] = self.HEADER

                            for i in range(2, 9):
                                buf[i] = int(self.uart.read()[0])

                            check = sum(buf[:8])
                            if buf[8] == (check & 255):
                                # 거리 및 신호 강도 계산
                                dist = buf[2] + buf[3] * 256
                                strength = buf[4] + buf[5] * 256

                                # 거리 및 신호 강도 출력
                                print("dist =", dist, "\t strength =", strength)

                                return dist

        except Exception as e:
            print("Error:", str(e))

        finally:
            # 리소스 해제
            self.uart.close()

if __name__ == '__main__':
    lidar_module = LidarModule()
    distance = lidar_module.getAltitude()
    print(distance)