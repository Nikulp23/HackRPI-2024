from flask import Blueprint, request, jsonify, send_file
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import requests

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
   
   # nikul code
   # ORIGINAL MATTEO IMAGE
   imgUrl = "image1.jpg"

   # Background removal using the remove.bg API (commented out for now)
   response = requests.post(
      'https://api.remove.bg/v1.0/removebg',
      files={'image_file': open(imgUrl, 'rb')},
      data={'size': 'auto'},
      headers={'X-Api-Key': '6w8VGP3e7P1as9hySLpBrGP2'},
   )
   if response.status_code == requests.codes.ok:
      with open('no-bg.png', 'wb') as out:
         out.write(response.content)
   else:
      print("Error:", response.status_code, response.text)
      exit()

   # Load the background-removed image with alpha channel
   image_path = 'no-bg.png'
   img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
   original_img = cv2.imread(imgUrl)  # Load the original image for drawing

   if img is None or original_img is None:
      print("Error: Image not found or unable to load.")
      exit()

   # Create a red background of the same size as the image
   height, width = img.shape[:2]
   red_background = np.full((height, width, 3), (0, 0, 255), dtype=np.uint8)  # Red background (BGR format)

   # Blend the foreground with the red background if alpha channel exists
   if img.shape[2] == 4:  # Check if the image has an alpha channel
      alpha_channel = img[:, :, 3] / 255.0
      for c in range(3):  # Apply alpha blending for each color channel
         red_background[:, :, c] = (1.0 - alpha_channel) * red_background[:, :, c] + alpha_channel * img[:, :, c]
   else:
      red_background = img

   # Use red_background in further processing
   img_foreground = red_background

   # Convert to HSV for color-based segmentation
   hsv = cv2.cvtColor(img_foreground, cv2.COLOR_BGR2HSV)
   bg_color = hsv[0, 0]  # Assume the background color is at the top-left corner

   # Define thresholds for background mask
   sensitivity = 30
   lower_thresh = np.clip(bg_color - np.array([sensitivity, 100, 100]), 0, 255)
   upper_thresh = np.clip(bg_color + np.array([sensitivity, 255, 255]), 0, 255)

   # Create and invert mask
   mask = cv2.inRange(hsv, lower_thresh, upper_thresh)
   mask_inv = cv2.bitwise_not(mask)

   # Find contours in the inverted mask
   contours, _ = cv2.findContours(mask_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

   # Collect bounding boxes from contours
   boxes = []
   for cnt in contours:
      area = cv2.contourArea(cnt)
      if area > 500:  # Ignore smaller contours
         x, y, w, h = cv2.boundingRect(cnt)
         boxes.append([x, y, w, h])

   # Non-Maximum Suppression (NMS) function to filter overlapping boxes
   def non_max_suppression(boxes, overlap_thresh=0.3):
      if len(boxes) == 0:
         return []
      
      boxes = np.array(boxes)
      pick = []

      x1 = boxes[:, 0]
      y1 = boxes[:, 1]
      x2 = boxes[:, 0] + boxes[:, 2]
      y2 = boxes[:, 1] + boxes[:, 3]

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

   # Apply NMS to the bounding boxes
   nms_boxes = non_max_suppression(boxes, overlap_thresh=0.3)

   # Save bounding boxes in a dictionary and draw on the original image
   bounding_boxes = {}
   for i, (x, y, w, h) in enumerate(nms_boxes):
      bounding_boxes[i] = {"x": x, "y": y, "width": w, "height": h}
      # Draw each bounding box on the original image
      cv2.rectangle(original_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

   # Save and display the final image with bounding boxes on the original image
   output_path = 'output_image_with_bounding_boxes_on_original.png'
   cv2.imwrite(output_path, original_img)

   # Display the original image with bounding boxes
   img_display = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
   plt.imshow(img_display)
   plt.axis('off')
   plt.title('Original Image with Bounding Boxes')
   plt.show()

   filename = file.filename
   file_path = os.path.join(UPLOAD_FOLDER, filename)
   file.save(file_path)

   print(bounding_boxes)
   # return bounding_boxes, send_file(img_display)

   # TEMPORARY - Return same image back
   return bounding_boxes, send_file(file_path, mimetype='image/jpeg')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
