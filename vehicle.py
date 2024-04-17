import asyncio
import math
from mavsdk import System
from multiprocessing import *

class Vehicle:
    def __init__(self, system_address) -> None:
        self.system_address = system_address
        self.takeoff_altitude = None
        
        # asyncio.run(self.initConnect())
        asyncio.get_event_loop().run_until_complete(self.initConnect())
        print(11)
        
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
            
        print(1)

    async def arm(self):
        await self.drone_system.action.arm()  # 드론 연결

    async def takeoff(self):
        print("-- 이륙 중")
        if self.takeoff_altitude != None:
            pass
        self.takeoff_altitude = self.drone_system.action.get_takeoff_altitude()
        await self.drone_system.action.takeoff()  # 드론 이륙

    async def setElev(self, altitude):
        print(f"고도 변경 중: {altitude}")
        await self.drone_system.setElev(altitude)  # 드론 고도 변경
        
    async def goto(self, longitude, latitude):
        pass

    async def wait(self, time):
        print(f"{time}초 대기 중")
        await self.drone_system.action.hold(time)

    async def land(self):
        print("-- 착륙 중")
        self.takeoff_altitude = None
        await self.drone_system.action.land()  # 드론 착륙

    async def disarm(self):
        # disarm은 착륙 후 자동으로 될 것이므로 pass
        pass

    async def startDrop(self):
        # startDrop 이벤트가 발생하면 Drop 모드로 변경
        await self.drone_system.changeMode("Drop")
    
    # async def move_meters(self, )
    
    
    
if __name__ == '__main__':
    async def test_vehicle(vehicle):        
        await vehicle.arm()
        await vehicle.takeoff()
        await vehicle.land()
        
    system_address = 'udp://:14540'
    vehicle = Vehicle(system_address)
    print(111)
    
    # asyncio.run(test_vehicle(vehicle))
    # asyncio.create_task(test_vehicle(vehicle))
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(test_vehicle(vehicle))

