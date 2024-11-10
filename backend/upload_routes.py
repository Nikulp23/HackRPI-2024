from flask import Blueprint, request, jsonify, make_response
import os
import numpy as np
import cv2
import requests
from io import BytesIO
import matplotlib.pyplot as plt
import base64


upload_routes = Blueprint('upload_routes', __name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

MAX_CONTENT_LENGTH = 32 * 1024 * 1024  

@upload_routes.route('/upload-image', methods=['POST'])
def upload_image():
   if 'image' not in request.files:
      return jsonify({"error": "No file part"}), 400

   file = request.files['image']
   if file.filename == '':
      return jsonify({"error": "No selected file"}), 400

   if not allowed_file(file.filename):
      return jsonify({"error": "Invalid file type"}), 400

   file_content = file.read()

   # Convert file content to NumPy array
   np_array = np.frombuffer(file_content, np.uint8)

   # Decode the image to the same format as cv2.imread
   imgFirst = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
   _, img_encoded = cv2.imencode('.png', imgFirst)


   # Background removal using the remove.bg API
   response = requests.post(
      'https://api.remove.bg/v1.0/removebg',
      files={'image_file': BytesIO(img_encoded.tobytes())},
      data={'size': 'auto'},
      headers={'X-Api-Key': 'h2DRfrubcCZ8c8UmMyTMPfpV'},  # Replace with your API key
   )

   if response.status_code == requests.codes.ok:
      # Load the returned image directly from the response content
      img = np.asarray(bytearray(response.content), dtype="uint8")
      img = cv2.imdecode(img, cv2.IMREAD_UNCHANGED)  # Includes alpha channel
   else:
      print("Error:", response.status_code, response.text)
      exit()

   # Continue processing with the image returned by the API
   if img is None:
      print("Error: Processed image is invalid.")
      exit()

   # If the image has an alpha channel, replace the transparent background with red
   if img.shape[2] == 4:  # Check for alpha channel
      alpha_channel = img[:, :, 3] / 255.0
      red_background = np.zeros_like(img[:, :, :3], dtype=np.uint8)
      red_background[:, :] = [0, 0, 255]  # Red background in BGR format

      img = (img[:, :, :3] * alpha_channel[:, :, None] + red_background * (1 - alpha_channel[:, :, None])).astype(np.uint8)

   # Convert to HSV for further processing
   hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

   bg_color = hsv[0, 0]

   # Define thresholds 
   sensitivity = 30  # Adjust this value if needed
   lower_thresh = bg_color - np.array([sensitivity, 100, 100])
   upper_thresh = bg_color + np.array([sensitivity, 255, 255])

   # Ensure the thresholds are in valid range
   lower_thresh = np.clip(lower_thresh, 0, 255)
   upper_thresh = np.clip(upper_thresh, 0, 255)

   # Create a mask for the background
   mask = cv2.inRange(hsv, lower_thresh, upper_thresh)

   # Invert mask for foreground
   mask_inv = cv2.bitwise_not(mask)

   # Resize the mask to match the original image dimensions
   mask_inv_resized = cv2.resize(mask_inv, (imgFirst.shape[1], imgFirst.shape[0]))

   # Find contours on the resized mask
   contours, _ = cv2.findContours(
    mask_inv_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
   )

   # Use the original image for drawing bounding boxes
   img_draw = imgFirst.copy()

   # Output cropped images
   croppedCoordinates = {}
   
   rectangle_color = (0, 255, 0)  # Green color for bounding box
   rectangle_thickness = 4

   counter = 0
   for idx, cnt in enumerate(contours):
      area = cv2.contourArea(cnt)
      if area > 6000:  # Ignore small contours
         x, y, w, h = cv2.boundingRect(cnt)
         cv2.rectangle(img_draw, (x, y), (x + w, y + h), rectangle_color, rectangle_thickness)
         
         # Store the bounding box in the desired format
         croppedCoordinates[counter] = {"x": x, "y": y, "width": w, "height": h}
         counter += 1

   # Encode the resulting image to PNG for sending
   _, buffer = cv2.imencode('.png', img_draw)
   base64_image = base64.b64encode(buffer).decode('utf-8')

   return jsonify({
      "croppedCoordinates": croppedCoordinates,
      "image": base64_image  # Image as base64 string
   }), 200

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
