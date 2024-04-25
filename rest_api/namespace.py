from flask import Flask
from flask_restx import Namespace, Api, Resource

app = Flask(__name__)
api = Api(app)

namespace = Namespace('hello')  # 첫 번째

@namespace.route('/')
class HelloWorld(Resource):  
    def get(self):
        return {"hello" : "world!"}, 201, {"hi":"hello"}
		
api.add_namespace(namespace, '/hello')  


@api.route('/hello')  # 두 번째
class HelloWorld(Resource):
    def get(self):
        return {"hello" : "world!"}, 201, {"hi":"hello"}