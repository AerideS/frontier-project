# app.py
from flask import Flask, request, render_template

#Flask 객체 인스턴스 생성
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST']) # 접속하는 url
def index():
  return render_template('main.html') 

@app.route('/service', methods=['GET', 'POST'])
def service():
  latitude = request.form['latitude']
  longitude = request.form['longitude']
  altitude = request.form['altitude']
  print("latitude : " + latitude)
  print("longitude : " + longitude)
  print("altitude : " + altitude)
  return render_template('service.html') 


if __name__=="__main__":
  app.run(host="0.0.0.0", port="5000", debug=True)
  # host 등을 직접 지정하고 싶다면
  # app.run(host="127.0.0.1", port="5000", debug=True)