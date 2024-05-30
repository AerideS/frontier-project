import asyncio
import math
import sys
from mavsdk import System, telemetry
from math import cos, radians, sqrt
import logging

# 최소 안전 거리 (미터)
MIN_SAFE_DISTANCE = 2
# 드론 이동 속도 (미터/초), 적절한 값으로 설정해야 함
DRONE_SPEED = 2

# 고도 정보 전송 주기
LOCATION_BEACON_PERIOD = 2

# 근접 범위 지정
MOVE_ACCURACY = 0.15

ARRIVAL_CHECK_PERIOD = 0.5

class Vehicle:
    def __init__(self, system_address) -> None:
        self.system_address = system_address
        self.takeoff_altitude = None
        self.drone_system = None  # drone_system 속성 초기화
        self.initiated = False
        # asyncio.create_task(self.initConnect())
        
    async def checkArrival(self, latitude, longitude):
        while True:
            
            await asyncio.sleep(ARRIVAL_CHECK_PERIOD)
            
    async def check_armed(self):
        async for is_armed in self.drone_system.telemetry.armed():
            return is_armed
        
    async def waitForHold(self, cur_order):
        '''
        드론의 현재 비행 상태를 받아옴
        '''
        try:
            async for mode in self.drone_system.telemetry.flight_mode():
                print(mode, cur_order)
                logging.debug("waiting for mode change, mode :{mode}, cur_order :{cur_order}")

                # print(type(mode))
                if mode == telemetry.FlightMode.HOLD:
                    '''
                    이전 동작을 완료한 경우 break
                    '''
                    logging.debug("Hold detected, change to operation")
                    break
        except GeneratorExit as e:
            print(e, cur_order)

    async def getLocation(self):
        '''
        현재 위치 종합하여 반환
        '''
        # while self.drone_system == None:
        #     await asyncio.sleep(0.5)
        
        while True:
            battery, velocity, position = None, None, None
            async for singel_vel in self.drone_system.telemetry.velocity_ned():
                velocity = singel_vel
                break
            async for singel_bat in self.drone_system.telemetry.battery():
                battery = singel_bat
                break
            async for singel_loc in self.drone_system.telemetry.position():
                position = singel_loc
                break
            
            yield velocity, battery, position    
            
            await asyncio.sleep(LOCATION_BEACON_PERIOD)
            
    async def initConnect(self):
        logging.debug("start initializing")
        
        if self.drone_system is None:
        
            self.drone_system = System()
            await self.drone_system.connect(self.system_address)
            
            print("드론 연결 대기 중...")
            logging.debug("waing for drone connection")
            async for state in self.drone_system.core.connection_state():
                if state.is_connected:
                    print(f"드론 발견!")
                    logging.debug("found drone")  
                    break
            
            logging.debug("waing for GPS")
            print("드론의 전역 위치 추정 대기 중...")
            async for health in self.drone_system.telemetry.health():
                if health.is_global_position_ok:
                    print("전역 위치 추정 완료")
                    logging.debug("GPS found")
                    break
        
    async def arm(self):
        # await self.initConnect()
        await self.drone_system.action.arm()  # 드론 연결

    async def takeoff(self, target_altitude=None):
            # await self.initConnect()
            print("-- 이륙 중, 고도 :", target_altitude)
            if target_altitude != None:
                await self.drone_system.action.set_takeoff_altitude(target_altitude)
            await self.drone_system.action.takeoff()  # 드론 이륙
            print('--takeoff complete')

    async def goto(self, target_lat, target_lon, target_alt=None):
        '''
        input
        output : 이동 결과
        '''
        print("GOTO : ", target_lat, target_lon, target_alt)
        
        if await self.check_armed() is False:
            print("unable to move when disarmed")
            return
        
        if target_alt is None:
            async for alt in self.drone_system.telemetry.altitude():
                target_alt = alt.altitude_monotonic_m
                break
        # await self.initConnect()
        # 목표 위치 설정
        self.target_position = (target_lat, target_lon, target_alt)

        # 이동 명령 보내기
        await self.drone_system.action.goto_location(target_lat, target_lon, target_alt, 0.0)

        # 스레드 오류 생김
        
        # 이동 명령이 완료될 때까지 대기
        try:
            while True:
                # 현재 위치 업데이트

                async for position in self.drone_system.telemetry.position():
                    self.current_position = (position.latitude_deg, position.longitude_deg, position.absolute_altitude_m)
                    break

                # 현재 위치와 목표 위치 사이의 거리 계산
                distance = self.calculate_distance(*self.current_position, *self.target_position)

                # 거리가 기준 이내인지 확인하여 반환
                if distance <= MOVE_ACCURACY:
                    break
                print("moving...", distance, MOVE_ACCURACY, self.current_position, self.target_position)
                await asyncio.sleep(ARRIVAL_CHECK_PERIOD)
        except GeneratorExit:
            print("why?")


        # await asyncio.sleep(1)  # 1초 대기

    def calculate_distance(self, current_lat, current_lon, current_alt, target_lat, target_lon, target_alt):
        # 지구의 반지름 (단위 : m)
        R = 6371000
        
        # 위도 및 경도를 라디안 단위로 변환
        lat1_rad = math.radians(current_lat)
        lon1_rad = math.radians(current_lon)
        lat2_rad = math.radians(target_lat)
        lon2_rad = math.radians(target_lon)
        # 위도 및 경도 간의 차이를 계산합니다.
        delta_lat = lat2_rad - lat1_rad
        delta_lon = lon2_rad - lon1_rad
        # Haversine 공식을 사용하여 거리를 계산합니다.
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        # 거리를 계산합니다.
        distance = R * c
        # 고도 차이를 추가하여 거리를 계산합니다.
        distance_with_altitude = math.sqrt(distance ** 2 + (target_alt - current_alt) ** 2)
        
        return distance_with_altitude

    async def move_meters(self, north_distance, east_distance):
        original_position = None
        print('move_meters', north_distance, east_distance)
        if await self.check_armed() is False:
            print("unable to move when disarmed")
            return
        
        await asyncio.sleep(0.5) # todo : 이거는 뭐임??
        # 현재 위치를 가져오는 코드
 
        print(174)
        async for position in self.drone_system.telemetry.position():
            if original_position is None:
                original_position = position
            print(position)
            current_lat = position.latitude_deg
            current_lon = position.longitude_deg
            current_alt = position.absolute_altitude_m
            
            # 대각선 거리 계산
            diagonal_distance = sqrt(north_distance ** 2 + east_distance ** 2)

            # 이동에 소요될 예상 시간 계산 (단위: 초)
            move_duration = diagonal_distance / DRONE_SPEED

            # 대기 시간 계산
            # wait_duration = move_duration

            new_lat = current_lat + (north_distance / 111111)
            new_lon = current_lon + (east_distance / (111111 * abs(cos(radians(current_lat)))))

            # 이동 처리
            await self.goto(new_lat, new_lon, current_alt)

            # 현재 고도가 안전 거리보다 작을 경우 고도 조정
            if current_alt < MIN_SAFE_DISTANCE:
                print("고도를 조정하여 안전 거리를 유지합니다.")
                await self.goto(new_lat, new_lon, current_alt + MIN_SAFE_DISTANCE)
                
            break

    async def setElev(self, altitude):
        print(f"고도 변경 중: {altitude}")
        # await self.initConnect()
        await self.drone_system.setElev(altitude) 
        # todo : 작동 되도록 : 고도값 주면 고도 변경 되도록
        
    async def wait(self, time):
        print(f"{time}초 대기 중")
        # await self.initConnect()
        await self.drone_system.action.hold() # 매개변수 개수 틀림
        await asyncio.sleep(time)

    async def land(self):
        print("-- 착륙 중")     
        # await self.initConnect()
        self.takeoff_altitude = None
        print(189)
        await self.drone_system.action.land()  # 드론 착륙
        print(191)
        
    async def disarm(self):
        # disarm은 착륙 후 자동으로 될 것이므로 pass
        pass

async def main():
    system_address = 'udp://:14540'
    vehicle = Vehicle(system_address)
    await vehicle.initConnect()
    await vehicle.takeoff(30)
    # await vehicle.arm()
    # await asyncio.sleep(5)
    # await vehicle.takeoff()
    # await asyncio.sleep(10)
    # await vehicle.move_meters(1,1)

if __name__ == '__main__':
    asyncio.run(main())
