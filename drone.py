import mqapi
import argparse
from networkChecker import networkChecker
from multiprocessing import Process
import asyncio
from vehicle import Vehicle
# from yoloModule import * 
from vehicle_stub import *
from datetime import datetime
from hardware import * # todo : 각 하드웨어에 대해 별도로 import 하지 않고 하나로 합칠수도 있을 듯
from math import tan

# 각 모드의 code 정의
NORMAL_MODE = 1
SEEK_MODE = 2
DROP_MODE = 3
RETURN_MODE = 4

PING_PERIOD = 5
DRONE_ADDRESS = 'udp://:14540'

class DroneMode:
    '''
    드론 동작을 위한 모드의 상위 클래스
    공통적으로 드론의 비행을 위한 동작 수행
    GCS의 명령을 rabbitmq로 수신
    arm, 이륙, 이동, 고도변경, 착륙의 동작을 수행함
    todo : 비행 종료 후 동작 정의 필요
    '''
    
    def __init__(self, parent) -> None:

        # drone
        self.parent = parent 
        
        # rabbitmq message receiver
        self.receiver = mqapi.MqReceiverAsync(parent.drone_name, parent.server_ip)
        
        # rabbitmq message sender
        self.sender = mqapi.MqSenderAsync(parent.server_ip)
        
        # mavsdk Drone actuator
        self.vehicle = Vehicle(DRONE_ADDRESS)
        # self.vehicle = Vehicle_Stub(DRONE_ADDRESS)
        
        # ping to server - network checker
        self.networkChecker = networkChecker(parent.server_ip, PING_PERIOD)     
        
        # 현재 모드가 수행할 함수, task의 목록 및 생성된 task의 목록
        self.task_list = []
        self.created_task_list = []
        
        # 네트워크 단절에 따른 네트워크 복귀를 위한 드론 이동 경로 
        self.route_record = []
        
        # 모드 변경을 위해 기존에 동작중인 task를 중지하기 위함, 실제로 동작하는 지는 확인 필요
        self.task_halt = False
        
        # start -> start_task를 통해 각 task가 실행될 때, start_task를 저장함
        self.cur_start = None
        
        #현재 모드에서 실행될 task를 목록에 추가함
        self.initTask()
        
    def initTask(self):
                
        self.task_list.clear()        
        self.task_list.append(self.processMessage()) # 메세지 수신 및 드론 동작
        # self.task_list.append(self.checkNetwork())   # 네트워크 연결 확인
        # self.task_list.append(self.updateStatus())    # 기체의 상태 받아옴
   
    async def processMessage(self):
        '''
        receiver에서 메세지를 받아 해석 후 명령 수행
        '''
        print('waiting for message')
        
        async for single_message in self.receiver.getMessage():
            
            # print(single_message)       
            if "type" not in single_message:
                print("not defined message")
                continue
            # print(76)
            cond = asyncio.Condition()
            await cond.acquire()
            
            if single_message["type"] == 'arm':
                await self.vehicle.arm()
            elif single_message["type"] == 'takeoff':
                await self.vehicle.takeoff()
            elif single_message["type"] == 'goto':
                await self.vehicle.goto(single_message['latitude'], single_message['longitude'])
            elif single_message["type"] == 'setElev':
                await self.vehicle.setElev(single_message['altitude'])
            elif single_message["type"] == 'wait':
                await self.vehicle.wait(single_message['time'])
            elif single_message["type"] == 'land':
                await self.vehicle.land()
            elif single_message["type"] == 'disarm':
                #disarm은 아마 착륙하면 자동으로 될것
                pass
            elif single_message["type"] == 'startDrop':
                await self.changeMode(SEEK_MODE)
            else:
                print("undefinded message")
                
            # print(95)
            if self.task_halt:
                print("break message")
                break
            await cond.release()
            
        # print(100) 
     
    async def updateStatus(self):
        '''
        기체의 상태 받아오기, 현재의 상태 저장과, 상태 전송에 사용됨
        '''
        async for velocity, battery, position in self.vehicle.getLocation():
            print(78)
            print(velocity, battery, position, sep='\n')
            print(80)
            if self.task_halt:
                break
            print(83)
            self.recordRoute(position)
            print(85)
            await self.sendStatus(velocity, battery, position)
            print(87)
            
    def recordRoute(self, position):
        '''
        드론의 현재 이동 위치를 저장
        '''
        
        single_data = {
            "time" : datetime.now().timestamp(),
            "latitude_deg" : position.latitude_deg,
            "longitude_deg" : position.longitude_deg,
            "absolute_altitude_m" : position.absolute_altitude_m,
            "relative_altitude_m" : position.relative_altitude_m
        }
        
        self.route_record.append(single_data)
    
    async def sendStatus(self, velocity, battery, position):
        '''
        드론의 현재 상태를 서버로 전송
        현재 시간, 장치명, 위치, 속도, 배터리 정보에 관한 정보 전송
        '''
        data =  {
            "time" : datetime.now().timestamp(),
            "device" : self.parent.drone_name,
            "position" : {
                "latitude_deg" : position.latitude_deg,
                "longitude_deg" : position.longitude_deg,
                "absolute_altitude_m" : position.absolute_altitude_m,
                "relative_altitude_m" : position.relative_altitude_m
            },
            "velocity" : {
                "north_m_s" : velocity.north_m_s,
                "east_m_s" : velocity.east_m_s,
                "down_m_s" : velocity.down_m_s
            },
            "battery" : {
                "voltage_v" : battery.voltage_v,
                "current_battery_a" : battery.current_battery_a,
                "remaining_percent" : battery.remaining_percent
            }
        }
        await self.sender.send_message(data, "SERVER")
        
    async def checkNetwork(self):
        '''
        서버로 보낸 ping이 돌아오는지 확인
        todo
        현재가 return mode가 아닐경우
            네트워크 연결이 확인됨 : 정상 동작
            네트워크 연결이 확인되지 않음 : 현재 task를 종료하고 return mode로,
            
        현재가 return mode일 경우
            네트워크 연결이 확인됨 : 현재 task를 종료하고 기존 실행 모드로 
            네트워크 연결이 확인되지 않음 : 현재 task 지속 수행
        '''
        async for response in self.networkChecker.ping():
            # print(response)
            if self.task_halt:
                break
            
            if self.parent.mode == "RETURN_MODE":
                if response == True:
                    self.changeMode(self.prev_mode)
            else:
                if response == False:
                    self.changeMode(RETURN_MODE)
          
    async def changeMode(self, new_mode):
        '''
        모드 변경
        기존 수행중인 task를 종료하고 새로운 객체 생성 후 실행
        '''
        # print('all task : ', end =' ')
        # print(task for task in asyncio.all_tasks())
        for single_task in self.created_task_list:
            self.task_halt = True
            single_task.cancel()
            # print(57, single_task)
                
        # print('all task : ', end =' ')
        # print(task for task in asyncio.all_tasks())
    
        if new_mode == NORMAL_MODE:
            self.parent.mode = NormalMode(self.parent)
        elif new_mode == DROP_MODE:
            self.parent.mode = DropMode(self.parent)
        elif new_mode == SEEK_MODE:
            self.parent.mode = SeekMode(self.parent)
        elif new_mode == RETURN_MODE:
            self.parent.mode = ReturnMode(self.parent, self.parent.mode)
        else:
            # print("Mode error")
            self.parent.mode = NormalMode(self.parent)
            
        # self.cur_start = asyncio.create_task()
        # # print(154, 'cur start', type(self.cur_start))
        # await asyncio.wait([self.cur_start])
        await self.parent.mode.start_task()       
               
    async def start_task(self):
        '''
        todo : 착륙시, 미션 종료시 아래의 loop 탈출 필요
        주요 기능 동작을 위함
        현재 mode에 맞는 task를 생성하고 실행
        '''
        while True:
            self.initTask()
            self.created_task_list.clear()
            # print(self.created_task_list)
            # print(111, self.parent.mode)
            # print(147, self.task_list)
            # print('all task : ', end =' ')
            # print(task for task in asyncio.all_tasks())
            self.task_halt = False
            # print(self.task_list)
            
            # loop = asyncio.get_running_loop()        
            
            # print(i for i in asyncio.all_tasks(loop=loop))
            # print(self.task_list)
            # print(self.created_task_list)
            for single_task in self.task_list:
                print(148, single_task)
                try:
                    single_created_task = asyncio.create_task(single_task)
                    print(170, type(single_created_task))
                    self.created_task_list.append(single_created_task)
                    
                except ValueError as val_e:
                    print(val_e)
            try:
                await asyncio.wait(self.created_task_list)
            except KeyboardInterrupt:
                await self.stop_task()
            # print(self.created_task_list)
            # print(158)
            # print('all task : ', end =' ')
            # print(task for task in asyncio.all_tasks())
        
    
    def start(self):
        '''
        start_task를 위한 동작 
        '''
        try:
            # asyncio.get_event_loop().run_until_complete(self.start_task())
            asyncio.run(self.start_task())
        except ValueError as val_e:
            # 현재 실행중인 함수 목록이 없을 경우 처리
            print(val_e)
        
    async def stop_task(self):
        '''
        mode 변환 등을 위해 수행중인 task를 종료함
        사용되지 않음
        '''
        # print(129)
        for single_task in self.created_task_list:
            single_task.cancel()
            
            try:
                await single_task
            except asyncio.CancelledError:
                print("task canceled")

    def stop(self):
        '''
        mode 변환 등을 위해 수행중인 task를 종료함
        사용되지 않음
        '''
        # print(135)
        self.task_halt = True
        for single_task in self.created_task_list:
            # print(150)
            single_task.cancel()
        loop = asyncio.get_running_loop()        
        
        # print(i for i in asyncio.all_tasks(loop=loop))
        
        # print(140)  
    
    
