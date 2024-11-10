from flask import Blueprint, request, jsonify, send_file
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import requests
import os
import uuid
import json
from PIL import Image

# 6w8VGP3e7P1as9hySLpBrGP2

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

   filename = file.filename
   file_path = os.path.join(UPLOAD_FOLDER, filename)
   file.save(file_path)

   print(filename)
   print(file_path)

   try:
        # Placeholder for background removal using external API if needed
        # Uncomment and use appropriate API settings
        # response = requests.post(
        #     'https://api.remove.bg/v1.0/removebg',
        #     files={'image_file': open(file_path, 'rb')},
        #     data={'size': 'auto'},
        #     headers={'X-Api-Key': 'your_api_key_here'},
        # )
        # if response.status_code == requests.codes.ok:
        #     with open('no-bg.png', 'wb') as out:
        #         out.write(response.content)
        #     image_path = 'no-bg.png'
        # else:
        #     return jsonify({"error": f"Background removal failed: {response.status_code}"}), 500

      image_path = file_path  # Assuming no external API call

      # Load the saved or processed image
      img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
      if img is None:
         return jsonify({"error": "Image not found or unable to load."}), 500

      # Create a red background
      height, width = img.shape[:2]
      red_background = np.full((height, width, 3), (0, 0, 255), dtype=np.uint8)

      # Blend image with red background if alpha channel exists
      if img.shape[2] == 4:
         alpha_channel = img[:, :, 3] / 255.0
         for c in range(3):
               red_background[:, :, c] = (1.0 - alpha_channel) * red_background[:, :, c] + alpha_channel * img[:, :, c]
         img_foreground = red_background
      else:
         img_foreground = img

      # Convert to HSV for color-based segmentation
      hsv = cv2.cvtColor(img_foreground, cv2.COLOR_BGR2HSV)
      bg_color = hsv[0, 0]

      print("typibg")

      # Define thresholds for mask
      sensitivity = 30
      lower_thresh = np.clip(bg_color - np.array([sensitivity, 100, 100]), 0, 255)
      upper_thresh = np.clip(bg_color + np.array([sensitivity, 255, 255]), 0, 255)

      # Create mask and invert it
      mask = cv2.inRange(hsv, lower_thresh, upper_thresh)
      mask_inv = cv2.bitwise_not(mask)

      # Draw bounding boxes
      contours, _ = cv2.findContours(mask_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      boxes = []
      for cnt in contours:
         area = cv2.contourArea(cnt)
         if area > 500:  # Filter by size
               x, y, w, h = cv2.boundingRect(cnt)
               boxes.append([x, y, w, h])

      # Apply Non-Maximum Suppression (NMS) to filter overlapping boxes
      def non_max_suppression(boxes, overlap_thresh=0.3):
         if len(boxes) == 0:
               return []
         boxes = np.array(boxes)
         pick = []
         x1, y1 = boxes[:, 0], boxes[:, 1]
         x2, y2 = boxes[:, 0] + boxes[:, 2], boxes[:, 1] + boxes[:, 3]
         area = (x2 - x1 + 1) * (y2 - y1 + 1)
         idxs = np.argsort(y2)

         while len(idxs) > 0:
               last = len(idxs) - 1
               i = idxs[last]
               pick.append(i)
               xx1 = np.maximum(x1[i], x1[idxs[:last]])
               yy1 = np.maximum(y1[i], y1[idxs[:last]])
               xx2 = np.minimum(x2[i], x2[idxs[:last]])
               yy2 = np.minimum(y2[i], y2[idxs[:last]])

               w = np.maximum(0, xx2 - xx1 + 1)
               h = np.maximum(0, yy2 - yy1 + 1)
               overlap = (w * h) / area[idxs[:last]]
               idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlap_thresh)[0])))

         return boxes[pick].astype("int")
      

      try:
         # Get filtered bounding boxes
         nms_boxes = non_max_suppression(boxes)
         bounding_boxes = [{"x": x, "y": y, "width": w, "height": h} for x, y, w, h in nms_boxes]
         output = json.loads(bounding_boxes)
         print(output)
         return jsonify(output)
      except Exception as e:
         return jsonify({"error": str(e)}), 500

      # Save the processed image with bounding boxes drawn
      # output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_image_with_red_background.png')
      # for (x, y, w, h) in nms_boxes:
      #    cv2.rectangle(img_foreground, (x, y), (x + w, y + h), (0, 255, 0), 2)
      # cv2.imwrite(output_path, img_foreground)

      # return jsonify({ "hello": bounding_boxes })

      # Return bounding boxes in response
      # return jsonify({
      #    "status": "success",
      #    "message": "Image processed and bounding boxes created.",
      #    "bounding_boxes": bounding_boxes
      # })

      # return jsonify({ "hello": "please" })

   except Exception as e:
      return jsonify({"error": str(e)}), 500
   
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
