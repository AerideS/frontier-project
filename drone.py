import mqapi
import argparse
from networkChecker import networkChecker
from multiprocessing import Process
from dropper import *
import asyncio
from vehicle import Vehicle

from vehicle_stub import *

PING_PERIOD = 5
DRONE_ADDRESS = 'udp://:14540'

class DroneMode:
    '''
    드론 동작을 위한 모드의 상위 클래스
    공통적으로 드론의 비행을 위한 동작 수행
    GCS의 명령을 rabbitmq로 수신
    arm, 이륙, 이동, 고도변경, 착륙의 동작을 수행함
    '''
    
    def __init__(self, parent) -> None:
        '''
        todo : 실행 주체에 따라 객체를 parent에 할당할지, self에 할당할지 결정 필요
        '''
        self.parent = parent
        
        self.receiver = mqapi.MqReceiverAsync(parent.drone_name, parent.server_ip)
        
        self.vehicle = Vehicle(DRONE_ADDRESS) # todo.. 모듈 연결 필요\
        # self.vehicle = Vehicle_Stub(DRONE_ADDRESS)
        
        self.networkChecker = networkChecker(parent.server_ip, PING_PERIOD)     
        
        self.task_list = []
        self.created_task_list = []
        
        self.task_list.append(self.processMessage())
        self.task_list.append(self.checkNetwork())        
        
    
    async def processMessage(self):
        '''
        receiver에서 메세지를 받아 해석 후 명령 수행
        '''
        print('waiting for message')
        async for single_message in self.receiver.getMessage():
            print(single_message)       
            print(type(single_message))
            if "type" not in single_message:
                print("not defined message")
                continue
                
            if single_message["type"] == 'takeoff':
                await self.vehicle.takeoff()
            elif single_message["type"] == 'goto':
                await self.vehicle.goto(single_message['latitude'], single_message['longitude'])
            elif single_message["type"] == 'setElev':
                await self.vehicle.setElev(single_message['altitude'])
            elif single_message["type"] == 'wait':
                await self.vehicle.wait(single_message['time'])
            elif single_message["type"] == 'land':
                await self.vehicle.land(single_message['time'])
            elif single_message["type"] == 'disarm':
                #disarm은 아마 착륙하면 자동으로 될것
                pass
            elif single_message["type"] == 'startDrop':
                self.parent.changeMode("Drop")
                
    async def checkNetwork(self):
        '''
        서버로 보낸 ping이 돌아오는지 확인
        '''
        async for response in self.networkChecker.ping():
            print(response)
            
            
    async def start_task(self):
        self.created_task_list = []
        for single_task in self.task_list:
            self.created_task_list = asyncio.create_task(single_task)
        
        await asyncio.wait([self.created_task_list])
    
    def start(self):
        asyncio.run(self.start_task())
    
    def stop(self):
        for single_task in self.created_task_list:
            single_task.cancel()
                   
    
    
class NormalMode(DroneMode):
    '''
    일반 모드, 드론이 이동하는 기능만 있으므로 별도 구현은 하지 않음
    '''
    def __init__(self, parent) -> None:
        super().__init__(parent)
        
    def start(self):
        super().start()
    
    def stop(self):
        super().stop()

class SeekMode(DroneMode):
    '''
    수목 탐색 모드, 카메라 사용 및 yolo 모듈 동작
    드론 이동시 위도, 경도 기반이 아닌 위치 기반 이동 고려중
    '''
    def __init__(self, parent) -> None:
        super().__init__(parent)
        
        self.task_list.append(self.yoloModule())
    
    def yoloModule(self):
        pass
        
    def start(self):
        super().start()
    
    def stop(self):
        super().stop()

class DropMode(DroneMode):
    '''
    수목 탐색 후 중계기 투하
    현재 지점의 위치 입력받아 중계기 마운트 동작
    '''
    def __init__(self, parent) -> None:
        super().__init__(parent)
        
        self.dropper = Dropper()

    def start(self):
        pass
    
    def stop(self):
        pass
 
class ReturnMode(DroneMode):
    '''
    운용중 네트워크 단절에 따른 복귀모드
    이전의 위치 기록을 전달받아 해당 기록을 따라 이동
    '''
    def __init__(self, parent) -> None:
        super().__init__()

    def start(self):
        pass
    
    def stop(self):
        pass

class Drone:
    def __init__(self, drone_name, server_ip) -> None:
        self.drone_name = drone_name
        self.server_ip = server_ip
        
        self.mode = NormalMode(self) # 초기 모듈
        
    def changeMode(self, mode):
        '''
        모드 변경을 위함
        기존 동작중인 모드를 정지하고
        mode값에 해당하는 모드로 변경한 후
        해당 모드 실행
        '''
        self.mode.stop(self)
        
        if mode == "Normal":
            self.mode = NormalMode(self)
            
        elif mode == "Seek":
            self.mode = SeekMode(self)
        
        elif mode == "Drop":
            self.mode = DropMode(self)
            
        elif mode == "Return":
            self.mode = ReturnMode(self)
        else:
            '''
            mode 전달과정에서 오류 발생시 normal mode로
            변경
            '''
            self.mode = NormalMode(self)
            
        self.mode.start(self)
    
    def start(self):
        self.mode.start()
        
    def stop(self):
        self.mode.stop()
        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='드론 작동을 위한 기본 정보')
    parser.add_argument('-name', help=' : 현재 드론의 이름')
    parser.add_argument('-server', help=' : 서버 주소')
    args = parser.parse_args()  
    
    drone = Drone(args.name, args.server)
    drone.start()