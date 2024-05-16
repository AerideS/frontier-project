from pymongo import MongoClient 

class Waypoints:
    '''
    Mongodb에서 waypoint의 정보를 관리함
    일단은 각각의 waypoint 목록이 아닌 하나의 목록, 하나의 미션 내의 waypoint로 관리함
    
    
    "waypoint" : [
        {
            "waypoint_id" : 1,
            "Type" : move or drop
            "latitude" : 35.12445,
            "longitude" : 126.12345
        }
    ]
    
    '''
    
    def __init__(self) -> None:
        client = MongoClient('mongodb://203.255.57.122:27018/')
        self.db = client['waypointtest']
        self.collection = self.db['waypoints']
        self.waypoint_num = 0 # waypoint의 개수
        
        self.initWaypointNum()
        # print(self.waypoint_num)
        
    def initWaypointNum(self):
        '''
        현재 DB에 몇개의 waypoint가 저장되어 있는지
        waypoint_num에 반영함
        '''
        self.waypoint_num = self.collection.count_documents({})
        
    def getWaypointIDList(self):
        '''
        존재하는 모든 waypoint의 목록 가져옴
        '''
        waypoint_ids = []
        waypoints = self.collection.find({}, {"_id": 0})
        for waypoint in waypoints:
            # print(waypoint)
            waypoint_ids.append(waypoint["waypoint_id"])
 
        return waypoint_ids
    
    def getWayPointList(self):
        '''
        존재하는 모든 waypoint의 정보 가져옴
        '''
        waypoints = self.collection.find({}, {"_id": 0})
        return [waypoint for waypoint in waypoints]
    
    def getWaypoint(self, waypoint_id):
        '''
        waypoint_id에 해당하는 하나의 waypoint 정보 반환 
        '''
        
        return dict(self.collection.find_one({"waypoint_id": waypoint_id}, {"_id": 0}))
    
    def switchWayPoints(self, waypoint_id1, waypoint_id2):
        '''
        DB내에 존재하는 2개의 waypoint에 대해 서로 순서를 바꿈
        '''
        waypoint1 = self.collection.find_one({"waypoint_id": waypoint_id1})
        waypoint2 = self.collection.find_one({"waypoint_id": waypoint_id2})
    
        if waypoint1 and waypoint2:
            temp_type = waypoint1["type"]
            temp_latitude = waypoint1["latitude"]
            temp_longitude = waypoint1["longitude"]
            
            waypoint1["type"]=waypoint2["type"]
            waypoint1["latitude"] = waypoint2["latitude"]
            waypoint1["longitude"] = waypoint2["longitude"]

            waypoint2["type"]= temp_type
            waypoint2["latitude"] = temp_latitude
            waypoint2["longitude"] = temp_longitude          

            self.collection.replace_one({"waypoint_id": waypoint_id1}, waypoint1)
            self.collection.replace_one({"waypoint_id": waypoint_id2}, waypoint2)

    
    def addWaypoint(self, type, latitude, longitude):
        max_id = self.collection.find_one(sort=[("waypoint_id", -1)])  # 현재 가장 큰 waypoint_id를 찾음
        new_waypoint_id = 1 if not max_id else max_id["waypoint_id"] + 1  # 가장 큰 waypoint_id보다 1 큰 값으로 설정
        
        new_waypoint = {
            "waypoint_id": new_waypoint_id,
            "type": type,
            "latitude": latitude,
            "longitude": longitude
        }
        self.collection.insert_one(new_waypoint)
        
        # '''
        # DB에 waypoint 추가
        # 기존에 존재하는 경우에도 ID만 다르게 하여 추가할 수 있음
        # 추가후 waypoint_num의 개수를 1 증가시킴
        # '''
        # new_waypoint_id = self.waypoint_num + 1
        # new_waypoint = {
        #     "waypoint_id": new_waypoint_id,
        #     "latitude": latitude,
        #     "longitude": longitude
        # }
        # self.collection.insert_one(new_waypoint)
        # self.waypoint_num += 1
    
    def updateWaypoint(self, waypoint_id, type, latitude, longitude):
        '''
        기존에 존재하는 waypoint의 타입, 위도, 경도 정보 갱신
        waypoint_id에 해당하는 waypoint를 갱신하며
        존재하지 않는 waypoint_id일 경우에는 아무런 동작도 하지 않음
        '''
        self.collection.update_one({"waypoint_id": waypoint_id}, {"$set": {"type": type, "latitude": latitude, "longitude": longitude}})
    
    def delWaypoint(self, waypoint_id):
        '''
        waypoint_id에 해당하는 waypoint 삭제,
        존재하지 않는 waypoint_id일 경우에는 아무런 동작도 하지 않음
        삭제 후 waypoint_num의 개수를 1 감소시킴
        '''
        self.collection.delete_one({"waypoint_id": waypoint_id})
        self.waypoint_num -= 1
        
        return True

    def clearWaypoint(self):
        '''
        현재 존재하는 모든 waypoint들을 삭제함
        '''
        self.collection.delete_many({})
        self.waypoint_num = 0    
        
        
