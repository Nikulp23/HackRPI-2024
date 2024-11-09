from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/get-data', methods=['GET'])
def get_data():
    data = {"message": "This is a GET response from Flask!"}
    return jsonify(data), 200

@app.route('/post-data', methods=['POST'])
def post_data():
    data = request.get_json()
    response = {"message": "Data received", "received_data": data}
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)
