import asyncio
import math
from mavsdk import System

# 두 지점 간의 거리를 계산하는 함수를 정의합니다.
def calculate_distance(lat1, lon1, alt1, lat2, lon2, alt2):
    # 지구의 반지름 (단위: m)
    R = 6371000  
    # 위도 및 경도를 라디안 단위로 변환합니다.
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    # 위도 및 경도 간의 차이를 계산합니다.
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    # Haversine 공식을 사용하여 거리를 계산합니다.
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # 거리를 계산합니다.
    distance = R * c
    # 고도 차이를 추가하여 거리를 계산합니다.
    distance_with_altitude = math.sqrt(distance ** 2 + (alt2 - alt1) ** 2)
    return distance_with_altitude

async def fly_to_location(drone, target_latitude, target_longitude, target_altitude):
    # 드론을 목표 위치로 이동시킵니다.
    await drone.action.goto_location(target_latitude, target_longitude, target_altitude, 0)
    print("목표 위치로 이동 중...")

async def check_arrival(drone, target_latitude, target_longitude, target_altitude):
    async for telemetry_data in drone.telemetry.position():
        # 드론의 현재 위치 데이터를 가져옵니다.
        current_latitude = telemetry_data.latitude_deg
        current_longitude = telemetry_data.longitude_deg
        current_altitude = telemetry_data.absolute_altitude_m

        # 현재 위치와 목표 위치 간의 거리를 계산합니다. 드론의 고도를 고려하여 계산합니다.
        distance_to_target = calculate_distance(current_latitude, current_longitude, current_altitude,
                                                target_latitude, target_longitude, target_altitude)

        # 일정 거리 내에 도착하면 반복문을 종료합니다. 여기서는 1m로 설정합니다.
        if distance_to_target < 1:  
            break

    # 도착 후에 착륙을 호출합니다.
    print("-- 목표 위치에 도착")
    print("-- 착륙 중")
    await drone.action.land()

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

