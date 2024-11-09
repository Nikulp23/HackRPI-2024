from flask import Flask, request, jsonify
from flask_cors import CORS
from upload_routes import upload_routes

app = Flask(__name__)
CORS(app)  # Enable CORS for main app

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

# Register the Blueprint with CORS enabled
app.register_blueprint(upload_routes, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)