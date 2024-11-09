from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import matplotlib.pyplot as plt
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/get-data', methods=['GET'])
def get_data():
    data = {"message": "This is a GET response from Flask!"}
    return jsonify(data), 200

@app.route('/recognizeObjects', methods=['POST'])
def post_data():

    # get image from frontend
    data = request.get_json()

    



    # covert to coordinates
    objects = [
        {"object": "ExampleObject1", "x": 50, "y": 100, "width": 150, "height": 200},
        {"object": "ExampleObject2", "x": 200, "y": 300, "width": 100, "height": 150}
    ]

    response = {"received_data": objects}
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)
