from pymongo import MongoClient 

class DroneData:
    def __init__(self) -> None:
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client['drone_data1']

    def add_device_data(self, drone_id, longitude, latitude, altitude):
        collection_name = 'drone_data'
        collection = self.db[collection_name]
        existing_data = collection.find_one({'drone_id': drone_id})
        if existing_data:
            collection.update_one({'_id': existing_data['_id']}, {'$set': {'longitude': longitude, 'latitude': latitude, 'altitude': altitude}})
        else:
            collection.insert_one({'drone_id': drone_id, 'longitude': longitude, 'latitude': latitude, 'altitude': altitude})

    def get_device_data(self, drone_id):
        collection_name = 'drone_data'
        collection = self.db[collection_name]
        data = collection.find_one({'drone_id': drone_id})
        return data

    def update_device_data(self, drone_id, longitude, latitude, altitude):
        self.add_device_data(drone_id, longitude, latitude, altitude)

class TerrainData:
    def __init__(self) -> None:
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client['terrain_data']
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
    drone_data = DroneData()
    drone_data.add_device_data('drone1', 40.7128, -74.0060, 100)
    drone_data.add_device_data('drone2', 40.7128, -74.0060, 150)
    drone_data.add_device_data('drone3', 34.0522, -118.2437, 150)
