import asyncio
import math
from mavsdk import System
from multiprocessing import *

class Vehicle:
    def __init__(self, system_address) -> None:
        self.system_address = system_address
        asyncio.run(self.initConnect())
        
        
    async def initConnect(self):
        self.drone_system = System()
        await self.drone_system.connect(self.system_address)
        
        print("드론 연결 대기 중...")
        # async for state in self.drone.core.connection_state():
        #     if state.is_connected:
        #         print(f"드론 발견!")
        #         break

        # print("드론의 전역 위치 추정 대기 중...")
        # async for health in self.drone.telemetry.health():  
        #     if health.is_global_position_ok:
        #         print("전역 위치 추정 완료")

    async def connect(self):
        await self.drone.connect(self.system_address)  # 드론 연결

    async def takeoff(self):
        print("-- 이륙 중")
        await self.drone.takeoff()  # 드론 이륙

    async def setElev(self, altitude):
        print(f"고도 변경 중: {altitude}")
        await self.drone.setElev(altitude)  # 드론 고도 변경

    async def wait(self, time):
        print(f"{time}초 대기 중")
        await asyncio.sleep(time)  # 일정 시간 동안 대기

    async def land(self):
        print("-- 착륙 중")
        await self.drone.land()  # 드론 착륙

    async def disarm(self):
        # disarm은 착륙 후 자동으로 될 것이므로 pass
        pass

    async def startDrop(self):
        # startDrop 이벤트가 발생하면 Drop 모드로 변경
        await self.drone.changeMode("Drop")
    
async def run():
    # 드론과 연결합니다.
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("드론 연결 대기 중...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"드론 발견!")
            break

    print("드론의 전역 위치 추정 대기 중...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("전역 위치 추정 완료")
            break

    print("-- 시동 걸기")
    await drone.action.arm()
    await asyncio.sleep(5)

    print("-- 이륙 중")
    await drone.action.takeoff()
    await asyncio.sleep(5)

    # 이동할 위치 설정
    target_latitude = 35.153898
    target_longitude = 128.094925
    target_altitude = 10.0

    # 목표 위치로 이동
    await fly_to_location(drone, target_latitude, target_longitude, target_altitude)

    # 도착 확인
    await check_arrival(drone, target_latitude, target_longitude, target_altitude)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())




async def run():
    # 드론에 연결
    drone = System()
    await drone.connect(system_address="udp://:14540")

    # 드론 이륙
    print("드론 이륙 중...")
    await drone.action.arm()
    await drone.action.takeoff()

    # 이륙 후 5초 대기
    await asyncio.sleep(5)

    # 현재 위치 가져오기
    async for position in drone.telemetry.position():
        current_lat = position.latitude_deg
        current_lon = position.longitude_deg
        current_alt = position.absolute_altitude_m

        # 전방으로 100m 이동
        await move(drone, current_lat + (100 / 111111), current_lon, current_alt)
        print("드론이 앞으로 이동했습니다.")

        # 다음 명령을 위해 5초 대기
        await asyncio.sleep(5)

        # 후방으로 100m 이동
        await move(drone, current_lat - (100 / 111111), current_lon, current_alt)
        print("드론이 뒤로 이동했습니다.")
        
        # 다음 명령을 위해 5초 대기
        await asyncio.sleep(5)
        
        # 좌측으로 100m 이동
        await move(drone, current_lat, current_lon - (100 / (111111 * abs(math.cos(math.radians(current_lat))))), current_alt)
        print("드론이 좌측으로 이동했습니다.")

        # 다음 명령을 위해 5초 대기
        await asyncio.sleep(5)

        # 우측으로 100m 이동
        await move(drone, current_lat, current_lon + (100 / (111111 * abs(math.cos(math.radians(current_lat))))), current_alt)
        print("드론이 우측으로 이동했습니다.")

        # 다음 명령을 위해 5초 대기
        await asyncio.sleep(5)
        
        break  # 한 번만 실행되도록 하기 위해

    # 착륙 명령을 보내기 전에 뒤로 이동이 완료되도록 5초 대기
    await asyncio.sleep(5)

    # 드론 착륙
    print("드론 착륙 중...")
    await drone.action.land()

async def move(drone, new_lat, new_lon, current_alt):
    # 드론 이동 명령 보내기
    await drone.action.goto_location(new_lat, new_lon, current_alt, yaw_deg=0)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

