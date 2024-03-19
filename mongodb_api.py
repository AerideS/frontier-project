from pymongo import MongoClient 

class DroneData:
    def __init__(self) -> None:
        client = MongoClient('mongodb://localhost:27017/')  # MongoDB 클라이언트를 생성하고 로컬 호스트의 기본 포트로 연결
        self.db = client['drone_data']  # 'drone_data'라는 데이터베이스를 선택

    # 새로운 장치 데이터를 추가하거나 기존 장치의 고도를 업데이트하는 함수를 정의
    def add_device_data(self, device_type, longitude, latitude, altitude):
        collection_name = device_type.lower() + '_data'  # 컬렉션 이름을 장치 타입에 따라 생성..
        collection = self.db[collection_name]  # 선택한 데이터베이스에서 해당 이름의 컬렉션을 선택..
        existing_data = collection.find_one({'longitude': longitude, 'latitude': latitude})  # 주어진 경도와 위도로 이미 존재하는 데이터를 조회
        if existing_data:  # 이미 데이터가 존재할 경우
            collection.update_one({'_id': existing_data['_id']}, {'$set': {'altitude': altitude}})  # 해당 데이터의 고도를 업데이트
        else:  # 데이터가 존재하지 않을 경우
            collection.insert_one({'longitude': longitude, 'latitude': latitude, 'altitude': altitude})  # 새로운 데이터를 추가

    # 주어진 장치 타입, 경도, 위도에 해당하는 장치 데이터를 가져오는 함수를 정의.
    def get_device_data(self, device_type, longitude, latitude):
        collection_name = device_type.lower() + '_data'  # 컬렉션 이름을 장치 타입에 따라 생성
        collection = self.db[collection_name]  # 선택한 데이터베이스에서 해당 이름의 컬렉션을 선택
        data = collection.find_one({'longitude': longitude, 'latitude': latitude})  # 주어진 경도와 위도로 데이터를 조회
        return data  # 조회된 데이터를 반환.

    # 장치 데이터의 고도를 업데이트하는 함수를 정의. 실제로는 add_device 함수를 호출하여 고도를 업데이트
    def update_device_data(self, device_type, longitude, latitude, altitude):
        self.add_device_data(device_type, longitude, latitude, altitude)  # add_device 함수를 호출하여 장치 데이터를 업데이트

class TerrainData:
    def __init__(self) -> None:
        client = MongoClient('mongodb://localhost:27017/')  # MongoDB 클라이언트를 생성하고 로컬 호스트의 기본 포트로 연결
        self.db = client['terrain_data']  # 'drone_data'라는 데이터베이스를 선택

    def _checkExist(longitude, latitude):
        pass

    def addHeight(longitude, latitude, altitude):
        pass

    def getHeight(longitude, latitude):
        pass

    def addLos(longitude, latitude, losElev):
        pass
    
    def getLos(longitude, latitude):
        pass

    if __name__ == '__main__':  # 스크립트가 단독으로 실행될 때만 아래 코드를 실행
        #app.run(debug=False)  # Flask 애플리케이션을 실행. 디버그 모드는 비활성화됩니다
        drone_data = DroneData()
        drone_data.add_device('drone', 40.7128, -74.0060, 100)  # 예시파일 New York City의 고도 100m로 설정
        drone_data.add_device('drone', 40.7128, -74.0060, 150)  # 예시파일 New York Citys의 고도 150m로 설정
        drone_data.add_device('drone', 34.0522, -118.2437, 150)  # 예시파일 Los Angeles의 고도 150m로 설정
        # 이상적인 예시 첫번쨰 New York City의 고도는 100m인데 두번째 코드로 인해 고도는 150m로 업로드 되서 첫번째 예시는 사라진다. 세번쨰 예시는 위도 경도가 나오니 출력


