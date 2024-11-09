import cv2
import numpy as np
import matplotlib.pyplot as plt
import requests

imgUrl = "image1.jpg"

def DOES_SOME_SHIT(OriginalimgUrl):

    # Background removal using the remove.bg API
    # response = requests.post(
    #     'https://api.remove.bg/v1.0/removebg',
    #     files={'image_file': open(OriginalimgUrl, 'rb')},
    #     data={'size': 'auto'},
    #     headers={'X-Api-Key': '6w8VGP3e7P1as9hySLpBrGP2'},
    # )
    # if response.status_code == requests.codes.ok:
    #     with open('no-bg.png', 'wb') as out:
    #         out.write(response.content)
    # else:
    #     print("Error:", response.status_code, response.text)
    #     exit()

    # # Set this flag to control drawing on removed background or original
    draw_on_removed_background = False

    # Load the background-removed image with alpha channel
    image_path = 'no-bg.png'
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    if img is None:
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

    # Prepare image for drawing bounding boxes
    if draw_on_removed_background:
        img_draw = cv2.cvtColor(img_foreground, cv2.COLOR_BGR2BGRA)
    else:
        img_draw = img_foreground

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

    # Save bounding boxes in a dictionary
    bounding_boxes = {}
    for i, (x, y, w, h) in enumerate(nms_boxes):
        bounding_boxes[i] = {"x": x, "y": y, "width": w, "height": h}
        # Draw each bounding box on the original image
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Draw the resulting bounding boxes
    rectangle_color = (0, 255, 0)  # Green color for bounding box
    for (x, y, w, h) in nms_boxes:
        cv2.rectangle(img_draw, (x, y), (x + w, y + h), rectangle_color, 2)

    # Save and display the final image
    output_path = 'output_image_with_red_background.png'
    cv2.imwrite(output_path, img_draw)

    # Display the image with bounding boxes
    img_display = cv2.cvtColor(img_draw, cv2.COLOR_BGRA2RGBA)
    plt.imshow(img_display)
    plt.axis('off')
    plt.title('Objects with Bounding Boxes on Red Background')
    plt.show()

    return bounding_boxes

print(DOES_SOME_SHIT(imgUrl))