import Jetson.GPIO as GPIO
import time

# GPIO 핀 번호 설정
relay_pin = 12  # 이 부분은 사용하는 GPIO 핀 번호에 맞게 변경하세요.

# GPIO 설정
GPIO.setmode(GPIO.BOARD)
GPIO.setup(relay_pin, GPIO.OUT)

def cut_string()
        # 릴레이를 켬
        GPIO.output(relay_pin, GPIO.HIGH)
        print("릴레이 켬")
        time.sleep(10)
        GPIO.output(relay_pin, GPIO.LOW)
        print("릴레이 켬")
        

if __name__ == '__main__':
     # 테스트 수행
    TEST = 1
    if TEST == 1:
        cut_string()
    else:
        pass
