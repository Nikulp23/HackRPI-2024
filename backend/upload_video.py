from flask import Blueprint, request, jsonify, make_response
import os
import numpy as np
import cv2
import requests
from io import BytesIO
import matplotlib.pyplot as plt


upload_video = Blueprint('upload_video', __name__)

@upload_video.route('/upload-video', methods=['POST'])
def upload_image():
   print(request.files)
   if 'video' not in request.files:
      return jsonify({"error": "No video file provided"}), 400

   file = request.files['video']
   if file.filename == '':
      return jsonify({"error": "No selected video"}), 400

   if not allowed_file(file.filename):
      return jsonify({"error": "Invalid file type"}), 400




   # return jsonify({
   #    "croppedCoordinates": croppedCoordinates,
   #    "image": base64_image  # Image as base64 string
   # }), 200

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


