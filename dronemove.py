import sys
import asyncio
from mavsdk import System
SYSTEM_ADDRESS="udp://:14540"

class DroneController:
    def __init__(self, system_address=SYSTEM_ADDRESS):
        # self.drone = Drone()  # Drone 클래스의 인스턴스 생성
        self.system_address = system_address

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
    controller = DroneController()

    await controller.connect()  # 드론 연결

    if len(sys.argv) == 2:
        command = sys.argv[1]
        if command == 'takeoff':
            await controller.takeoff()  # 이륙
        elif command == 'land':
            await controller.land()  # 착륙
    elif len(sys.argv) == 5 and sys.argv[1] == 'goto':
        latitude = float(sys.argv[2])
        longitude = float(sys.argv[3])
        altitude = float(sys.argv[4])
        await controller.goto(latitude, longitude)  # 목표 위치로 이동
        await controller.setElev(altitude)  # 고도 설정
    elif len(sys.argv) == 3 and sys.argv[1] == 'wait':
        time = float(sys.argv[2])
        await controller.wait(time)  # 대기
    elif len(sys.argv) == 2 and sys.argv[1] == 'disarm':
        await controller.disarm()  # disarm
    elif len(sys.argv) == 2 and sys.argv[1] == 'startDrop':
        await controller.startDrop()  # startDrop

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())  # 비동기 실행

