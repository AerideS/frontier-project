from pymongo import MongoClient 
from flask import Flask, render_template, jsonify
from flask_cors import CORS

# MongoDB connection
client = MongoClient('mongodb://203.255.57.122:27018/')
db = client['drone_data1']
collection = db['drone_data']

# Flask app setupls
app = Flask(__name__)
CORS(app)  # 모든 엔드포인트에 CORS를 활성화합니다.

# Route to fetch data from MongoDB and render it in an HTML template
@app.route("/", methods=['GET', 'POST'])  
def root():
    data = collection.find_one({'drone_id': 'drone1'})
    data_copy = data.copy()
    data_copy.pop('_id')  # ObjectId 필드 제거
    return jsonify(data_copy)

# Run the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)

