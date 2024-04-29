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
import tracemalloc

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import mqapi

# 각 모드의 code 정의
NORMAL_MODE = 1
SEEK_MODE = 2
DROP_MODE = 3
RETURN_MODE = 4

PING_PERIOD = 5
DRONE_ADDRESS = 'udp://:14540'

    
class NormalMode:
    '''
    일반 모드, 드론이 이동하는 기능만 있으므로 별도 구현은 하지 않음
    '''
    def __init__(self, parent) -> None:
        self.base_mode = parent
        self.task_list = []
        
        self.task_list.append(self.base_mode.processMessage()) # 메세지 수신 및 드론 동작
        
    def __str__(self) -> str:
        return 'NORMAL_MODE'

class SeekMode:
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
        self.base_mode = parent
        self.task_list = []
        
        # self.yolo_module = FindTree()
        self.cam_module = RaspiCAM__STUB() # 카메라 모듈 스텁
        self.yolo_module = FindTree__STUB() # yolov5 모듈 스텁
        self.lidar_module = LidarModule__STUB() # 라이다 모듈 스텁
                
        self.task_list.append(self.yoloModule())
        self.task_list.append(self.base_mode.processMessage()) # 메세지 수신 및 드론 동작
        
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
            print(366)
            this_pic = self.cam_module.getPicture() # 사진 받아옴
            print(368)
            process_result = await self.yolo_module.find_tree_coordinate(this_pic)
            print(370)
            if process_result is None:
                pass # 결과가 없을 경우 이동하고 다시 비행하는 과정 포함
                print(373)
            else:
                x_dis, y_dis = process_result
                print(376)
                await self.base_mode.vehicle.move_meters(x_dis, y_dis)
                print(378)
                await self.base_mode.changeMode(DROP_MODE)
                print(380)
                break
            
            await asyncio.sleep(3)
            
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

class DropMode:
    '''
    수목 탐색 후 중계기 투하
    현재 지점의 위치 입력받아 중계기 마운트 동작
    '''
    def __init__(self, parent) -> None:
        self.base_mode = parent
        self.task_list = []
            
        self.dropper = Dropper__STUB()
        self.lidar_module = LidarModule()
        
        self.task_list.append(self.dropRepeater())
        self.task_list.append(self.base_mode.processMessage()) # 메세지 수신 및 드론 동작

    def __str__(self) -> str:
        return 'DROP_MODE'
    
    async def dropRepeater(self):
        '''
        todo : 지금 위치를 전달받아야 할까?
        '''
        print("DROP REPEATER --------")
        height = await self.lidar_module.getAltidude()
        print("GOT HEIGHT  ----------")
        await self.dropper.drop(height)
        print("DROP COMPLETE --------")
        await self.base_mode.changeMode(NORMAL_MODE)
          
class ReturnMode:
    '''
    운용중 네트워크 단절에 따른 복귀모드
    이전의 위치 기록을 전달받아 해당 기록을 따라 이동
    '''
    def __init__(self, parent, prev_mode) -> None:
        self.base_mode = parent
        self.task_list = []
        self.prev_mode = prev_mode
        
        self.base_mode.route_record_set = False
        
        self.task_list.append(self.traceBack())
        
        
    async def traceBack(self):
        '''
        이동 기록을 따라 이전 지점으로 이동해 나가는 것
        네트워크 복귀할때 까지
        
        "time" : datetime.now().timestamp(),
        "latitude_deg" : position.latitude_deg,
        "longitude_deg" : position.longitude_deg,
        "absolute_altitude_m" : position.absolute_altitude_m,
        "relative_altitude_m" : position.relative_altitude_m
        '''
        # todo 네트워크 복귀 후 지점 전송
        for single_point in self.base_mode.route_record:
            lat = single_point["latitude_deg"]
            lon = single_point["longitude_deg"]
            alt = single_point["relative_altitude_m"]
            print("get back to...", lat, lon, alt)
            await self.base_mode.vehicle.goto(lat, lon, alt)
            
            
        # loop 문 탈출한 경우에는 집 못찾은 것이므로 안전 고도로 상승하여
        # GCS 위치로 복귀함
        self.base_mode.route_record_set = True
        self.base_mode.changeMode(self.prev_mode)        
        
    def __str__(self) -> str:
        return 'RETURN_MODE'

