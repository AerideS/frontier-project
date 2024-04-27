import asyncio
import math
from mavsdk import System
from multiprocessing import *

WAIT_PERIOD = 1


class Vehicle_Stub:
    def __init__(self, system_address) -> None:
        self.system_address = system_address
        self.takeoff_altitude = None
        asyncio.run(self.initConnect())
            
    async def initConnect(self):
        '''
        테스트 스텁
        '''
        await asyncio.sleep(WAIT_PERIOD)
        print("init completed")

    async def arm(self):
        '''
        테스트 스텁
        '''
        await asyncio.sleep(WAIT_PERIOD)
        print("arm completed")
        
    async def takeoff(self):
        '''
        테스트 스텁
        '''
        await asyncio.sleep(WAIT_PERIOD)
        print("takeoff completed")
        
    async def goto(self, latitude, longitude):
        '''
        테스트 스텁
        '''
        await asyncio.sleep(WAIT_PERIOD)
        print("goto completed")
        
    async def setElev(self, altitude):
        '''
        테스트 스텁
        '''
        await asyncio.sleep(WAIT_PERIOD)
        print("setElev completed")
        
    async def wait(self, time):
        '''
        테스트 스텁
        '''
        await asyncio.sleep(WAIT_PERIOD)
        print("wait completed")
        
    async def land(self):
        '''
        테스트 스텁
        '''
        await asyncio.sleep(WAIT_PERIOD)
        print("land completed")

    async def disarm(self):
        '''
        테스트 스텁
        '''
        await asyncio.sleep(WAIT_PERIOD)
        print("disarm completed")
        
    async def startDrop(self):
        # startDrop 이벤트가 발생하면 Drop 모드로 변경
        await self.drone_system.changeMode("Drop")
    
    async def move_meters(self, m_north, m_east):
        '''
        # 계산식
        입력 : 현재 위도, 경도, 북쪽 이동 거리, 동쪽 이동 거리
        출력 : 목표지점 위도(target_latitude), 목표지점 경도(target_longitude)
        '''
        target_latitude ,target_longitude = None, None
        await self.goto(target_latitude, target_longitude)
        
if __name__ == '__main__':
    async def test_vehicle(vehicle):        
        await vehicle.arm()
        await vehicle.takeoff()
        await vehicle.land()
        
    system_address = 'udp://:14540'
    vehicle = Vehicle_Stub(system_address)
    
    asyncio.run(test_vehicle(vehicle))
