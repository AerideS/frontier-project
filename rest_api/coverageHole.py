from flask import request
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

@Holes.route('', methods=['POST'])
class DeviceInfo(Resource):
    '''
    전체 device에 대한 정보
    '''
    def get(self):
        data = request.get_json()
        
        gcs_lat = data.get('gcs_lat')
        gcs_lng = data.get('gcs_lng')
        gcs_alt = data.get('gcs_alt')
        flight_alt = data.get('flight_alt')
        distance = data.get('distance')
        
        if LAT_MIN <= gcs_lat <= LAT_MAX and LNG_MIN <= gcs_lng <= LNG_MAX:
                    
            result = getPolygone(gcs_lat, gcs_lng, gcs_alt, 1, flight_alt, distance)
            
            return {'result' : result}
        else:
            return {'error' : "point out of range"}

