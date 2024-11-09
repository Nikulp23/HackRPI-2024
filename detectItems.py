import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

draw_on_removed_background = False  # Set to False to draw on the original image

# Load the image
image_path = './test.png'
img = cv2.imread(image_path)

if img is None:
    print("Error: Image not found or unable to load.")
    exit()

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

# Invert mask fr foreground
mask_inv = cv2.bitwise_not(mask)

# Apply the mask to the image to get the foreground
img_foreground = cv2.bitwise_and(img, img, mask=mask_inv)

if draw_on_removed_background:
    img_draw = cv2.cvtColor(img_foreground, cv2.COLOR_BGR2BGRA)

    alpha_channel = np.ones(mask_inv.shape, dtype=mask_inv.dtype) * 255  
    alpha_channel[mask_inv == 0] = 0  
    img_draw[:, :, 3] = alpha_channel
else:
    img_draw = img.copy()

# Output cropped images
output_folder = 'cropped_objects'
os.makedirs(output_folder, exist_ok=True)

contours, hierarchy = cv2.findContours(
    mask_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
)

rectangle_color = (0, 255, 0)  
rectangle_thickness = 4 

object_counter = 0

# Draw bounding rectangles 
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area > 500:  
        x, y, w, h = cv2.boundingRect(cnt)
        if draw_on_removed_background:
            cv2.rectangle(img_draw, (x, y), (x + w, y + h), (0, 255, 0, 255), rectangle_thickness)
            cropped_object = img_draw[y:y+h, x:x+w]
        else:
            cv2.rectangle(img_draw, (x, y), (x + w, y + h), rectangle_color, rectangle_thickness)
            cropped_object = img[y:y+h, x:x+w]

        object_filename = f'object_{object_counter}.png'
        object_path = os.path.join(output_folder, object_filename)
        cv2.imwrite(object_path, cropped_object)
        object_counter += 1

if draw_on_removed_background:
    cv2.imwrite('output_image_with_boxes.png', img_draw)
else:
    cv2.imwrite('output_image_with_boxes.png', img_draw)

if draw_on_removed_background:
    img_display = cv2.cvtColor(img_draw, cv2.COLOR_BGRA2RGBA)
else:
    img_display = cv2.cvtColor(img_draw, cv2.COLOR_BGR2RGB)

plt.imshow(img_display)
plt.axis('off')
plt.title('Objects with Bounding Boxes')
plt.show()

print(f"Saved {object_counter} objects to the '{output_folder}' folder.")