class DroneData:
    def __init__(self) -> None:
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client['drone_data1test']

    def add_device_data(self, drone_id, longitude, latitude, altitude):
        collection_name = 'drone_data'
        collection = self.db[collection_name]
        existing_data = collection.find_one({'drone_id': drone_id})
        if existing_data:
            collection.update_one({'_id': existing_data['_id']}, {'$set': {'longitude': longitude, 'latitude': latitude, 'altitude': altitude}})
        else:
            collection.insert_one({'drone_id': drone_id, 'longitude': longitude, 'latitude': latitude, 'altitude': altitude})

    def getDeviceList(self):
        '''
        디바이스들의 ID 목록 가져옴
        '''
        collection_name = 'drone_data'
        collection = self.db[collection_name]
        cursor = collection.find()
        
        return [single_name['drone_id'] for single_name in cursor]
        
    def get_device_data(self, drone_id):
        '''
        디바이스 ID에 해당하는 디바이스의 정보를 가져옴
        '''
        collection_name = 'drone_data'
        collection = self.db[collection_name]
        data = collection.find_one({'drone_id': drone_id}, {"_id": 0})
        return data

    def update_device_data(self, drone_id, longitude, latitude, altitude):
        self.add_device_data(drone_id, longitude, latitude, altitude)

class TerrainData:
    def __init__(self) -> None:
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client['terrain_datatest']
        self.collection_name = "terrain_data"
        self.collection = self.db[self.collection_name]

    def _checkExist(self, longitude, latitude):
        existing_data = self.collection.find_one({'longitude': longitude, 'latitude': latitude})
        return existing_data
    
    def addHeight(self, longitude, latitude, altitude):
        existing_data = self._checkExist(longitude, latitude)
        if existing_data:
            self.collection.update_one({'_id': existing_data['_id']}, {'$set': {'elevation': altitude}})
        else:
            self.collection.insert_one({'longitude': longitude, 'latitude': latitude, 'elevation': altitude, 'losAlt': -1})

    def getHeight(self, drone_id):
        drone_data = DroneData()
        drone_info = drone_data.get_device_data(drone_id)
        if drone_info:
            return drone_info.get('altitude')  # 고도를 의미하는 altitude를 반환

    def addLos(self, longitude, latitude, losElev):
        existing_data = self._checkExist(longitude, latitude)
        if existing_data:
            self.collection.update_one({'_id': existing_data['_id']}, {'$set': {'losAlt': losElev}})
        else:
            self.collection.insert_one({'longitude': longitude, 'latitude': latitude, 'elevation': -1, 'losAlt': losElev})

    def getLos(self, drone_id):
        drone_data = DroneData()
        drone_info = drone_data.get_device_data(drone_id)
        if drone_info:
            return drone_info.get('altitude')  # 시야 고도를 의미하는 altitude를 반환
        return None


if __name__ == '__main__':
    # drone_data = DroneData()
    # drone_data.add_device_data('drone1', 40.7128, -74.0060, 100)
    # drone_data.add_device_data('drone2', 40.7128, -74.0060, 150)
    # drone_data.add_device_data('drone3', 34.0522, -118.2437, 150)
    # print(drone_data.getDeviceList())
    # print(drone_data.get_device_data('drone1'))
    # print(drone_data.get_device_data('drone2'))
    # print(drone_data.get_device_data('drone3'))
    waypoint = Waypoints()
    dronedata=DroneData()
    terraindata=TerrainData()
    # waypoint.clearWaypoint()
    # waypoint.addWaypoint("move", 111.111, 222.222)
    # waypoint.addWaypoint("move", 222.222, 222.222)
    # waypoint.addWaypoint("drop", 222.222, 333.333)
    #print('getWaypointIDList :', waypoint.getWaypointIDList())
    #print('getWayPointList :', waypoint.getWayPointList())
    #print('getWaypoint(3) :', waypoint.getWaypoint(3))
    # waypoint.switchWayPoints(1,4)
    # print('switchWayPoints(1,2):', waypoint.getWayPointList())
    # waypoint.updateWaypoint(1, "move", 444.444, 555.555)
    # print('updateWaypoint(1, "move", 444.444, 555.555):', waypoint.getWayPointList())
    # waypoint.delWaypoint(1)
    # print('delWaypoint(1) :', waypoint.getWayPointList())
    # waypoint.clearWaypoint()
    # print('clearWaypoint() :', waypoint.getWayPointList())
    # waypoint.addWaypoint(111.111, 222.222)
    # waypoint.addWaypoint(111.111, 222.222)
    # waypoint.addWaypoint(222.222, 333.333)
    
    # dronedata.add_device_data(2, 111, 222, 333)
    # dronedata.update_device_data(1, 222, 333, 444)
    # print('getDeviceList: ', dronedata.getDeviceList())
    # print('getDeviceList: ', dronedata.get_device_data(2))
    terraindata.addHeight(1,2,3)
    terraindata.addLos(1,2,4)
    print("_checkExist: ", terraindata._checkExist(1,2))
    print("getHeight: ", terraindata.getHeight("drone1"))
    print("getLos: ", terraindata.getLos("drone1"))
    
    # print(waypoint.getWayPointList())
