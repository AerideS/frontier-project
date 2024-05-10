from flask import request
from flask_restx import Resource, Api, Namespace

import os
import sys
import json
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from mongodb_api import Waypoints


waypoint_data = Waypoints()

Waypoint  = Namespace(
    name="Waypoints",
    description="APIs for getting and updating data of Waypoints",
)

@Waypoint.route('')
class WaypointInfo(Resource):
    '''
    전체 waypoint에 대한 정보
    '''
    def get(self):
        print(waypoint_data.getWayPointList())
#        for i in range(-100, 300):
#            waypoint_data.delWaypoint(i)
        return {'result' : waypoint_data.getWayPointList()}
    
    def post(self):
        data = request.data
        json_data = json.loads(data)
        print(data)
        print(json_data)
        waypoint_data.addWaypoint(latitude=json_data['latitude'], longitude=json_data['longitude'])
        
        return {'post' : 'success'}

@Waypoint.route('/<int:waypoint_id>')
class WaypointInfoSpec(Resource):
    def get(self, waypoint_id):
        data = waypoint_data.getWaypoint(waypoint_id)
        if data is not None:
            return {'result' : data}

    # 웨이포인트 수정
    def put(self, waypoint_id):
        data = request.json
        id = int(data[0])
        latitude = data[1]
        longitude = data[2]

        print(latitude, longitude)
        print('=============')
        print(data)

        waypoint_data.updateWaypoint(int(id), float(latitude), float(longitude))
        return {'put' : 'success'}
        
    def delete(self, waypoint_id):
        result = waypoint_data.delWaypoint(waypoint_id)
        
        if result:
            return {
                'delete' : 'failed'
            }
        else:
            return {
                'delete' : 'success'
            }

@Waypoint.route('/switch/<int:waypoint_id1>/<int:waypoint_id2>')
class WaypointSwitch(Resource):
    def put(self, waypoint_id1, waypoint_id2):
        waypoint_data.switchWayPoints(waypoint_id1=waypoint_id1, \
            waypoint_id2=waypoint_id2)
        
        return {'result' : {'switch' : 'success'}}
