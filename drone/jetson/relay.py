import Jetson.GPIO as GPIO
import time

class RelayModule:
    def __init__(self) -> None:
        self.relay_pin = 16

        # GPIO 설정
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.relay_pin, GPIO.OUT)

    def cut_string(self):
        try:
            GPIO.output(self.relay_pin, GPIO.HIGH)
            print("5초간 릴레이 켬")
            time.sleep(5)
            GPIO.output(self.relay_pin, GPIO.LOW)
            print("릴레이 끔")
        finally:
            GPIO.cleanup()
        

if __name__ == '__main__':
     # 테스트 수행
    TEST = 1
    if TEST == 1:
        relay_module = RelayModule()
        relay_module.cut_string()
    else:
        pass
