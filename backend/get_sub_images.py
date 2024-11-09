from flask import Blueprint, request, jsonify, send_file
from PIL import Image
import os
import uuid
import json


get_sub_images = Blueprint('get_sub_images', __name__)

SUB_UPLOAD_FOLDER = 'sub-uploads'
if not os.path.exists(SUB_UPLOAD_FOLDER):
   os.makedirs(SUB_UPLOAD_FOLDER)


@get_sub_images.route('/get-sub-images', methods=['POST'])
def getSubImages():
   # Verify file
   if 'image' not in request.files:
      return jsonify({"error": "No file part"}), 400

   file = request.files['image']
   if file.filename == '':
      return jsonify({"error": "No selected file"}), 400

   # Verify and parse coordinates
   try:
      coordinates = request.form.get('coordinates')
      if not coordinates:
         return jsonify({"error": "No coordinates provided"}), 400
      coordinates = json.loads(coordinates)
   except Exception as e:
      return jsonify({"error": f"Invalid coordinates format: {str(e)}"}), 400

   image = Image.open(file)
   cropped_images = []


   # Process coordinates and crop images
   for key, coord in coordinates.items():
      x, y, width, height = coord['x'], coord['y'], coord['width'], coord['height']
      cropped_image = image.crop((x, y, x + width, y + height))
      # Temporarily storing into the subfolder to see what is saved
      cropped_filename = os.path.join(SUB_UPLOAD_FOLDER, f'crop_{key}_{uuid.uuid4().hex}.png')
      cropped_image.save(cropped_filename)
      cropped_images.append(cropped_filename)

      #TO DO 
      # 1. Call Firebase to convert each image into a link
      # 2. Pass each link into the callChat endpoint
      # 3. Return data to frontend

   return "success", 200



def allowed_file(filename):
   ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS