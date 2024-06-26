import argparse
from networkChecker import networkChecker
import asyncio
from vehicle import Vehicle
# from yoloModule import * 
# from vehicle_stub import *
from datetime import datetime
# from hardware_stub import RaspiCAM__STUB
from math import tan
import tracemalloc
from yoloModule import * 
from jetson.lidar import *
from jetson.motor import *
from jetson.relay import *
from jetson.camera import *
import logging

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
# DRONE_ADDRESS = 'udp://:14540' # local simulator 
DRONE_ADDRESS = 'udp://192.168.0.94:14580' # remote simulator
# DRONE_ADDRESS =  'serial:///dev/ttyACM0' # 


MINIMAL_RECORD_THREADHOLD = 0.1

DROP_MARGIN = 40  # 중계기 투하시 거리에서 제외 # 음수 처리 todo

DROP_TICK = 1

logging.basicConfig(filemode=f'/home/jetson/home/logs/log_{str(datetime.now().timestamp())}', 
                                    format='%(asctime)s %(levelname)s %(message)s %(lineno)d %(pathname)s %(processName)s %(threadName)s',
                                    level=logging.DEBUG, 
                                    datefmt='%m/%d/%Y %I:%M:%S %p',)
    
class NormalMode:
    '''
    일반 모드, 드론이 이동하는 기능만 있으므로 별도 구현은 하지 않음
    '''
    def __init__(self, parent) -> None:
        self.base_mode = parent
        self.sub_task_list = []
        
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
        self.sub_task_list = [self.yoloModule()]
        
        # self.yolo_module = FindTree()
        self.cam_module = RaspiCAM() # 카메라 모듈 
        # self.cam_module = RaspiCAM__STUB()
        self.yolo_module = FindTree() # yolov5 모듈 스텁
        self.lidar_module = LidarModule() # 라이다 모듈 스텁
                
        self.CAM_ANGLE = 63/2 # 라즈베리파이 캠의 화각
        self.CAM_WIDTH_PIXEL = 640
        self.CAM_HEIGHT_PIXEL = 480
    
    def __str__(self) -> str:
        return 'SEEK_MODE'
    
    async def seek_stub(self):
        cnt = 0
        try:
            while cnt < 10:
                # print("SeekMode operating...", cnt)
                logging.debug(f'"SeekMode stub operating...", {cnt}')
                await asyncio.sleep(1)
                cnt += 1
                # print("SeekMode, sub")
                # print(self.base_mode.created_sub_task_list)
                # print("SeekMode, main")
                # print(self.base_mode.created_task_list)
                
            await self.base_mode.changeMode('DROP_MODE')

        except asyncio.CancelledError as err:
            logging.CRITICAL("asyncio.CancelledError", str(err))
            # print("asyncio.CancelledError", err)
    
    async def yoloModule(self):
        '''
        1. 사진 받는다
        2. 객체 확인한다
        3. 이동한다
        4. 모드 변경한다
        '''
        cnt = 0
        while True: # 카운트 세다가 없으면 넘어가기?
            logging.debug(f'yolo Module started {cnt}')
            this_pic = self.cam_module.getPicture() # 사진 받아옴
            # this_pic = self.cam_module.savePicture()
            print('나 됐어')

            logging.debug(f'got picture, {type(this_pic)}')
            if type(this_pic) is None:
                logging.debug(f'NO PICTUTE CAPTURED')
                continue
            process_result = await self.yolo_module.process_image(this_pic)
            logging.debug(f'got coordinate {str(process_result)}')
            if (process_result[0] is None) or (process_result[1] is None):
                logging.debug(f'fail to detect image')
                pass # 결과가 없을 경우 이동하고 다시 비행하는 과정 포함
            else:
                terrain_distance = self.lidar_module.getAltitude()
                x_pix, y_pix = process_result
                if (x_pix is None) or (y_pix is None):
                    logging.debug(f'invalid result : {x_pix, y_pix}')
                    continue 
                x_dist, y_dist = self.convertPixelToMeters(x_pix, y_pix, terrain_distance)
                print(126)
                logging.debug(f'move to {x_dist}, {y_dist}')
                print(128)
                await self.base_mode.vehicle.move_meters(x_dist, y_dist)
                print(130)
                await self.base_mode.changeMode('DROP_MODE')
                print(132)
                break
            
            await asyncio.sleep(1)
            cnt += 1
            
    def convertPixelToMeters(self, pixel_width_dis, pixel_height_dis, lidar_dis):
        '''
        pixel_width_dis     : 픽셀 가로 길이
        pixel_height_dis    : 픽셀 세로 길이
        lidar_dis           : 라이다 측정 수목간 차이
        '''
        lidar_dis = round(lidar_dis/100, 1)
        absolute_whole_width = 2* lidar_dis * math.tan(self.CAM_ANGLE)
        
        conversion_factor = absolute_whole_width / self.CAM_WIDTH_PIXEL
        
        x_dist = conversion_factor * pixel_width_dis
        y_dist = conversion_factor * pixel_height_dis
        
        return x_dist, y_dist