class NormalMode(DroneMode):
    '''
    일반 모드, 드론이 이동하는 기능만 있으므로 별도 구현은 하지 않음
    '''
    def __init__(self, parent) -> None:
        super().__init__(parent)
    
    def __str__(self) -> str:
        return 'NORMAL_MODE'
     
    async def start(self):
        await super().start_task()
    
    async def stop(self):
        super().stop()


class SeekMode(DroneMode):
    '''
    수목 탐색 모드, 카메라 사용 및 yolo 모듈 동작
    드론 이동시 위도, 경도 기반이 아닌 위치 기반 이동 고려중
    
    1. 이미지를 받는다
        카메라 센서 -> 드론 하부 촬영 이미지
    2. 이미지에서 수목 위치를 추출한다
        드론 촬영 이미지 -> 수목 위치까지의 가로, 세로 픽셀 (가로, 세로)
        픽셀이 없을 경우 -> 주변 탐색 : todo
    3. 픽셀을 미터로 변환한다
        수목 위치까지의 가로, 세로 픽셀 -> 해당 지점까지의 거리
    '''
    def __init__(self, parent) -> None:
        super().__init__(parent)
        
        # self.yolo_module = FindTree()
        self.cam_module = RaspiCAM__STUB() # 카메라 모듈 스텁
        self.yolo_module = FindTree__STUB() # yolov5 모듈 스텁
        self.lidar_module = LidarModule__STUB() # 라이다 모듈 스텁
                
        self.task_list.append(self.yoloModule())
        
        self.CAM_ANGLE = 63/2 # 라즈베리파이 캠의 화각
        self.CAM_WIDTH_PIXEL = 640
        self.CAM_HEIGHT_PIXEL = 480
    
    def __str__(self) -> str:
        return 'SEEK_MODE'
    
    async def yoloModule(self):
        '''
        1. 사진 받는다
        2. 객체 확인한다
        3. 이동한다
        4. 모드 변경한다
        '''
        while True: # 카운트 세다가 없으면 넘어가기?
            this_pic = self.cam_module.getPicture() # 사진 받아옴
            process_result = self.yolo_module.find_tree_coordinate(this_pic)
            if process_result is None:
                pass # 결과가 없을 경우 이동하고 다시
            else:
                x_dis, y_dis = process_result
                await self.vehicle.move_meters(x_dis, y_dis)
                self.changeMode(DROP_MODE)
                break
            
            await asyncio.sleep(3)
        
    async def start(self):
        await super().start_task()
    
    async def stop(self):
        super().stop()
        
    def convertPixelToMeters(self, pixel_width_dis, pixel_height_dis, lidar_dis):
        '''
        pixel_width_dis     : 픽셀 가로 길이
        pixel_height_dis    : 픽셀 세로 길이
        lidar_dis           : 라이다 측정 수목간 차이
        '''
        
        absolute_whole_width = 2* lidar_dis * math.tan(self.CAM_ANGLE)
        
        conversion_factor = absolute_whole_width / self.CAM_WIDTH_PIXEL
        
        x_dist = conversion_factor * pixel_width_dis
        y_dist = conversion_factor * pixel_height_dis
        
        return (x_dist, y_dist)

