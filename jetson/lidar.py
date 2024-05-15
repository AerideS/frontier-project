import serial
import Jetson.GPIO as GPIO
import time

# UART 포트 설정
serial_port = '/dev/ttyTHS1'
# serial_port = '/dev/ttyS0'
baud_rate = 115200

# GPIO 핀 설정
TX_pin = 33  # GPIO 핀 번호 설정
RX_pin = 19 # GPIO 핀 번호 설정

HEADER = 89
DATA_LENGTH = 9

# UART 초기화
uart = serial.Serial(serial_port, baud_rate, timeout=1)
buf = [_ for _ in range(9)]
try:
    # GPIO 초기화
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(TX_pin, GPIO.OUT)
    GPIO.setup(RX_pin, GPIO.IN)
    
    while True:
        # 시리얼 포트로부터 읽기
        data = uart.read()
        if data:
            if int(data[0]) == HEADER:
                buf[0] = HEADER
                if int(uart.read()[0]) == HEADER:
                    buf[1] = HEADER

                    for i in range(2, 9):
                        buf[i] = int(uart.read()[0])

                    check = sum(buf[:8])
                    if buf[8] == (check & 255):
                        # 거리 및 신호 강도 계산
                        dist = buf[2] + buf[3] * 256
                        strength = buf[4] + buf[5] * 256
                        
                        # 거리 및 신호 강도 출력
                        print("dist =", dist, "\t strength =", strength)
                
except Exception as e:
    print("Error:", str(e))

finally:
    # 리소스 해제
    uart.close()
    GPIO.cleanup()
