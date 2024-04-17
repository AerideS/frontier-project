import Jetson.GPIO as GPIO
import time

class MotorController:
    '''
        [요구사항]
        1. 시계방향, 반시계방향으로 모터의 방향제어와 속도 제어가 가능해야 한다.
        2. 드론과 나무 사이 거리에 따라 적정 평균 속도를 정해야 한다.
        3. 라이다를 통해 얻은 거리값과 평균 속도를 가지고 모터를 작동시켜야 하는 시간을 계산해야 한다.
        4. 모터 작동 시간 동안 평균 속도 기준으로 점점 빨라지다가 느려지게 제어해야 한다.

        [메모]
            서보모터 PWM 주기 : 50Hz(=200ms)
            duty cycle 7.5%일 때 정지상태
            duty cycle 5~7.5% : 시계방향 (5%일 때 high 신호가 1ms)
            duty cycle 7.5~10% : 반시계방향 (10%일 때 high 신호가 2ms)
    '''

    def __init__(self, distance, PWM_pin=33, period=50) -> None:
        self.PWM_pin = PWM_pin
        self.distance = distance

        #GPIO 채널 설정
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(PWM_pin, GPIO.OUT)

        #pwm 객체 생성
        self.pwm = GPIO.PWM(PWM_pin, period)
    
    def set_avg_speed(self):
        
        pass

    def set_rotate_time(self):
        
        pass

    def rotate_cw(self, duty_cycle_percent=5):
        self.pwm.start(duty_cycle_percent)    
        time.sleep(1)

    def rotate_ccw(self, duty_cycle_percent=10):
        self.pwm.ChangeDutyCycle(duty_cycle_percent)
        time.sleep(1)

    def stop(self):
        self.pwm.stop()
        GPIO.cleanup()


if __name__ == '__main__':
     # 테스트 수행
    TEST = 1
    if TEST == 1:
        motor=MotorController(12, 33, 50)
        motor.rotate_cw(6.5)
        motor.rotate_ccw(8.5)
        motor.stop()
    else:
        pass