'''
참고 블로그
: https://justkode.kr/python/flask-restapi-1/
: https://justkode.kr/python/flask-restapi-2/
'''

from flask import Flask
from flask_restx import Resource, Api
from flask_cors import CORS

# from todo import Todo
from waypoint_data import Waypoint
from device_data import Devices
from coverageHole import Holes

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 모든 엔드포인트에 CORS를 활성화하고 모든 도메인에서의 접근을 허용
api = Api(
    app,
    version='0.1',
    title="frontier's API Server",
    description="frontier's REST API Server!",
    terms_url="/",
    contact="frontier@gmail.com",
    license="MIT"
)

api.add_namespace(Waypoint, '/waypoint')
api.add_namespace(Devices, '/device')
api.add_namespace(Holes, '/hole')
# api.add_namespace(Todo, '/todos')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)