class DropMode(DroneMode):
    '''
    수목 탐색 후 중계기 투하
    현재 지점의 위치 입력받아 중계기 마운트 동작
    '''
    def __init__(self, parent) -> None:
        super().__init__(parent)
        
        self.dropper = Dropper__STUB()
        self.lidar_module = LidarModule()

    async def start(self):
        await super().start_task()
    
    async def stop(self):
        super().stop()
        
    def __str__(self) -> str:
        return 'DROP_MODE'
    
    async def dropRepeater(self):
        '''
        todo : 지금 위치를 전달받아야 할까?
        '''
        
        height = await self.lidar_module.getAltidude()
        
        await self.dropper.drop(height)
        
        self.changeMode(NORMAL_MODE)
 
 
class ReturnMode(DroneMode):
    '''
    운용중 네트워크 단절에 따른 복귀모드
    이전의 위치 기록을 전달받아 해당 기록을 따라 이동
    '''
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.prev_mode = None
        
        self.task_list.append(self.traceBack)()
        
        
    async def traceBack(self):
        '''
        이동 기록을 따라 이전 지점으로 이동해 나가는 것
        네트워크 복귀할때 까지
        '''
        # todo 네트워크 복귀 후 지점 전송
        for single_point in self.route_record:
            lat, lon, alt = single_point
            self.vehicle.goto(lat, lon, alt)
            
        # loop 문 탈출한 경우에는 집 못찾은 것이므로 안전 고도로 상승하여
        # GCS 위치로 복귀함

    async def start(self):
        await super().start_task()
    
    async def stop(self):
        super().stop()
        
    def __str__(self) -> str:
        return 'RETURN_MODE'

class Drone:
    def __init__(self, drone_name, server_ip) -> None:
        self.drone_name = drone_name
        self.server_ip = server_ip
        
        # print(drone_name, server_ip)
        
        self.mode = NormalMode(self) # 초기 모듈
        
    async def start(self):
        await self.mode.start()
        
    async def stop(self):
        await self.mode.stop()
        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='드론 작동을 위한 기본 정보')
    parser.add_argument('-name', help=' : 현재 드론의 이름')
    parser.add_argument('-server', help=' : 서버 주소')
    args = parser.parse_args()  
    
    async def main():
        drone = Drone(args.name, args.server)
        await drone.start()
        
    asyncio.run(main())
    
    