class DropMode:
    '''
    수목 탐색 후 중계기 투하
    현재 지점의 위치 입력받아 중계기 마운트 동작
    '''
    def __init__(self, parent) -> None:
        self.base_mode = parent
        self.sub_task_list = [self.dropRepeater()]
            
        self.lidar_module = LidarModule()
        
    def __str__(self) -> str:
        return 'DROP_MODE'
    
    async def drop_stub(self):
        cnt = 0
        try:
            while cnt < 10:
                logging.debug(f'DropMode operating..., {cnt}')
                print("DropMode operating...", cnt) 
                await asyncio.sleep(1)
                cnt += 1
                print("DropMode, sub")
                # print(self.base_mode.created_sub_task_list)
                print("DropMode main")
                # print(self.base_mode.created_task_list)
                
            await self.base_mode.changeMode('NORMAL_MODE')
                
        except asyncio.CancelledError as err:
            print("asyncio.CancelledError", err)
        
    async def dropRepeater(self):
        '''
        todo : 지금 위치를 전달받아야 할까?
        '''
        # print("DROP REPEATER --------")
        logging.debug(f'DROP REPEATER')
        height = self.lidar_module.getAltitude()
        # print("GOT HEIGHT  ----------")
        logging.debug(f'GOT HEIGHT {height - DROP_MARGIN}')
        self.base_mode.dropper.descent_repeater(height - DROP_MARGIN)
        logging.debug(f'DROP COMPLETE')
        self.base_mode.cutter.cut_string()
        # print("DROP COMPLETE --------")
        logging.debug(f'CUT COMPLETE')
        await self.base_mode.changeMode('NORMAL_MODE')
          
