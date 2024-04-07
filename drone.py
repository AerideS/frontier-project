import mqapi
import argparse
from networkChecker import networkChecker
from multiprocessing import Process

class DroneMode:
    '''
    드론 동작을 위한 모드의 상위 클래스
    공통적으로 드론의 비행을 위한 동작 수행
    GCS의 명령을 rabbitmq로 수신
    arm, 이륙, 이동, 고도변경, 착륙의 동작을 수행함
    '''
    
    def __init__(self) -> None:
        pass    
    

class NormalMode(DroneMode):
    '''
    일반 모드, 드론이 이동하는 기능만 있으므로 별도 구현은 하지 않음
    '''
    def __init__(self) -> None:
        super().__init__()
        
    def start():
        pass
    
    def stop():
        pass

class SeekMode(DroneMode):
    '''
    수목 탐색 모드, 카메라 사용 및 yolo 모듈 동작
    드론 이동시 위도, 경도 기반이 아닌 위치 기반 이동 고려중
    '''
    def __init__(self) -> None:
        super().__init__()
        
    def start():
        pass
    
    def stop():
        pass

class DropMode(DroneMode):
    '''
    수목 탐색 후 중계기 투하
    현재 지점의 위치 입력받아 중계기 마운트 동작
    '''
    def __init__(self) -> None:
        super().__init__()

    def start():
        pass
    
    def stop():
        pass
 
class ReturnMode(DroneMode):
    '''
    운용중 네트워크 단절에 따른 복귀모드
    이전의 위치 기록을 전달받아 해당 기록을 따라 이동
    '''
    def __init__(self) -> None:
        super().__init__()

    def start():
        pass
    
    def stop():
        pass

class Drone:
    def __init__(self, drone_name, server_ip) -> None:
        self.drone_name = drone_name
        self.server_ip = server_ip
        
        self.receiver = mqapi.MqReceiver(drone_name, server_ip)
        
        self.vehicle = None # todo.. 모듈 연결 필요
        
        self.networkChecker = networkChecker() # todo.. 모듈 연결 필요
        
        self.mode = NormalMode()        
        
    def start(self):
        while True: 
            single_message = self.receiver.getOneMessage()
            print(single_message)       

            if single_message['']
        
        
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='드론 작동을 위한 기본 정보')
    parser.add_argument('--name', help=' : 현재 드론의 이름')
    parser.add_argument('--server', help=' : 서버 주소')
    args = parser.parse_args()  
    print(args.name, args.server)
    drone = Drone(args.name, args.server)
    drone.start()