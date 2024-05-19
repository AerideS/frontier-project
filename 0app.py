# app.py
from flask import Flask, request, render_template
from flask_cors import CORS
import requests, json

#Flask 객체 인스턴스 생성
app = Flask(__name__)
CORS(app)

## 상수 정의부
REST_IP_DEVICE = 'http://203.255.57.136:5001/device'
REST_IP_WAYPOINT = 'http://203.255.57.136:5001/waypoint'
REST_IP_HOLE = 'http://203.255.57.136:5001/hole'

WP_TYPE_MOVE = 0

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

## debug
# 계산된 폴리곤 가져오기
@app.route('/getPoly', methods=['GET'])
def fetch_polygon():
    lat = 35.16223
    lng = 128.08989
    alt = 1.0    
    distance = 90
    unit = 1

    payload = {'gcs_lat': lat, 'gcs_lng': lng, 'gcs_alt': alt, 'flight_alt': unit, 'distance': distance}
    response = requests.post(REST_IP_HOLE, json=payload)
    print(response)
    return render_template('main.html')



if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=5000)


