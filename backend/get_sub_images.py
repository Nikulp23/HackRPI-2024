from flask import Blueprint, request, jsonify, send_file
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import firebase_admin
from firebase_admin import credentials, storage
from io import BytesIO
import os
import uuid
import json
from chatOutput import chat_output_route

from dotenv import load_dotenv  

load_dotenv()

storage_bucket_name = os.getenv('FIREBASE_STORAGE_BUCKET')

cred = credentials.Certificate("./service-account.json")
firebase_admin.initialize_app(cred, {
   'storageBucket': storage_bucket_name
})

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

   original_image_bytes = file.read()
   cropped_images_urls = []


   # Find sub images and upload synchronously 
   with ThreadPoolExecutor() as executor:
      futures = [
         executor.submit(process_and_upload, original_image_bytes, coord, key)
         for key, coord in coordinates.items()
      ]
      for future in futures:
         cropped_images_urls.append(future.result())

   # TEMPORARY LIMIT OF PROCESSING ONLY 2 ITEMS TO SAVE GPT $
   with ThreadPoolExecutor() as executor:
      api_futures = [
         executor.submit(chat_output_route, image_url)
         for image_url in cropped_images_urls
      ]

      results = [future.result() for future in as_completed(api_futures)]

   print(results)
   return jsonify({"message": "success", "results": results}), 200



def allowed_file(filename):
   ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_firebase(file_obj, filename):
   bucket = storage.bucket()
   blob = bucket.blob(filename)
   
   blob.upload_from_file(file_obj, content_type='image/png')
   blob.make_public() 
   
   return blob.public_url

def process_and_upload(original_image_bytes, coord, key):
   # Reload image for each thread
   image = Image.open(BytesIO(original_image_bytes))

   x, y, width, height = coord['x'], coord['y'], coord['width'], coord['height']
   cropped_image = image.crop((x, y, x + width, y + height))

   in_memory_cropped_image = BytesIO()
   cropped_image.save(in_memory_cropped_image, format='PNG')
   in_memory_cropped_image.seek(0)

   firebase_filename = f'cropped_images/{uuid.uuid4().hex}.png'
   return upload_to_firebase(in_memory_cropped_image, firebase_filename)


# def call_chat_output(image_url):
#    return chat_output_route(image_url)
   #  """Calls the chatOutput API with the image URL."""
   #  try:
   #      response = requests.post('http://localhost:5000/api/chatOutput', json={"image_url": image_url})
   #      if response.status_code == 200:
   #          return response.json()
   #      else:
   #          return {"error": f"Failed to get description for {image_url}"}
   #  except Exception as e:
   #      return {"error": f"Exception for {image_url}: {str(e)}"}
