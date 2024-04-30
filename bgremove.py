import cv2
import numpy as np
import time
import subprocess
import os
from flask import send_file

# Function to remove background using pixel value difference
def remove_background_mask(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply median blur to the grayscale image to remove noise
    # median blur preserves edges
    blurred = cv2.medianBlur(gray, 11)

    # Perform edge detection
    edges = cv2.Canny(blurred, 10, 40)

    # Perform dilation and erosion to close gaps in between object edges
    dilated = cv2.dilate(edges, None, iterations=2)
    eroded = cv2.erode(dilated, None, iterations=2)

    # Find contours in the eroded image
    contours, _ = cv2.findContours(eroded.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw the contours on a mask
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, contours, -1, (255), -1)

    mask = cv2.erode(mask, None, iterations=2)

    return mask

def remove_greenscreen(frame):
    lower_green = np.array([0, 0, 80])
    upper_green = np.array([360, 50, 255])
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the green color
    mask = cv2.bitwise_not(cv2.inRange(hsv, lower_green, upper_green))

    return mask

def clear_folder():
    try:
        for filename in os.listdir("output"):
            file_path = os.path.join("output", filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return "Folder cleared successfully"
    except Exception as e:
        return str(e), 500

def process_video(video_path, image_path, mode):
    clear_folder()
    try:
        bg = cv2.imread(image_path)
    except:
        bg = None
    # Open the video file
    cap = cv2.VideoCapture(video_path)


    # Resizing the background image
    if(bg is not None):
        bg = cv2.resize(bg, (int(cap.get(3)), int(cap.get(4))))
    # Check if the video file opened successfully
    if not cap.isOpened():
        print("Error: Could not open video file.")
        exit()


    # Read until the end of the video
    c = 0
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()

        # If frame is read correctly ret is True
        if not ret:
            break

        if(mode == 0):
            mask = remove_background_mask(frame)
        else:
            mask = remove_greenscreen(frame)

        mask_inv = cv2.bitwise_not(mask)
        # Extract the foreground
        foreground = cv2.bitwise_and(frame, frame, mask=mask)

        # Extract the background
        if(bg is not None):
            background = cv2.bitwise_and(bg, bg, mask=mask_inv)
        else:
            background = np.zeros_like(foreground)

        # Combine foreground and background
        superimposed_image = cv2.add(background, foreground)
        current_timestamp = int(time.time_ns())
        # Display the resulting frame
        cv2.imwrite(filename=f"output/{current_timestamp}.png", img=superimposed_image)
        c = c+1
    # Release the video capture object
    cap.release()
    # Path to the folder containing frames
    frames_folder = 'output/'
    # Output video path
    output_video_path = 'output_video.mp4'
    # Create the video from frames
    create_video(frames_folder, output_video_path)
    return send_file(output_video_path, mimetype="video/mp4")



# Function to create a video from frames
def create_video(frames_folder, output_video_path, fps=30):
    # Get the list of frames
    frame_files = [f for f in os.listdir(frames_folder) if os.path.isfile(os.path.join(frames_folder, f))]
    frame_files.sort()

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'H264')  # Change codec as needed (e.g., 'XVID', 'mp4v', 'MJPG')
    frame = cv2.imread(os.path.join(frames_folder, frame_files[0]))
    height, width, _ = frame.shape
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))


    # Write frames to the video
    for filename in frame_files:
        img = cv2.imread(os.path.join(frames_folder, filename),1)
        out.write(img)

    # Release the VideoWriter
    out.release()
    print("Video created successfully!")
    