class ReturnMode:
    '''
    운용중 네트워크 단절에 따른 복귀모드
    이전의 위치 기록을 전달받아 해당 기록을 따라 이동
    '''
    def __init__(self, parent, prev_mode) -> None:
        self.base_mode = parent
        self.sub_task_list = [self.traceBack()]
        self.prev_mode = str(prev_mode)
        self.start_point = None
        self.base_mode.route_record_set = False
        
    async def return_stub(self):
        cnt = 0
        try:
            while cnt < 3:
                print("ReturnMode operating...")
                await asyncio.sleep(1)
                cnt += 1
                print("DropMode sub", end=" ")
                print(self.base_mode.created_sub_task_list)
                print("DropMode main", end=" ")
                print(self.base_mode.created_task_list)
            
            # await self.base_mode.changeMode('NORMAL_MODE')
                
        except asyncio.CancelledError as err:
            print("asyncio.CancelledError", err)
                
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
        self.start_point = self.base_mode.route_record[-1]
        logging.debug(f'Start Trace Back')
        for single_point in reversed(self.base_mode.route_record):
            lat = round(single_point["latitude_deg"], 5)
            lon = round(single_point["longitude_deg"], 5)
            alt = round(single_point["absolute_altitude_m"], 2)
            # print("get back to...", lat, lon, alt)
            logging.debug(f'get back to... {lat}, {lon}, {alt}')
            await self.base_mode.vehicle.goto(lat, lon, alt)
            
        # loop 문 탈출한 경우에는 집까지 돌아온 것이므로 착륙
        # GCS 위치로 복귀함
        await self.base_mode.vehicle.land()
        await self.base_mode.changeMode(self.prev_mode)        
        
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
        logging.debug(f'device_name : {device_name}, server_addr : {server_addr}')
        # print(207, device_name, server_addr)
        
        # rabbitmq message receiver
        self.receiver = mqapi.MqReceiverAsync(device_name, server_addr)
        
        # rabbitmq message sender
        self.sender = mqapi.MqSenderAsync(server_addr)
        
        # mavsdk Drone actuator
        self.vehicle = Vehicle(DRONE_ADDRESS)
        # self.vehicle = Vehicle_Stub(DRONE_ADDRESS)

        self.dropper = ReelModule() # 릴은 항상 동작하도록
        self.cutter = RelayModule()
        
        # ping to server - network checker
        self.networkChecker = networkChecker(server_addr, PING_PERIOD)     
        
        # 현재 모드가 수행할 함수, task의 목록 및 생성된 task의 목록
        self.task_list = [self.processMessage(), self.checkNetwork(), \
            self.updateStatus(), self.task_manager()] #self.userInteraction(), 
        
        self.created_task_list = []
        
        self.created_sub_task_list = []
        
        # 네트워크 단절에 따른 네트워크 복귀를 위한 드론 이동 경로 
        self.route_record = []
        
        # 모드 변경을 위해 기존에 동작중인 task를 중지하기 위함, 실제로 동작하는 지는 확인 필요
        self.task_halt = False
        
        # start -> start_task를 통해 각 task가 실행될 때, start_task를 저장함
        # self.cur_start = None
        
        # 초기 모드를 normal 모드로
        self.cur_mode = NormalMode(self)
        
        self.route_record_set = True
        
    async def normal_stub(self):
        cnt = 0
        try:
            while True:
                print("NormalMode operating...")
                await asyncio.sleep(0.5)
                cnt += 1
                if (cnt%5 == 4) and (type(self.cur_mode) == NormalMode):
                    await self.changeMode('SEEK_MODE')
                
        except asyncio.CancelledError as err:
            print("asyncio.CancelledError", err)
            
    async def initSystem(self):
        await self.vehicle.initConnect()
        await self.receiver.initConnection()
            
    # async def userInteraction(self): 
    #     # todo : 모드 변경시 user interaction 2번 들어가는 문제가 있었는데 해결 필요
    #     print_text = "cmd>"
    #     while True:
    #         user_input = await asyncio.to_thread(input, print_text)
            
    #         if user_input[:4] == 'MODE':
    #             if user_input == 'MODE NOR':
    #                 print(self.cur_mode, '> NORMAL')
    #                 if type(self.cur_mode) != NormalMode:
    #                     await self.changeMode('NORMAL_MODE')
    #             elif user_input == 'MODE SEEK':
    #                 print(self.cur_mode, '> SEEK')
    #                 if type(self.cur_mode) != SeekMode:
    #                     await self.changeMode('SEEK_MODE')
    #             elif user_input == 'MODE DROP':
    #                 print(self.cur_mode, '> DROP')
    #                 if type(self.cur_mode) != DropMode:
    #                     await self.changeMode('DROP_MODE')
    #             elif user_input == 'MODE RTN':
    #                 print(self.cur_mode, '> RTN')
    #                 if type(self.cur_mode) != ReturnMode:
    #                     await self.changeMode('RETURN_MODE')
    #             else:
    #                 print(self.cur_mode)
    #         elif user_input[:3] == 'NET':
    #             if user_input == 'NET CUT':
    #                 self.networkChecker.test__false()
    #             elif user_input == 'NET CNT':
    #                 self.networkChecker.test__true()
    #         else:
    #             print("cmd>")
                
    async def getCurrentMode(self):
        while True:
            yield type(self.cur_mode)
                      
    async def processMessage(self): # todo : 현재 상태가 이륙 상태가 아닐때 메세지 거부하기
        '''
        receiver에서 메세지를 받아 해석 후 mavsdk 명령 수행
        '''
        print('waiting for message')
        logging.debug("waiting for message")
        async for single_message in self.receiver.getMessage():
            
            if "type" not in single_message:
                logging.CRITICAL(f'not defined message{str(single_message)}')
                print("not defined message")
                continue
            await self.vehicle.waitForHold(single_message["type"])
            
            async for mode in self.getCurrentMode():
                print(357, mode)
                logging.debug(f"wait for normal mode. cur:{mode}")
                if mode == NormalMode:
                    break
                await asyncio.sleep(0.5)
            logging.debug(f"GOT MESSAGE : {str(single_message)}")
            print("GOT MESSAGE :", single_message["type"])
            if single_message["type"] == 'arm':
                await self.vehicle.arm()
            elif single_message["type"] == 'takeoff':
                if 'altitude' in single_message:
                    logging.debug(f"takeoff, altitude : {single_message['altitude']}")
                    await self.vehicle.takeoff(single_message['altitude'])
            elif single_message["type"] == 'goto':
                if ('latitude' in single_message) and ('longitude' in single_message):
                    logging.debug(f"goto, lat : {single_message['latitude']}, lng : {single_message['longitude']}")
                    await self.vehicle.goto(single_message['latitude'], single_message['longitude'])
            elif single_message["type"] == 'setElev':
                if 'altitude' in single_message:
                    logging.debug(f"setElev, {single_message['altitude']}")
                    await self.vehicle.setElev(single_message['altitude'])
            elif single_message["type"] == 'wait':
                if 'time' in single_message:
                    logging.debug(f"wait, {single_message['time']}")
                    await self.vehicle.wait(single_message['time'])
            elif single_message["type"] == 'land':
                logging.debug(f"land,")
                await self.vehicle.land()
            elif single_message["type"] == 'disarm':
                # disarm은 아마 착륙하면 자동으로 될 것
                logging.debug(f"disarm,")
                pass
            elif single_message["type"] == 'startDrop':
                logging.debug("startDrop, change to SEEK MODE")
                print("startDrop, change to SEEK MODE")
                if ('latitude' in single_message) and ('longitude' in single_message):
                    logging.debug(f"goto, {single_message['latitude']}, {single_message['longitude']}")
                    await self.vehicle.goto(single_message['latitude'], single_message['longitude'])
                await self.changeMode('SEEK_MODE')
                print("changed")
                break
            elif single_message["type"] == 'cutString':
                self.cutter.cut_string()
            elif single_message["type"] == 'ascent_repeater':
                self.dropper.ascent_repeater(single_message['distance'])
                # self.dropper.ascent_repeater(DROP_TICK)
            elif single_message["type"] == 'descent_repeater':
                self.dropper.descent_repeater(single_message['distance'])
                # self.dropper.descent_repeater(DROP_TICK)

            else:
                logging.critical(f"undefined message, {str(single_message)}")
                print("undefined message")
            if self.task_halt:
                logging.critical("break message")
                print("break message")
                break
            
            await self.vehicle.waitForHold(single_message["type"])
            
            # print(320)
     
    async def updateStatus(self):
        '''
        기체의 상태 받아오기, 현재의 상태 저장과, 상태 전송에 사용됨
        '''
        prev_sent = datetime.now().timestamp()
        async for velocity, battery, position in self.vehicle.getLocation():
            logging.debug("Status sent")
            print("Status sent", datetime.now().timestamp() - prev_sent)
            prev_sent = datetime.now().timestamp()
            if self.task_halt:
                break
            self.recordRoute(position)
            print(self.route_record)
            await self.sendStatus(velocity, battery, position)
            
    def getDistance(self, lat_1, lon_1, alt_1, lat_2, lon_2, alt_2):
        # 지구의 반지름 (단위 : m)
        R = 6371000
        
        # 위도 및 경도를 라디안 단위로 변환
        lat1_rad = math.radians(lat_1)
        lon1_rad = math.radians(lon_1)
        lat2_rad = math.radians(lat_2)
        lon2_rad = math.radians(lon_2)
        # 위도 및 경도 간의 차이를 계산합니다.
        delta_lat = lat2_rad - lat1_rad
        delta_lon = lon2_rad - lon1_rad
        # Haversine 공식을 사용하여 거리를 계산합니다.
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        # 거리를 계산합니다.
        distance = R * c
        # 고도 차이를 추가하여 거리를 계산합니다.
        distance_with_altitude = math.sqrt(distance ** 2 + (alt_1 - alt_2) ** 2)
        
        return distance_with_altitude
            
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
            logging.debug(f"cur record, {str(single_data)}")
            if len(self.route_record) == 0:
                self.route_record.append(single_data)
            # todo : 이전 기록과 비교하여 그렇게 차이나지 않는 경우에는 추가로 기록하지 않기
            distance = self.getDistance(single_data["latitude_deg"], single_data["longitude_deg"], \
                single_data['absolute_altitude_m'], \
                self.route_record[-1]["latitude_deg"], self.route_record[-1]["longitude_deg"], \
                    self.route_record[-1]["absolute_altitude_m"])
            print('distance ',distance)
            logging.debug(f'distance {distance}')
            if distance > MINIMAL_RECORD_THREADHOLD:
                self.route_record.append(single_data)
                logging.debug('route recorded')
                print('route recorded :', self.route_record)
            else:
                logging.debug('too close, pass recording')
                print("too close, pass recording")
    
    async def sendStatus(self, velocity, battery, position):
        '''
        드론의 현재 상태를 서버로 전송
        현재 시간, 장치명, 위치, 속도, 배터리 정보에 관한 정보 전송

        type : status, ... 
        '''
        data =  {
            "type" : "status",
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
                logging.debug(f"network check, {self.cur_mode}, {response}")
                if self.task_halt:
                    break
                
                if type(self.cur_mode) == ReturnMode:
                    if response == True:
                        logging.debug(f"return mode, network retrived, change to {self.cur_mode.prev_mode}, \
                            {type(self.cur_mode.prev_mode)}")
                        print("return mode, network retrived, change to ", self.cur_mode.prev_mode, \
                            type(self.cur_mode.prev_mode))
                        async for _, _, position in self.vehicle.getLocation():
                            end_point = position
                            start_point = self.cur_mode.start_point             
                
                            message = {
                                'type' : 'hole',
                                'start_lat' : start_point['latitude_deg'],
                                'start_lng' : start_point['longitude_deg'],
                                'start_alt' : start_point['absolute_altitude_m'],
                                'end_lat' : end_point.latitude_deg,
                                'end_lng' : end_point.longitude_deg,
                                'end_alt' : end_point.absolute_altitude_m,
                                'time' : float(datetime.now().timestamp())
                            }
                            
                            await self.sender.send_message(message, "SERVER")
                            break
                        print(524)
                        self.route_record_set = True
                        await self.changeMode(self.cur_mode.prev_mode)
                else:
                    print(396)
                    if response == False:
                        print(398)
                        # await self.changeMode('RETURN_MODE') # 리턴 모드로 못들어가게
        except asyncio.CancelledError as err:
            print("asyncio.CancelledError", err)
            
        finally:
            pass # todo
            
    async def changeMode(self, new_mode):
        '''
        모드 변경
        기존 수행중인 task를 종료하고 새로운 객체 생성 후 실행
        '''
        # for single_task in self.created_sub_task_list:
        #     self.task_halt = True
        #     single_task.cancel()
        #     print(440, single_task)
        logging.debug("change mode")
            
        if new_mode == 'NORMAL_MODE':
            logging.debug("NORMAL_MODE")
            self.cur_mode = NormalMode(self)
        elif new_mode == 'DROP_MODE':
            logging.debug("DROP_MODE")
            self.cur_mode = DropMode(self)
        elif new_mode == 'SEEK_MODE':
            logging.debug("SEEK_MODE")
            self.cur_mode = SeekMode(self)
        elif new_mode == 'RETURN_MODE':
            logging.debug("RETURN_MODE")
            self.cur_mode = ReturnMode(self, self.cur_mode)
        else:
            logging.error("Mode error")
            print("Mode error", new_mode)
            self.cur_mode = NormalMode(self)
 
        logging.debug(str(self.cur_mode))
        logging.debug(str(self.created_task_list))
        logging.debug(str(self.created_sub_task_list))

        
        # await self.start()       
               
    async def stop_task(self):
        '''
        수행중인 task를 종료함
        '''
        # print(129)
        for single_task in self.created_task_list:
            try:
                single_task.cancel()
            except asyncio.CancelledError:
                print("task canceled")     
                

    #     return created_task_list

    async def clear_sub_task(self):
        logging.debug("clear_sub_task")
        # for single_task in self.created_task_list:
        #     print(single_task)
        #     single_task.cancel()
        
        # self.created_task_list.clear()
        
        for single_task in self.created_sub_task_list:
            print(single_task)
            single_task.cancel()
            
        self.created_sub_task_list.clear()


    async def task_manager(self):
        cur_mode = NormalMode
        for single_task in self.created_sub_task_list:
            single_task.cancel()
            
        self.created_sub_task_list.clear()
        
        while True:
            if type(self.cur_mode) != cur_mode:
                cur_mode = type(self.cur_mode)
                loop = asyncio.get_event_loop()
                for single_task in self.created_sub_task_list:
                    single_task.cancel()
                
                self.created_sub_task_list.clear()
                
                for single_task in self.cur_mode.sub_task_list:
                    self.created_sub_task_list.append(loop.create_task(single_task))
                    
                await asyncio.gather(*self.created_sub_task_list)
            await asyncio.sleep(0.1)
    
    async def start(self):
        '''
        todo : 착륙시, 미션 종료시 아래의 loop 탈출 필요
        주요 기능 동작을 위함
        현재 mode에 맞는 task를 생성하고 실행
        
        '''
        # 초기 시스템 설정
        logging.debug("system started")
        self.created_task_list = [asyncio.create_task(task) for task in self.task_list]
        cnt = 0
        while True:
            await self.clear_sub_task()
            try:
                
                print(587, self.cur_mode)
                logging.debug(str(self.cur_mode))
                print(590, self.created_sub_task_list)
                logging.debug(str(self.created_sub_task_list))
                print(591, self.created_task_list)
                logging.debug(str(self.created_task_list))
                print(590)
                await asyncio.gather(*self.created_task_list, *self.created_sub_task_list)
                            
            except KeyboardInterrupt as err:
                logging.debug(str(err))
                await self.stop_task()
            # except asyncio.CancelledError:
                
                
            if cnt > 3:
                logging.debug(f"cnt {cnt}")
                return 
            cnt += 1
      
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='드론 작동을 위한 기본 정보')
    parser.add_argument('-name', help=' : 현재 드론의 이름')
    parser.add_argument('-server', help=' : 서버 주소')
    args = parser.parse_args()  
    
    async def main():
        tracemalloc.start()
        # drone = Drone(args.name, args.server)
        # drone = Drone('drone1', '203.255.57.136')
        drone = Drone('drone1', '192.168.0.94')
        await drone.initSystem()
        await drone.start()
        
    asyncio.run(main())
