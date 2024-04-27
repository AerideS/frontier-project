'''
참고 블로그
: https://justkode.kr/python/flask-restapi-1/
: https://justkode.kr/python/flask-restapi-2/
'''

from flask import Flask
from flask_restx import Resource, Api
# from todo import Todo
from waypoint_data import Waypoint

app = Flask(__name__)
api = Api(
    app,
    version='0.1',
    title="frontier's API Server",
    description="frontier's Todo API Server!",
    terms_url="/",
    contact="frontier@gmail.com",
    license="MIT"
)

api.add_namespace(Waypoint, '/waypoint')
# api.add_namespace(Todo, '/todos')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)