class Drone:
    '''
    드론 동작을 위한 모드의 상위 클래스
    공통적으로 드론의 비행을 위한 동작 수행
    GCS의 명령을 rabbitmq로 수신
    arm, 이륙, 이동, 고도변경, 착륙의 동작을 수행함
    todo : 비행 종료 후 동작 정의 필요
    '''
    
    def __init__(self, device_name, server_addr) -> None:
        '''
        'drone1', 'localhost'
        '''
        self.device_name = device_name
        self.server_addr = server_addr
        
        print(device_name, server_addr)
        
        # rabbitmq message receiver
        self.receiver = mqapi.MqReceiverAsync(device_name, server_addr)
        
        # rabbitmq message sender
        self.sender = mqapi.MqSenderAsync(server_addr)
        
        # mavsdk Drone actuator
        self.vehicle = Vehicle(DRONE_ADDRESS)
        # self.vehicle = Vehicle_Stub(DRONE_ADDRESS)
        
        # ping to server - network checker
        self.networkChecker = networkChecker(server_addr, PING_PERIOD)     
        
        # 현재 모드가 수행할 함수, task의 목록 및 생성된 task의 목록
        self.task_list = []
        self.created_task_list = []
        
        # 네트워크 단절에 따른 네트워크 복귀를 위한 드론 이동 경로 
        self.route_record = []
        
        # 모드 변경을 위해 기존에 동작중인 task를 중지하기 위함, 실제로 동작하는 지는 확인 필요
        self.task_halt = False
        
        # start -> start_task를 통해 각 task가 실행될 때, start_task를 저장함
        self.cur_start = None
        
        # 초기 모드를 normal 모드로
        self.cur_mode = NormalMode(self)
        
        self.next_mode = None
        
        self.route_record_set = True
        
    async def initSystem(self):
        await self.vehicle.initConnect()
        
    def applyTask(self):
                
        self.task_list.clear()        
        self.task_list.append(self.checkNetwork())   # 네트워크 연결 확인
        self.task_list.append(self.updateStatus())    # 기체의 상태 받아옴 - 저장 및 서버 전송 
        self.task_list.append(self.userInteraction())
        
        for single_sub_task in self.cur_mode.task_list:
            self.task_list.append(single_sub_task)
            
        print('task :', self.task_list)
    
    async def userInteraction(self): 
        # todo : 모드 변경시 user interaction 2번 들어가는 문제가 있었는데 해결 필요
        print_text = "cmd>"
        while True:
            user_input = await asyncio.to_thread(input, print_text)
            
            if user_input[:4] == 'MODE':
                if user_input == 'MODE NOR':
                    print(self.cur_mode, '> NORMAL')
                    self.changeMode(NORMAL_MODE)
                elif user_input == 'MODE SEEK':
                    print(self.cur_mode, '> SEEK')
                    self.changeMode(SEEK_MODE)
                elif user_input == 'MODE DROP':
                    print(self.cur_mode, '> DROP')
                    self.changeMode(DROP_MODE)
                elif user_input == 'MODE RTN':
                    print(self.cur_mode, '> RTN')
                    self.changeMode(RETURN_MODE)
                else:
                    print(self.cur_mode)
            elif user_input[:3] == 'NET':
                if user_input == 'NET CUT':
                    self.networkChecker.test__false()
                elif user_input == 'NET CNT':
                    self.networkChecker.test__true()
            else:
                print("cmd>")
                      
    async def processMessage(self): # todo : 현재 상태가 이륙 상태가 아닐때 메세지 거부하기
        '''
        receiver에서 메세지를 받아 해석 후 mavsdk 명령 수행
        '''
        print('waiting for message')
        async for single_message in self.receiver.getMessage():
            
            if "type" not in single_message:
                print("not defined message")
                continue
            await self.vehicle.waitForHold(single_message["type"])
            print("GOT MESSAGE :", single_message["type"])
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
                # disarm은 아마 착륙하면 자동으로 될 것
                pass
            elif single_message["type"] == 'startDrop':
                await self.changeMode(SEEK_MODE)
            else:
                print("undefined message")
            if self.task_halt:
                print("break message")
                break
            
            await self.vehicle.waitForHold(single_message["type"])
     
    async def updateStatus(self):
        '''
        기체의 상태 받아오기, 현재의 상태 저장과, 상태 전송에 사용됨
        '''
        async for velocity, battery, position in self.vehicle.getLocation():
            # print(velocity, battery, position, sep='\n')
            print("Status sent")
            if self.task_halt:
                break
            self.recordRoute(position)
            await self.sendStatus(velocity, battery, position)
            
    def recordRoute(self, position):
        '''
        드론의 현재 이동 위치를 저장
        '''
        if self.route_record_set:
            single_data = {
                "time" : datetime.now().timestamp(),
                "latitude_deg" : position.latitude_deg,
                "longitude_deg" : position.longitude_deg,
                "absolute_altitude_m" : position.absolute_altitude_m,
                "relative_altitude_m" : position.relative_altitude_m
            }
            # todo : 이전 기록과 비교하여 그렇게 차이나지 않는 경우에는 추가로 기록하지 않기
            self.route_record.append(single_data)
            print(self.route_record)
    
    async def sendStatus(self, velocity, battery, position):
        '''
        드론의 현재 상태를 서버로 전송
        현재 시간, 장치명, 위치, 속도, 배터리 정보에 관한 정보 전송
        '''
        data =  {
            "time" : datetime.now().timestamp(),
            "device" : self.device_name,
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
        try:
            async for response in self.networkChecker.ping():
                # print(response)
                print(386, self.cur_mode, response)
                if self.task_halt:
                    break
                
                if type(self.cur_mode) == ReturnMode:
                    print(391)
                    if response == True:
                        print(393)
                        await self.changeMode(self.cur_mode.prev_mode)
                else:
                    print(396)
                    if response == False:
                        print(398)
                        await self.changeMode(RETURN_MODE)
        except asyncio.CancelledError as err:
            print(err)
            
        finally:
            pass # todo
            
    async def changeMode(self, new_mode):
        '''
        모드 변경
        기존 수행중인 task를 종료하고 새로운 객체 생성 후 실행
        '''
        print(task.get_name() for task in asyncio.all_tasks())
        print(348)
        for single_task in self.created_task_list:
            self.task_halt = True
            print(351, single_task)
            single_task.cancel()
            print(353, single_task)
            
        if new_mode == NORMAL_MODE:
            self.cur_mode = NormalMode(self)
        elif new_mode == DROP_MODE:
            self.cur_mode = DropMode(self)
        elif new_mode == SEEK_MODE:
            self.cur_mode = SeekMode(self)
        elif new_mode == RETURN_MODE:
            self.cur_mode = ReturnMode(self, self.cur_mode)
        else:
            print("Mode error")
            self.cur_mode = NormalMode(self)
            
        print(377, self.cur_mode)
        await self.start()       
               
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

    async def start(self):
        '''
        todo : 착륙시, 미션 종료시 아래의 loop 탈출 필요
        주요 기능 동작을 위함
        현재 mode에 맞는 task를 생성하고 실행
        '''
        
        while True:
            self.applyTask()
            print(388)
            self.created_task_list.clear()
            print(390)
            self.task_halt = False
            print(392)

            await self.initSystem()
            print(407, end=": ")
            print(task.get_name() for task in asyncio.all_tasks())
            print(395)
            for single_task in self.task_list:
                print(148, single_task)
                try:
                    single_created_task = asyncio.ensure_future(single_task)
                    print(170, type(single_created_task))
                    self.created_task_list.append(single_created_task)
                    
                except ValueError as val_e:
                    print(val_e)
            try:
                print(413)
                print(task.get_name() for task in asyncio.all_tasks())
                await asyncio.wait(self.created_task_list)
                print(415) # 왜 끝나지...?
            except KeyboardInterrupt:
                await self.stop_task()
      
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='드론 작동을 위한 기본 정보')
    parser.add_argument('-name', help=' : 현재 드론의 이름')
    parser.add_argument('-server', help=' : 서버 주소')
    args = parser.parse_args()  
    
    async def main():
        tracemalloc.start()
        # drone = Drone(args.name, args.server)
        drone = Drone('drone1', 'localhost')
        await drone.start()
        
    asyncio.run(main())