from pymongo import MongoClient 
from flask import Flask, render_template, jsonify

# MongoDB connection
client = MongoClient('mongodb://203.255.57.122:27018/')
db = client['drone_data1']
collection = db['drone_data']

# Flask app setup
app = Flask(__name__)

# Route to fetch data from MongoDB and render it in an HTML template
@app.route("/")  
def root():
    data = collection.find_one({'drone_id': 'drone1'})
    data_copy = data.copy()
    data_copy.pop('_id')  # ObjectId 필드 제거
    return jsonify(data_copy)

# Run the Flask app
if __name__ == '__main__':
    app.run(host="127.0.0.1", port="8080", debug=True)
