from flask import request
from flask_restx import Resource, Api, Namespace

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from mongodb_api import Waypoints
from mqapi import MqSender

Missions  = Namespace(
    name="Missions",
    description="APIs for getting and updating data of Missions",
)

waypoint_list = Waypoints()
sender = MqSender()

@Missions.route('/<string:device_id>')
class MissionsInfoSpec(Resource):
    def put(self, device_id):
        for single_message in waypoint_list.getWayPointList():
            if 'type' not in single_message:
                continue
            
            if single_message['type'] == 'arm':
                sender.arm()
            elif single_message['type'] == 'takeoff':
                sender.takeoff(single_message['altitude'])
            elif single_message['type'] == 'move':
                sender.goto(single_message['latitude'], single_message['longitude'])
            elif single_message['type'] == 'drop':
                sender.startDrop(single_message['latitude'], single_message['longitude'])
            elif single_message['type'] == 'land':
                sender.land()
            else:
                return {'error' : "unidentifided mission type"} 