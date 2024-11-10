from flask import Blueprint, request, jsonify, send_file
import os
import cv2
from werkzeug.utils import secure_filename
from moviepy.editor import ImageSequenceClip
from PIL import Image
import uuid

upload_video = Blueprint('upload_video', __name__)

@upload_video.route('/upload-video', methods=['POST'])
def video():
    # Validate
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected video"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    # Save local
    filename = secure_filename(file.filename)
    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)
    video_path = os.path.join(upload_folder, filename)
    file.save(video_path)

    try:
        # Process the video
        processed_video_path = process_video(video_path)
        return send_file(processed_video_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_video(video_path):
    # Create a folder to store frames
    frame_folder = os.path.join('processed_frames', str(uuid.uuid4()))
    os.makedirs(frame_folder, exist_ok=True)

    # Read the video
    video_capture = cv2.VideoCapture(video_path)
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    
    if fps <= 0:
        raise ValueError("Invalid FPS detected in the video.")

    frames_to_skip = fps * 2  # 2 seconds worth of frames
    success = True
    frame_list = []
    frame_count = 0

    while success:
        success, frame = video_capture.read()
        if not success or frame is None:
            break

        if frame_count % frames_to_skip == 0:
            # Save the frame as an image
            frame_filename = os.path.join(frame_folder, f'frame_{frame_count}.png')
            cv2.imwrite(frame_filename, frame)
            frame_list.append(frame_filename)
        
        frame_count += 1

    video_capture.release()

    if not frame_list:
        raise ValueError("No valid frames were extracted from the video.")

    # extend frames for 2 seconds each
    modified_frames = []
    for frame_path in frame_list:
        img = Image.open(frame_path).convert("L")  # Testing by switching them to grey
        modified_frame_path = frame_path.replace('frame_', 'modified_')
        img.save(modified_frame_path)
        
        # Repeat frame to last for 2 seconds
        modified_frames.extend([modified_frame_path] * (fps * 2))  # 2 seconds at original fps

    if not modified_frames:
        raise ValueError("No modified frames available for video creation.")

    # Combine the extended frames back into a video
    output_video_path = os.path.join('processed_videos', f'output_{uuid.uuid4().hex}.mp4')
    os.makedirs('processed_videos', exist_ok=True)
    
    for frame_path in modified_frames:
        if not os.path.exists(frame_path):
            raise FileNotFoundError(f"Frame not found: {frame_path}")

    clip = ImageSequenceClip(modified_frames, fps=fps)
    clip.write_videofile(output_video_path, codec='libx264')

    return output_video_path

