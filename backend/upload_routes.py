from flask import Blueprint, request, jsonify, send_file
import os

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

   # TEMPORARY - Return same image back
   return send_file(file_path, mimetype='image/jpeg')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
