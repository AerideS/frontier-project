# app.py
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import requests, json
import mqapi

#Flask 객체 인스턴스 생성
app = Flask(__name__)
CORS(app)

## 상수 정의부
REST_IP_DEVICE = 'http://203.255.57.136:5001/device'
REST_IP_WAYPOINT = 'http://203.255.57.136:5001/waypoint'
REST_IP_HOLE = 'http://203.255.57.136:5001/hole'

WP_TYPE_MOVE = 0
WP_TYPE_DROP_AP = 1

# 선택 디바이스 전역 저장
selectDevice = 'NONE'

@app.route('/', methods=['GET', 'POST'])
def main():
  return render_template('main.html')

# service 최초 접속
@app.route('/service', methods=['GET']) 
def service_get():
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
  
@app.route('/submit', methods=['POST']) 
def submit_command():
  data = request.json
  hash = data['hash']
  print(hash)
  if hash == 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3':
    print('permission accepted')
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


