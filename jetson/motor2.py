import Jetson.GPIO as GPIO
import time
import math

'''
todo : 사실 메인 함수 이거 하나만 있으면 된다...
input : 중계기 투하 높이
output : 서모보터로의 pwm 신호 내보냄

'''

class MotorController:
    '''
        [요구사항]
        1. 시계방향, 반시계방향으로 모터의 방향제어와 속도 제어가 가능해야 한다.
        2. 드론과 나무 사이 거리에 따라 적정 평균 속도를 정해야 한다.
        3. 라이다를 통해 얻은 거리값과 평균 속도를 가지고 모터를 작동시켜야 하는 시간을 계산해야 한다.
        4. 모터 작동 시간 동안 평균 속도 기준으로 점점 빨라지다가 느려지게 제어해야 한다.

        [메모]
            서보모터 PWM 주기 : 50Hz(=200ms)
            duty cycle 3~7.5% : 시계방향 (5%일 때 high 신호가 1ms)
            duty cycle 7.5%일 때 정지상태
            duty cycle 7.5~12% : 반시계방향 (10%일 때 high 신호가 2ms)

            duty cycle percent | RPM(-는 반시계 방향 의미함)
                    3           100.1
                    4           95.8
                    5           82.3
                    6           64.5
                    7           22.9
                    7.5         0
                    8           -22.4
                    9           -67.5
                    10          -92.4
                    11          -103.4
                    12          -109.9
    '''

    def __init__(self, PWM_pin=33, period=50) -> None:
        self.PWM_pin = PWM_pin
        self.diameter = 22 #풀리 지름
        self.speed = 0 #풀리 선속도

        #GPIO 채널 설정
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(PWM_pin, GPIO.OUT)

        #pwm 객체 생성
        self.pwm = GPIO.PWM(PWM_pin, period)

        self.pwm.start(0)
    
    def cal_speed(self, duty_cycle_percent):
        if duty_cycle_percent == 3:
            # RPM을 라디안/초로 변환
            angular_speed = 100 * 2 * math.pi / 60  # 1분에 2π 라디안이 1회전
            # 선속도 계산
            self.speed = self.diameter/2 * angular_speed #단위 : mm/2
            self.speed = self.speed/1000 #단위 : m/s
        else:
            # RPM을 라디안/초로 변환
            angular_speed = 103.4 * 2 * math.pi / 60  # 1분에 2π 라디안이 1회전
            # 선속도 계산
            self.speed = self.diameter/2 * angular_speed #단위 : mm/2
            self.speed = self.speed/1000 #단위 : m/s

    def cal_time(self, distance):
        rotate_time = distance / self.speed
        print('걸리는 시간 : ', rotate_time)
        return rotate_time

    def rotate_cw(self, distance, duty_cycle_percent):
        self.cal_speed(duty_cycle_percent)
        rotate_time = self.cal_time(distance)
        self.pwm.ChangeDutyCycle(duty_cycle_percent)
        time.sleep(rotate_time)

    def rotate_ccw(self, distance, duty_cycle_percent):
        self.cal_speed(duty_cycle_percent)
        rotate_time = self.cal_time(distance)
        self.pwm.ChangeDutyCycle(duty_cycle_percent)
        time.sleep(rotate_time)

    def stop(self):
        self.pwm.stop()
        GPIO.cleanup()


if __name__ == '__main__':
     # 테스트 수행
    TEST = 1
    if TEST == 1:
        motor=MotorController(33, 50)
        motor.rotate_cw(1, 3)
        motor.rotate_ccw(1, 11)
        motor.stop()
    else:
        pass