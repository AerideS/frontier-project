# app.py
from flask import Flask, request, render_template
from flask_cors import CORS
import requests, json

#Flask 객체 인스턴스 생성
app = Flask(__name__)
CORS(app)

REST_IP_DEVICE = 'http://203.255.57.136:5001/device'
REST_IP_WAYPOINT = 'http://203.255.57.136:5001/waypoint'

@app.route('/', methods=['GET', 'POST']) # 접속하는 url
def index():
  f = open('credential.txt', 'r')
  token = f.readline()
  f.close()
  print(token)
  return render_template('main.html', token = token) 

@app.route('/service', methods=['GET'])
def service_get():
  latitude = request.args.get('latitude')
  longitude = request.args.get('longitude')
  altitude = request.args.get('altitude')

  if (latitude == '' or longitude == '' or altitude == ''):
    return render_template('main.html')
  
  try :
    latitude = float(latitude)
    longitude = float(longitude)
    altitude = float(altitude)

    payload = {'deviceID': 'MASTER', 'latitude': latitude, 'longitude' : longitude, 'altitude' : altitude}
    print(payload)
    response = requests.put(REST_IP_DEVICE + '/MASTER', json=payload)
    #print(response)

    return render_template('service.html') 
  except :
    return render_template('main.html')
@app.route('/service', methods=['POST'])
def service_post():
    data = request.json
    print(data)
    new_point = data.get('newPoint')
    print('수신된 newPoint:', new_point)
    # TO DO : REST API에 전송하기
    payload = {'latitude' : new_point[0], 'longitude' : new_point[1]}
    j_payload = json.dumps(payload)
    print(j_payload)
    response = requests.post(REST_IP_WAYPOINT, j_payload)
    print(response)
    return render_template('service.html') 
    
@app.route('/poc', methods=['GET', 'POST'])
def poc():
  return render_template('poc_realtime_position.html')

@app.route('/table', methods=['GET', 'POST'])
def table():
  return render_template('table_test.html')

if __name__=="__main__":
  app.run(host="0.0.0.0", port="5000", debug=True)
  # host 등을 직접 지정하고 싶다면
  # app.run(host="127.0.0.1", port="5000", debug=True)