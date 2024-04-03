from mavsdk import System
import asyncio
from math import cos, radians

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
        await move(drone, current_lat, current_lon - (100 / (111111 * abs(cos(radians(current_lat))))), current_alt)
        print("드론이 좌측으로 이동했습니다.")

        # 다음 명령을 위해 5초 대기
        await asyncio.sleep(5)

        # 우측으로 100m 이동
        await move(drone, current_lat, current_lon + (100 / (111111 * abs(cos(radians(current_lat))))), current_alt)
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
