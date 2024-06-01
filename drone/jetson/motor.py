import Jetson.GPIO as GPIO
import time
import math

'''
todo : 사실 메인 함수 이거 하나만 있으면 된다...
input : 중계기 투하 높이
output : 서모보터로의 pwm 신호 내보냄

'''

class ReelModule:
    '''
        [요구사항]
        1. 시계방향, 반시계방향으로 모터의 방향제어와 속도 제어가 가능해야 한다.
        2. 드론과 나무 사이 거리에 따라 적정 평균 속도를 정해야 한다.
        3. 라이다를 통해 얻은 거리값과 평균 속도를 가지고 모터를 작동시켜야 하는 시간을 계산해야 한다.
        4. 모터 작동 시간 동안 평균 속도 기준으로 점점 빨라지다가 느려지게 제어해야 한다.

        [메모]
            서보모터 PWM 주기 : 50Hz(=200ms)
            duty cycle 2.5~7.5% : 시계방향 (5%일 때 high 신호가 1ms)
            duty cycle 7.5%일 때 정지상태
            duty cycle 7.5~12.5% : 반시계방향 (10%일 때 high 신호가 2ms)

            duty cycle percent  |  RPM(-는 반시계 방향 의미함)
                    2.5             52.8
                    3.5             52.8
                    4.5             52.8
                    5.5             47.5
                    6.5             32.4
                    7.5             0
                    8.5             -38.2
                    9.5             -46.8
                    10.5            -52.8
                    11.5            -52.8
                    12.5            -52.8

            측정 결과, 2.5~4.5 구간과 10.5~12.5 구간은 회전 속도의 차이가 없다.

            풀리 지름 : 24.18 mm
            기어비 : 2.667

        [메서드]
        1. __intit__(self, PWM_pin1=33, PWM_pin2=32, period=50) : 초기 설정
        2. ascent_repeater(self, duty_cycle_percent, distance) : 시계방향 회전
        3. descent_repeater(self, duty_cycle_percent, distance) : 반시계 방향 회전
        4. cal_time(self, distance, rpm=52.8) : 거리에 따른 회전 시간 계산
        5. stop(self) : 모터 작동 중지
    '''

    def __init__(self, PWM_pin1=33, PWM_pin2=32, period=50) -> None:
        self.diameter = 24.18  # 풀리 지름
        self.rpm = 52.8 * 2.667  # 풀리 rpm = 모터 rpm * 기어비 # 무부하인 경우 모터 rpm
        self.PWM_pin1 = PWM_pin1
        self.PWM_pin2 = PWM_pin2
        self.hold_dutyCyclePercent = 5
        self.release_dutyCyclePercent = 7.5
        
        #GPIO 채널 설정
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(PWM_pin1, GPIO.OUT)
        GPIO.setup(PWM_pin2, GPIO.OUT)

        #pwm 객체 생성
        self.servo1_pwm = GPIO.PWM(PWM_pin1, period)
        self.servo2_pwm = GPIO.PWM(PWM_pin2, period)

        self.servo1_pwm.start(7.5)
        self.servo2_pwm.start(self.hold_dutyCyclePercent)
        time.sleep(0.3)

    # 모터는 시계, 풀리는 반시계로 돈다.
    def ascent_repeater(self, distance, duty_cycle_percent=2.5):
        distance = distance/100
        if duty_cycle_percent >= 2.5 and duty_cycle_percent < 7.5:
            self.rpm = 45.0 * 2.667  #중계기 무게 고려한 상승시 모터 rpm
            # 풀리 끝 선속도 계산
            angular_speed = self.rpm * (2*math.pi)/60
            self.linear_speed = self.diameter/2 * angular_speed *0.001 # 단위 : m/s

            # 회전 시간 계산
            rotate_time = distance / self.linear_speed
            print('걸리는 시간 : ', rotate_time)

            # #회전 시간 계산
            # rotate_time = self.cal_time(distance)

            #잠금해제 및 회전
            self.servo2_pwm.ChangeDutyCycle(self.release_dutyCyclePercent)
            time.sleep(0.3)
            self.servo1_pwm.ChangeDutyCycle(duty_cycle_percent)
            time.sleep(rotate_time)
            self.servo1_pwm.ChangeDutyCycle(7.5)
            #잠금
            time.sleep(0.3)
            self.servo2_pwm.ChangeDutyCycle(self.hold_dutyCyclePercent)
            time.sleep(0.3)
            self.servo2_pwm.ChangeDutyCycle(self.release_dutyCyclePercent)
            time.sleep(0.3)
            self.servo2_pwm.ChangeDutyCycle(self.hold_dutyCyclePercent)
            time.sleep(0.3)

        else:
            print('시계방향 회전을 위한 올바른 pwm값이 아님')

    # 모터는 반시계, 풀리는 시계로 돈다.
    def descent_repeater(self, distance, duty_cycle_percent=12.5):
        distance = distance/100
        if duty_cycle_percent > 7.5 and duty_cycle_percent <= 12.5:
            self.rpm = 64 * 2.667  #중계기 무게 고려한 하강시 모터 rpm
            # 풀리 끝 선속도 계산
            angular_speed = self.rpm * (2*math.pi)/60
            self.linear_speed = self.diameter/2 * angular_speed *0.001 # 단위 : m/s

            # 회전 시간 계산
            rotate_time = distance / self.linear_speed
            print('걸리는 시간 : ', rotate_time)

            # #회전 시간 계산
            # rotate_time = self.cal_time(distance)

            #잠금해제 및 회전
            self.servo2_pwm.ChangeDutyCycle(self.release_dutyCyclePercent)
            self.servo1_pwm.ChangeDutyCycle(duty_cycle_percent)
            time.sleep(rotate_time)
            self.servo1_pwm.ChangeDutyCycle(7.5)
            #잠금
            time.sleep(0.3)
            self.servo2_pwm.ChangeDutyCycle(self.hold_dutyCyclePercent)
            time.sleep(0.3)
            self.servo2_pwm.ChangeDutyCycle(self.release_dutyCyclePercent)
            time.sleep(0.3)
            self.servo2_pwm.ChangeDutyCycle(self.hold_dutyCyclePercent)
            time.sleep(0.3)
        else:
            print('반시계방향 회전을 위한 올바른 pwm값이 아님')

    # def cal_time(self, distance):
    #     # 풀리 끝 선속도 계산
    #     angular_speed = self.rpm * (2*math.pi)/60
    #     self.linear_speed = self.diameter/2 * angular_speed *0.001 # 단위 : m/s

    #     # 회전 시간 계산
    #     rotate_time = distance / self.linear_speed
        
    #     print('걸리는 시간 : ', rotate_time)
        
    #     return rotate_time

    def stop(self):
        self.servo1_pwm.stop()
        GPIO.cleanup()


if __name__ == '__main__':
     # 테스트 수행
    TEST = 1
    if TEST == 1:
        reel_module=ReelModule()
        # time.sleep(3)
        reel_module.descent_repeater(5)
        reel_module.ascent_repeater(5)
        reel_module.stop()
    else:
        pass
