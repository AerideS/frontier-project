from mavsdk import System
import asyncio
from math import cos, radians, sqrt

# 최소 안전 거리 (미터)
MIN_SAFE_DISTANCE = 2
# 드론 이동 속도 (미터/초), 적절한 값으로 설정해야 함
DRONE_SPEED = 2

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

    original_position = None

    # 현재 위치 가져오기
    async for position in drone.telemetry.position():
        if original_position is None:
            original_position = position
        current_lat = position.latitude_deg
        current_lon = position.longitude_deg
        current_alt = position.absolute_altitude_m

        # 이동 거리 입력 받기
        move_distance_north = float(input("북쪽으로 얼마나 이동하시겠습니까? (미터 단위): "))
        move_distance_east = float(input("동쪽으로 얼마나 이동하시겠습니까? (미터 단위): "))

        # 대각선 거리 계산
        diagonal_distance = sqrt(move_distance_north ** 2 + move_distance_east ** 2)

        # 이동에 소요될 예상 시간 계산 (단위: 초)
        move_duration = diagonal_distance / DRONE_SPEED

        # 대기 시간 계산
        wait_duration = move_duration

        # 이동 처리
        await move(drone,
                   current_lat + (move_distance_north / 111111),
                   current_lon + (move_distance_east / (111111 * abs(cos(radians(current_lat))))),
                   current_alt)

        # 다음 명령을 위해 대기
        await asyncio.sleep(wait_duration)

        break  # 한 번만 실행되도록 하기 위해

    # 착륙 명령을 보내기 전에 뒤로 이동이 완료되도록 5초 대기
    await asyncio.sleep(5)

    # 드론 착륙
    print("드론 착륙 중...")
    await drone.action.land()

async def move(drone, new_lat, new_lon, current_alt):
    # 드론 이동 명령 보내기
    await drone.action.goto_location(new_lat, new_lon, current_alt, yaw_deg=0)

    # 고도 모니터링 및 안전 거리 조절
    async for position in drone.telemetry.position():
        current_alt = position.absolute_altitude_m
        # 현재 고도가 안전 거리보다 작을 경우 고도 조정
        if current_alt < MIN_SAFE_DISTANCE:
            print("고도를 조정하여 안전 거리를 유지합니다.")
            await drone.action.goto_location(new_lat, new_lon, current_alt + MIN_SAFE_DISTANCE, yaw_deg=0)
        break  # 한 번만 실행되도록 하기 위해

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
