from flask import Flask, request, jsonify
from flask_restx import Resource, Api, Namespace

import os, sys, time
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from mongodb_api import DroneData
from mqapi import MqReceiver
from multiprocessing import Process

device_data = DroneData()

Devices  = Namespace(
    name="Devices",
    description="APIs for getting and updating data of Devices",
)

receiver = MqReceiver("SERVER", "localhost")  # 큐 이름, 서버 주소

def start_receiver():
    message = receiver.get_message()

# 드론 정보 메시지 수신을 담당하는 프로세스 시작
receiver_process = Process(target=start_receiver)
receiver_process.start()


@Devices.route('')
class DeviceInfo(Resource):
    '''
    전체 device에 대한 정보
    '''
    def get(self):
        print(device_data.getDeviceList())
        return {'result' : device_data.getDeviceList()}

@Devices.route('/<string:device_id>')
class DevicesInfoSpec(Resource):
    def get(self, device_id):
        data = device_data.get_device_data(device_id)
        if data is not None:
            return {'result' : data}

    def put(self, device_id):
        data = request.json
        print(data)
        device_data.update_device_data(device_id, data['longitude'], data['latitude'], data['altitude'])
        
        return {'put' : 'success'}
    