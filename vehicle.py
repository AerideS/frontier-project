import asyncio
import math
import sys
from mavsdk import System
from math import cos, radians, sqrt

# 최소 안전 거리 (미터)
MIN_SAFE_DISTANCE = 2
# 드론 이동 속도 (미터/초), 적절한 값으로 설정해야 함
DRONE_SPEED = 2

# 고도 정보 전송 주기
LOCATION_BEACON_PERIOD = 5

# 근접 범위 지정
MOVE_ACCURACY = 1

class Vehicle:
    def __init__(self, system_address) -> None:
        self.system_address = system_address
        self.takeoff_altitude = None
        self.drone_system = None  # drone_system 속성 초기화
        
    async def getLocation(self):
        '''
        현재 위치 종합하여 반환
        '''
        await self.initConnect()
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
        self.drone_system = System()
        await self.drone_system.connect(self.system_address)
        
        print("드론 연결 대기 중...")
        async for state in self.drone_system.core.connection_state():
            if state.is_connected:
                print(f"드론 발견!")
                break

        print("드론의 전역 위치 추정 대기 중...")
        async for health in self.drone_system.telemetry.health():
            if health.is_global_position_ok:
                print("전역 위치 추정 완료")
                break

    async def arm(self):
        await self.initConnect()
        await self.drone_system.action.arm()  # 드론 연결

    async def takeoff(self):
        await self.initConnect()
        print("-- 이륙 중")
        if self.takeoff_altitude != None:
            pass
        # self.takeoff_altitude = self.drone_system.action.get_takeoff_altitude()
        await self.drone_system.action.takeoff()  # 드론 이륙

    async def goto(self, target_lat, target_lon, target_alt):
        '''
        input
        output : 이동 결과
        '''
        
        await self.initConnect()
        # 목표 위치 설정
        self.target_position = (target_lat, target_lon, target_alt)

        # 이동 명령 보내기
        await self.drone_system.action.goto_location(target_lat, target_lon, target_alt, 0)

        # 이동 명령이 완료될 때까지 대기
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

        await asyncio.sleep(1)  # 1초 대기

    def calculate_distance(self, current_lat, current_lon, target_lat, target_lon, current_alt, target_alt):
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
        
        await self.initConnect()  # 드론 연결 및 초기화
        
        # 현재 위치를 가져오는 코드
        async for position in self.drone_system.telemetry.position():
            if original_position is None:
                original_position = position
            current_lat = position.latitude_deg
            current_lon = position.longitude_deg
            current_alt = position.absolute_altitude_m
            
            # 대각선 거리 계산
            diagonal_distance = sqrt(north_distance ** 2 + east_distance ** 2)

            # 이동에 소요될 예상 시간 계산 (단위: 초)
            move_duration = diagonal_distance / DRONE_SPEED

            # 대기 시간 계산
            wait_duration = move_duration
            
            new_lat = current_lat + (north_distance / 111111)
            new_lon = current_lon + (east_distance / (111111 * abs(cos(radians(current_lat)))))

            # 이동 처리
            await self.drone_system.action.goto_location(new_lat, new_lon, current_alt, yaw_deg=0)
            
            # 현재 고도가 안전 거리보다 작을 경우 고도 조정
            if current_alt < MIN_SAFE_DISTANCE:
                print("고도를 조정하여 안전 거리를 유지합니다.")
                await self.drone_system.action.goto_location(new_lat, new_lon, current_alt + MIN_SAFE_DISTANCE, yaw_deg=0)


    async def setElev(self, altitude):
        print(f"고도 변경 중: {altitude}")
        await self.initConnect()
        await self.drone_system.setElev(altitude) 
        
    async def wait(self, time):
        print(f"{time}초 대기 중")
        await self.initConnect()
        await self.drone_system.action.hold(time)

    async def land(self):
        print("-- 착륙 중")
        await self.initConnect()
        self.takeoff_altitude = None
        await self.drone_system.action.land()  # 드론 착륙

    async def disarm(self):
        # disarm은 착륙 후 자동으로 될 것이므로 pass
        pass

    async def startDrop(self):
        # startDrop 이벤트가 발생하면 Drop 모드로 변경
        self.drone_system.changeMode("Drop")

async def main():
    system_address = 'udp://:14540'
    vehicle = Vehicle(system_address)
    # drone_system = System()
    # await drone_system.connect(system_address)
    # async for bat in drone_system.telemetry.battery():
    #     print(bat)
    await vehicle.initConnect()
    async for data in vehicle.getLocation():
        velocity, battery, position = data
        print(position, battery, velocity, sep='\n',end='\n------------------\n')
    # if len(sys.argv) > 1:
    #     command = sys.argv[1].lower()

    #     loop = asyncio.get_event_loop()

    #     if command == 'takeoff':
    #         await vehicle.initConnect()
    #         await vehicle.takeoff()
    #     elif command == 'arm':
    #         await vehicle.initConnect()
    #         await vehicle.arm()
    #     elif command == 'land':
    #         await vehicle.initConnect()
    #         await vehicle.land()
    #     elif command == 'goto':
    #         if len(sys.argv) != 5:
    #             print("Usage: python script.py goto <latitude> <longitude> <altitude>")
    #         else:
    #             real_lat, real_lon, real_alt = map(float, sys.argv[2:])
    #             await vehicle.initConnect()
    #             await vehicle.goto(real_lat, real_lon, real_alt)
    #     elif command == 'move_meters':
    #         north_distance = float(input("북쪽으로 얼마나 이동하시겠습니까? (미터단위)"))
    #         east_distance = float(input("동쪽으로 얼마나 이동하시겠습니까? (미터 단위): "))
    #         await vehicle.initConnect()
    #         await vehicle.move_meters(north_distance, east_distance)
    #     else:
    #         print("올바른 명령을 입력하세요.")
    # else:
    #     print("명령을 입력하세요 (takeoff, land, goto, move_meters).")

if __name__ == '__main__':
    asyncio.run(main())
