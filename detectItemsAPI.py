import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import requests
from io import BytesIO

draw_on_removed_background = False  # Set to False to draw on the original image

# Load the original image
image_path = './test1.png'
imgFirst = cv2.imread(image_path)

if imgFirst is None:
    print("Error: Image not found or unable to load.")
    exit()

_, img_encoded = cv2.imencode('.png', imgFirst)

# Background removal using the remove.bg API
response = requests.post(
    'https://api.remove.bg/v1.0/removebg',
    files={'image_file': BytesIO(img_encoded.tobytes())},
    data={'size': 'auto'},
    headers={'X-Api-Key': '6w8VGP3e7P1as9hySLpBrGP2'},  # Replace with your API key
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
output_folder = 'cropped_objects'
os.makedirs(output_folder, exist_ok=True)

rectangle_color = (0, 255, 0)  # Green color for bounding box
rectangle_thickness = 4

object_counter = 0

# Draw bounding rectangles and crop objects
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area > 6000:  # Ignore small contours
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Draw rectangles on the original image
        cv2.rectangle(img_draw, (x, y), (x + w, y + h), rectangle_color, rectangle_thickness)
        
        # Crop the object from the original image
        cropped_object = imgFirst[y:y+h, x:x+w]

        object_filename = f'object_{object_counter}.png'
        object_path = os.path.join(output_folder, object_filename)
        cv2.imwrite(object_path, cropped_object)
        object_counter += 1

# Save and display the final image with bounding boxes
output_image_path = 'output_image_with_boxes.png'
cv2.imwrite(output_image_path, img_draw)

# Display the final image
img_display = cv2.cvtColor(img_draw, cv2.COLOR_BGR2RGB)
plt.imshow(img_display)
plt.axis('off')
plt.title('Objects with Bounding Boxes')
plt.show()

print(f"Saved {object_counter} objects to the '{output_folder}' folder.")
