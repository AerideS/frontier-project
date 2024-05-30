# app.py
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import requests, json
from mqapi import *

#Flask 객체 인스턴스 생성
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 모든 엔드포인트에 CORS를 활성화하고 모든 도메인에서의 접근을 허용

## 상수 정의부
REST_IP_DEVICE = 'http://203.255.57.136:5001/device'
REST_IP_WAYPOINT = 'http://203.255.57.136:5001/waypoint'
REST_IP_HOLE = 'http://203.255.57.136:5001/hole'

WP_TYPE_MOVE = 0
WP_TYPE_DROP_AP = 1

# 선택 디바이스 전역 저장
selectDevice = 'NONE'

# mq 인스턴스 초기화
mqsender = MqSender('203.255.57.136')

@app.route('/', methods=['GET', 'POST'])
def main():
  return render_template('main.html')

# service 최초 접속
@app.route('/service', methods=['GET']) 
def service_get():
  gcs_lat = request.args.get('gcs_lat')
  gcs_lng = request.args.get('gcs_lng')
  gcs_alt = request.args.get('gcs_alt')
  flight_alt = request.args.get('flight_alt')
  distance = request.args.get('distance')
  return render_template('0service_refactoring.html') 

# selectDevice 선택 후 접속
@app.route('/service', methods=['POST'])
def service_post():
  selectDevice = request.form['dropdown']
  return render_template('0service_refactoring.html', selectDevice=selectDevice)

# waypoint 추가 
@app.route('/addWP', methods=['POST'])
def addWP_post():
  payload = request.json
  print(payload)
  requests.post(REST_IP_WAYPOINT, json=payload)
  return render_template('0service_refactoring.html', selectDevice=selectDevice)

@app.route('/editWP', methods=['POST'])
def edit_waypoint():
  # waypoint ID, longitude, latitude 
  data = request.json
  print(data[0])
  response = requests.put(REST_IP_WAYPOINT + '/' + data[0], json=data)
  return render_template('service.html', selectDevice=selectDevice)

@app.route('/deleteWP', methods=['POST'])
def delete_waypoint():
  data = request.json
  response = requests.delete(REST_IP_WAYPOINT + '/' + data['data'][0])
  print(response)
  return render_template('service.html', selectDevice=selectDevice)
  
URL_WP = 'http://203.255.57.136:5001/waypoint'
@app.route('/submit', methods=['POST']) 
def submit_command():
  data = request.json
  hash = data['hash']
  print(hash)
  if hash == 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3':
    print('permission accepted')
    # 여기 코드를 넣을거야.
    response = requests.get(URL_WP)
    json_data = response.json()
    result_data = json_data['result']
    for data in result_data:
      if data['type'] == WP_TYPE_MOVE:
        latitude = data['latitude']
        longitude = data['longitude']
        mqsender.goto(latitude, longitude, 'drone1')
      elif data['type'] == WP_TYPE_DROP_AP:
        mqsender.goto(latitude, longitude, 'drone1')
        mqsender.cutString('drone')


    return jsonify({"status": "accepted"})
  else:
    print('permission denied')
    return jsonify({"status": "denied"})


@app.route('/takeoff', methods=['POST']) 
def takeoff_command():
  data = request.json
  hash = data['hash']
  print(hash)
  if hash == 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3':
    print('permission accepted')
    # debug
    mqsender.takeoff(30, 'drone1')
    return jsonify({"status": "accepted"})
  else:
    print('permission denied')
    return jsonify({"status": "denied"})

@app.route('/land', methods=['POST']) 
def land_command():
  data = request.json
  hash = data['hash']
  print(hash)
  if hash == 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3':
    print('permission accepted')
    # debug
    mqsender.land('drone1')
    return jsonify({"status": "accepted"})
  else:
    print('permission denied')
    return jsonify({"status": "denied"})
  
@app.route('/heater', methods=['POST']) 
def heater_command():
  data = request.json
  hash = data['hash']
  print(hash)
  if hash == 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3':
    print('permission accepted')
    return jsonify({"status": "accepted"})
  else:
    print('permission denied')
    return jsonify({"status": "denied"})

if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=5000)


