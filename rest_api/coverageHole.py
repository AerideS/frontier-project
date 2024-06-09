from flask import request, jsonify
from flask_restx import Resource, Api, Namespace

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from mongodb_api import DroneData
from CoverageHoleCalc import * 

LAT_MIN = 35.14864
LAT_MAX = 35.16801

LNG_MIN = 128.09248
LNG_MAX = 128.09759

Holes = Namespace(
    name="Holes",
    description="APIs for getting data of Holes",
)

@Holes.route('')
class DeviceInfo(Resource):
    '''
    전체 device에 대한 정보
    '''
    def get(self):
        gcs_lat = request.args.get('gcs_lat', type=float)
        gcs_lng = request.args.get('gcs_lng', type=float)
        gcs_alt = request.args.get('gcs_alt', type=float)
        flight_alt = request.args.get('flight_alt', type=float)
        distance = request.args.get('distance', type=int)
        
        result = getPolygone(gcs_lat, gcs_lng, gcs_alt, 1, flight_alt, distance)
        return jsonify({'result': result})
        
#        else:
#            return {'error' : "point out of range"}

