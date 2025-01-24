# Author: Lars Hof
# Date August 2024

import numpy as np
import os
import cv2
import json
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
import math
import subprocess
from scipy.signal import find_peaks 
from scipy.ndimage import gaussian_filter1d
import sys
import random
import time
import matplotlib.ticker as ticker

# Use LaTeX for text rendering (ensure you have LaTeX installed)
# Factors rescale the figures in x and y direction.
facx = 1.75
facy = 1.75
# Configure LaTeX settings
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 24,
    "axes.labelsize": 24,
    "axes.titlesize": 24,
    "legend.fontsize": 24,
    "xtick.labelsize": 24,
    "ytick.labelsize": 24,
    "lines.linewidth": 1,
    "lines.markersize": 3,
    "figure.figsize": (8, 6),  # Adjusted for better aspect ratio
    "axes.grid": True,  # Enable grid
    "grid.alpha": 0.3,  # Grid transparency
    "grid.linestyle": '--'  # Grid style
})
line_styles = [
    "-",      # Solid line
    "--",     # Dashed line
    "-.",     # Dash-dot line
    ":",      # Dotted line
    "solid",  # Solid line (equivalent to "-")
    "dashed", # Dashed line (equivalent to "--")
    "dashdot",# Dash-dot line (equivalent to "-.")
    "dotted", # Dotted line (equivalent to ":")
]
colors = []
random.seed(time.time())
for i in range(10):
    colors.append('#%06X' % random.randint(0, 0xFFFFFF))
colors = [
    "#1f77b4",  # Blue
    "#ff7f0e",  # Orange
    "#2ca02c",  # Green
    "#d62728",  # Red
    "#9467bd",  # Purple
    "#8c564b",  # Brown
    "#e377c2",  # Pink
    "#7f7f7f",  # Gray
    "#bcbd22",  # Olive
    "#17becf"   # Cyan
]
line_markers = [
    ".",    # Point marker
    ",",    # Pixel marker
    "o",    # Circle marker
    "v",    # Triangle down marker
    "^",    # Triangle up marker
    "<",    # Triangle left markercolumn_names
    ">",    # Triangle right marker
    "1",    # Tri down marker
    "2",    # Tri up marker
    "3",    # Tri left marker
    "4",    # Tri right marker
    "s",    # Square marker
    "p",    # Pentagon marker
    "*",    # Star marker
    "h",    # Hexagon1 marker
    "H",    # Hexagon2 marker
    "+",    # Plus marker
    "x",    # X marker
    "D",    # Diamond marker
    "d",    # Thin diamond marker
]

with open("python/process_files/parameters.txt", 'r') as file:
    loaded_json_str = file.read()

try:
    parameters = json.loads(loaded_json_str)
except json.JSONDecodeError as e:
    print(f"Error loading JSON: {e}")
    print(f"Problematic part of JSON: {loaded_json_str[e.pos-50:e.pos+50]}")

# Deserialize the JSON string to a dictionary
parameters = json.loads(loaded_json_str)

#Specify bounds for the HSV mask
# lower_bound_picture = np.array([0, 120, 115]) #downwards
# upper_bound_picture = np.array([80, 255, 255])
lower_bound_picture = np.array([0, 20, 0]) #dots_downwards
upper_bound_picture = np.array([80, 255, 255])

lower_bound_video = np.array([0, 80, 50]) 
upper_bound_video = np.array([80, 255, 255])

lower_bound_screenshot = np.array([0, 100, 100])
upper_bound_screenshot = np.array([100, 255, 255])

#Set kernel size for different images
kernel_size_screenshot = 10
kernel_size_picture = 12
kernel_size_video = 7

def process_image(img_color, image_type, plot = False):
    if image_type == "screenshot":
        kernel = np.ones((kernel_size_screenshot, kernel_size_screenshot), np.uint8)
        lower = lower_bound_screenshot
        upper = upper_bound_screenshot
    elif image_type == "picture":
        kernel = np.ones((kernel_size_picture, kernel_size_picture), np.uint8)
        lower = lower_bound_picture
        upper = upper_bound_picture
    elif image_type == "video":
        kernel = np.ones((kernel_size_picture, kernel_size_video), np.uint8)
        lower = lower_bound_video
        upper = upper_bound_video
    else:
        raise ValueError("Select screenshot, picture, or video as image type")

    # Convert the image to grayscale
    image_gray = cv2.cvtColor(img_color, cv2.COLOR_RGB2GRAY)
    
    # Threshold to select non-white items
    ret, im_thresh = cv2.threshold(image_gray, 250, 255, cv2.THRESH_BINARY_INV)

    # Convert the original image to HSV
    hsv = cv2.cvtColor(img_color, cv2.COLOR_RGB2HSV)

    # Apply the HSV mask to keep only the selected range
    mask_hsv = cv2.inRange(hsv, lower, upper)
    img_masked_hsv = cv2.bitwise_and(img_color, img_color, mask=mask_hsv)

    # Combine the grayscale threshold mask and the HSV mask
    combined_mask = cv2.bitwise_and(im_thresh, mask_hsv)

    # Apply the combined mask to the original image
    img_masked = cv2.bitwise_and(img_color, img_color, mask=combined_mask)

    # Create a new image in Gray from the masked RGB image to change every pixel to either white [255] or black [0]
    image_gray_masked = cv2.cvtColor(img_masked, cv2.COLOR_RGB2GRAY)
    ret, im_thresh_masked = cv2.threshold(image_gray_masked, 0, 255, cv2.THRESH_BINARY)

    if image_type == "screenshot":
        img_closing = cv2.morphologyEx(im_thresh_masked, cv2.MORPH_CLOSE, kernel, iterations=1)
        image_mask = cv2.morphologyEx(img_closing, cv2.MORPH_OPEN, kernel, iterations=0)
    elif image_type == "picture":
        image_open = cv2.morphologyEx(im_thresh_masked, cv2.MORPH_OPEN, kernel, iterations=2)
        image_mask = cv2.morphologyEx(image_open, cv2.MORPH_CLOSE, kernel, iterations=1)
        # image_mask = cv2.morphologyEx(img_closing, cv2.MORPH_OPEN, kernel, iterations=1)
    elif image_type == "video":
        image_open = cv2.morphologyEx(im_thresh_masked, cv2.MORPH_OPEN, kernel, iterations=0)
        image_mask = cv2.morphologyEx(image_open, cv2.MORPH_CLOSE, kernel, iterations=2)
        # image_mask = cv2.morphologyEx(img_closing, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, hierarchy = cv2.findContours(image_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        contour[:, :, 1] = img_masked.shape[0] - contour[:, :, 1]

    if contours:
        biggest_contour = contours[0]
        for i in range(len(contours)):
            if cv2.contourArea(contours[i]) > cv2.contourArea(biggest_contour):
                biggest_contour = contours[i]
    else:
        biggest_contour = None

    if plot:

        points = np.array(points_from_contour(biggest_contour))
        draw_points = points
        img_height = img_masked.shape[0]
        draw_points[:, 1] = img_height - draw_points[:, 1]

        img_with_contour = img_color.copy()

        draw_contour = biggest_contour
        img_height = img_masked.shape[0]
        draw_contour[:, :, 1] = img_height - draw_contour[:, :, 1]

        cv2.drawContours(img_with_contour, [draw_contour], -1, (0, 255, 0), 10)

        plt.imshow(cv2.cvtColor(img_with_contour, cv2.COLOR_BGR2RGB))
        plt.scatter(points[:, 0], points[:, 1], label='Joints', color='r', s=25, marker='x')
        plt.title('Image with Contour')
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
        # plt.savefig(f'impr_{str(image_type)}.png')
        if image_type == "video" and plot:
            plt.show(block=False)  # Non-blocking show
            plt.pause(0.005)  # Display the plot for 1 second (adjust as needed)
            plt.clf()

        else:
            plt.show()

            fig, axs = plt.subplots(3, 2, figsize=(8, 6))

            axs[0, 0].imshow(cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB))
            axs[0, 0].set_title('Original Image')

            axs[0, 1].imshow(image_gray, cmap='gray')
            axs[0, 1].set_title('Grayscale Image')

            axs[1, 0].imshow(im_thresh, cmap='gray')
            axs[1, 0].set_title('Threshold Image')

            axs[1, 0].imshow(cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB))
            axs[1, 0].set_title('HSV Image')

            axs[1, 1].imshow(cv2.cvtColor(img_masked, cv2.COLOR_BGR2RGB))
            axs[1, 1].set_title('Masked Image')

            axs[2, 0].imshow(cv2.cvtColor(image_mask, cv2.COLOR_BGR2RGB))
            axs[2, 0].set_title('Thresholded Image')

            axs[2, 1].imshow(cv2.cvtColor(img_with_contour, cv2.COLOR_BGR2RGB))
            axs[2,1].scatter(points[:, 0], points[:, 1], label='Joints', color = 'r', s = 15, marker = 'x')
            axs[2, 1].set_title('Image with Contour')

            plt.tight_layout(rect=[0, 0, 1, 0.96])
            fig.suptitle('Image processing steps of a screenshot', fontsize=16)
            plt.savefig(f'impr_{str(image_type)}.png')
            plt.show()


            # Save each subplot as a separate PNG file
            for i, ax in enumerate(axs.flat):
                # Save the current subplot
                extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
                fig.savefig(os.getcwd()+ f'/python/images/subplot_{i+1}.png', bbox_inches=extent, dpi=500)

    return image_mask, biggest_contour


def resize_image(img, scale_percent):
    # Calculate the new dimensions
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    
    # Resize the image
    resized_img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
    
    return resized_img


def exponential_smoothing(series, alpha):
    smoothed_series = [series[0]]  # Initialize the smoothed series with the first observation

    for i in range(1, len(series)):
        smoothed_value = alpha * series[i] + (1 - alpha) * smoothed_series[-1]
        smoothed_series.append(smoothed_value)

    return smoothed_series


def points_from_contour(contour, plot = False):
    x_coordinates = contour[:,:,0]
    # min_x = np.min(x_coordinates)
    max_x = np.max(x_coordinates)

    top_line_x = []
    top_line_y = []
    bottom_line_x = []
    bottom_line_y = []
    reached_end = False
    reached_start = False
    i = 0
    while i < len(contour):
        point = contour[i][0]
        if point[0] == max_x:
            reached_end = True
        if i > 0:
            if point[1] > previous_y:
                reached_start = True
        if reached_end:
            top_line_x.insert(0, point[0])
            top_line_y.insert(0, point[1])
        elif reached_start:
            bottom_line_x.append(point[0])
            bottom_line_y.append(point[1])
        i+=1
        previous_y = point[1]

    # Convert lists to numpy arrays
    top_line_y = np.array(top_line_y)
    bottom_line_y = np.array(bottom_line_y)

    smoothed_bottom_y = exponential_smoothing(bottom_line_y, alpha=0.8)
    smoothed_bottom_y = exponential_smoothing(smoothed_bottom_y, alpha=0.7)
    smoothed_bottom_y = bottom_line_y


    # Convert lists to numpy arrays
    top_line_y = np.array(top_line_y)
    bottom_line_y = np.array(bottom_line_y)

    # Smooth the data with Savitzky-Golay filter
    # smoothed_bottom_y = savgol_filter(bottom_line_y, window_length=11, polyorder=5)
    # detrended_bottom_y = detrend(smoothed_bottom_y)
    # Find local maxima in the bottom line
    bottom_maxima_indices, _ = find_peaks(smoothed_bottom_y, prominence=0.2, distance=30)
    # Select the desired number of peaks
    num_peaks_to_find = 7
    bottom_maxima_indices = bottom_maxima_indices[:num_peaks_to_find]

    if plot:
        # Plot the original, smoothed, and detrended data
        plt.figure(figsize=(12, 6))

        plt.plot(bottom_line_y, label='Original Bottom Line', color='blue')
        plt.plot(smoothed_bottom_y, label='Smoothed Bottom Line', color='green')
        # plt.plot(detrended_bottom_y, label='Detrended Bottom Line', color='purple')

        # Mark the detected peaks on the detrended data
        plt.scatter(bottom_maxima_indices, smoothed_bottom_y[bottom_maxima_indices], color='red', label='Detected Peaks', zorder=5)

        plt.title('Detrended and Smoothed Data with Detected Peaks')
        plt.xlabel('Index')
        plt.ylabel('Value')
        plt.legend()
        # plt.grid(True)
        plt.show()


    smoothed_top_y = exponential_smoothing(top_line_y, alpha=0.8)
    smoothed_top_y = exponential_smoothing(smoothed_top_y, alpha=0.7)
    smoothed_top_y = top_line_y

    # Assuming smoothed_top_y is a list
    smoothed_top_y = np.array(smoothed_top_y)

    # Negate the smoothed top line data to find valleys
    smoothed_negative_top_y = -smoothed_top_y
    # Find local maxima in the bottom line
    top_minima_indices, _ = find_peaks(smoothed_negative_top_y, prominence=0.3, distance=40)
    # Select the desired number of peaks
    # num_peaks_to_find = 7
    # bottom_maxima_indices = bottom_maxima_indices[:num_peaks_to_find]

    top_minima_x = []
    top_minima_y = []
    for i in list(top_minima_indices):
        top_minima_x.append(top_line_x[i])
        top_minima_y.append(top_line_y[i])

    bottom_maxima_x = []
    bottom_maxima_y = []
    points = []
    for i in list(bottom_maxima_indices):
        bottom_maxima_x.append(bottom_line_x[i])
        bottom_maxima_y.append(bottom_line_y[i])
        points.append([bottom_line_x[i],bottom_line_y[i]])

    return points


# Define the starting point
start_point = [0,0]

def forward_kinematics(angles, length):
    x, y = start_point[0], start_point[1]
    points = [start_point]
    cumulative_angle = 0
    for i in range(len(angles)):
        cumulative_angle += angles[i]
        
        x += length[i] * np.cos(cumulative_angle)
        y -= length[i] * np.sin(cumulative_angle)
        points.append([x, y])
    return points

def inverse_kinematics(points):
    angles = []
    lengths = []
    
    for i in range(1, len(points)):
        # Calculate the difference in x and y coordinates
        dx = points[i][0] - points[i-1][0]
        dy = points[i][1] - points[i-1][1]
        
        # Calculate the length between the points
        length = np.sqrt(dx**2 + dy**2)
        lengths.append(length)
        
        # Calculate the angle of the line segment relative to the previous segment
        angle = np.arctan2(-dy, dx)
        if i == 1:
            angles.append(angle)
        else:
            # Calculate the relative angle to the previous segment
            angles.append(angle - sum(angles))
    
    return angles, lengths

def get_length(points):
    lengths = []
    
    for i in range(1, len(points)):
        # Calculate the difference in x and y coordinates
        dx = points[i][0] - points[i-1][0]
        dy = points[i][1] - points[i-1][1]
        
        # Calculate the length between the points
        length = np.sqrt(dx**2 + dy**2)
        lengths.append(length)
        
    return lengths


# Function to count overshoots in a video and track the y-coordinate of the detected corners
def process_video(video_path, frame_rate):
    tolerance = 12.4 #amount of pixels that correspond to a distance in mm where 12.4px = 1mm

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return -1
    # Initialize variables
    frame_count = 0
    settling_time = 0

    # List to store y positions
    y_positions = []

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # Process the frame (assuming your processing function is process_image)
        processed_frame, contour = process_image(frame, "video", plot=False)
        angles, lengths = inverse_kinematics(points_from_contour(contour))

        # Find the corner with the highest x-value
        max_x_corner = tuple(contour[contour[:, 0, 0].argmax()][0])

        # Append y-position to the list
        y_positions.append(max_x_corner[1])

    cap.release()

    # Smoothing the y_positions with a Gaussian filter
    y_positions_smoothed = gaussian_filter1d(y_positions, sigma=4)

    # Count peaks in the smoothed signal
    peaks, _ = find_peaks(y_positions_smoothed, prominence=0.9, distance=30)#, threshold=tolerance)

    # Count valleys in the smoothed signal (inverted peaks)
    valleys, _ = find_peaks(-y_positions_smoothed, prominence=0.9, distance=30)#, threshold=tolerance)

    # Combine peaks and valleys into a single array of indices
    all_extrema_indices = np.sort(np.concatenate((peaks, valleys)))

    #Ensure that the first direction is upwards
    while y_positions_smoothed[all_extrema_indices[0]] > y_positions_smoothed[all_extrema_indices[1]]:
        all_extrema_indices = all_extrema_indices[1:]

    # Initialize a list for filtered extreme indices
    extreme_indices = [all_extrema_indices[0]]
    # Loop through the combined extrema indices
    for i in range(1, len(all_extrema_indices)-1):
        # Ensure we have neighbors to compare
        current_value = y_positions_smoothed[all_extrema_indices[i]]
        previous_value = y_positions_smoothed[all_extrema_indices[i-1]]
        next_value = y_positions_smoothed[all_extrema_indices[i+1]]

        # Check the conditions with correct data types
        if abs(current_value - previous_value) > tolerance:
            if  abs(current_value - next_value) > tolerance:
                extreme_indices.append(all_extrema_indices[i])

    #Ensure that the first direction is upwards
    while y_positions_smoothed[extreme_indices[0]] > y_positions_smoothed[extreme_indices[1]]:
        extreme_indices = extreme_indices[1:]

    # Overshoot count is the total number of valid peaks and valleys
    overshoot_count = len(extreme_indices)-1

    # Count the frames from initial extrema to the last one plus the time from single to last to last (assumption)
    # Count the frames from initial extrema to the last one plus the time from single to last to last (assumption)
    end_point = extreme_indices[-1]+round((extreme_indices[-1]-extreme_indices[-2])/2)
    frame_count = end_point - extreme_indices[0] 
    settling_time = frame_count/frame_rate

    print("Total Frames: {}".format(frame_count))
    print("Number of Overshoots: {}".format(overshoot_count))
    print("Settling Time: {} seconds".format(settling_time))

    # Plot y positions over time with peaks and valleys
    # plt.figure(figsize=(10, 6))

    y_positions = np.array(y_positions) / 12.4
    y_positions_smoothed = np.array(y_positions_smoothed) / 12.4

    # Plot the original and smoothed y-positions
    plt.plot(y_positions, label='Measured Y Position', alpha=0.6, zorder=1)
    plt.plot(y_positions_smoothed, label='Smoothed Y Position', color='red', zorder=2)

    # Plot valid peaks with increased size and zorder
    plt.scatter(extreme_indices, np.array(y_positions_smoothed)[extreme_indices], 
                color='green', label='Extreme points', s=50, zorder=3)
    plt.scatter(extreme_indices[0], np.array(y_positions_smoothed)[extreme_indices[0]], 
                color='blue', label='Start/End point', s=75, zorder=4)
    plt.scatter(end_point, np.array(y_positions_smoothed)[end_point], 
                color='blue', s=75, zorder=4)
    

    # Plot settings
    plt.xlabel('Time [ms]')
    plt.ylabel('Y Position [mm]')
    # plt.title('Y Position of Corner with Highest X-value Over Time')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'video_processing.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.show()

    return settling_time, overshoot_count

def process_y_values(y_values):
    tolerance = 1 #mm
    frame_rate = 1000
    y_values = y_values * 1000
    y_positions_smoothed = y_values
    # Count peaks in the smoothed signal
    peaks, _ = find_peaks(y_positions_smoothed, prominence=0.9, distance=30)#, threshold=tolerance)

    # Count valleys in the smoothed signal (inverted peaks)
    valleys, _ = find_peaks(-y_positions_smoothed, prominence=0.9, distance=30)#, threshold=tolerance)

    # Combine peaks and valleys into a single array of indices
    all_extrema_indices = np.sort(np.concatenate((peaks, valleys)))

    all_extrema_indices = np.insert(all_extrema_indices, 0, 0)

    # Initialize a list for filtered extreme indices
    extreme_indices = [all_extrema_indices[0]]
    # Loop through the combined extrema indices
    for i in range(1, len(all_extrema_indices)-1):
        # Ensure we have neighbors to compare
        current_value = y_positions_smoothed[all_extrema_indices[i]]
        previous_value = y_positions_smoothed[all_extrema_indices[i-1]]
        next_value = y_positions_smoothed[all_extrema_indices[i+1]]

        # Check the conditions with correct data types
        if abs(current_value - previous_value) > tolerance:
            if  abs(current_value - next_value) > tolerance:
                extreme_indices.append(all_extrema_indices[i])

    # Overshoot count is the total number of valid peaks and valleys
    overshoot_count = len(extreme_indices)-1

    # Count the frames from initial extrema to the last one plus the time from single to last to last (assumption)
    end_point = extreme_indices[-1]+round((extreme_indices[-1]-extreme_indices[-2])/2)
    frame_count = end_point - extreme_indices[0] 
    settling_time = frame_count/frame_rate

    print("Total Frames: {}".format(frame_count))
    print("Number of Overshoots: {}".format(overshoot_count))
    print("Settling Time: {} seconds".format(settling_time))

    # Plot y positions over time with peaks and valleys
    # plt.figure(figsize=(10, 6))

    # Plot the original and smoothed y-positions
    plt.plot(y_values, label='Measured Y Position', alpha=0.6)
    plt.plot(y_positions_smoothed, label='Smoothed Y Position', color='red')

    # Plot valid peaks
    plt.scatter(extreme_indices, np.array(y_positions_smoothed)[extreme_indices], color='green', label='Extreme points')
    plt.scatter(extreme_indices[0], np.array(y_positions_smoothed)[extreme_indices[0]], color='blue', label='Starting/End point')
    plt.scatter(end_point, np.array(y_positions_smoothed)[end_point], color='blue')
    

    # Plot settings
    plt.xlabel('Frame Number')
    plt.ylabel('Y Position [Px]')
    # plt.title('Y Position of Corner with Highest X-value Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

    return settling_time, overshoot_count

def crop_center_percentage(image, crop_percentage):
    """
    Crops an image to keep the center region based on a percentage.

    Args:
    image (numpy.ndarray): Input image.
    crop_percentage (tuple): Desired crop size as a percentage (width%, height%).

    Returns:
    numpy.ndarray: Cropped image.
    """
    # Get the dimensions of the image
    img_height, img_width = image.shape[:2]

    # Calculate the crop dimensions based on the percentage
    crop_width = int(img_width * crop_percentage[0] / 100)
    crop_height = int(img_height * crop_percentage[1] / 100)

    # Calculate the starting point for cropping (centered)
    start_x = img_width // 2 - (crop_width // 2)
    start_y = img_height // 2 - (crop_height // 2)

    # Crop the image
    cropped_image = image[start_y:start_y + crop_height, start_x:start_x + crop_width]

    return cropped_image

# all_points = {}

def create_overlay(mass):
    image_path = os.getcwd()+"/python/images/"+str(parameters["direction"])+"_"+str(mass)+'.png'
    img_color = cv2.imread(image_path, 1)  # Retrieve real image in RGB
    img_color_flipped = cv2.flip(img_color, 0)
    image_mask, biggest_contour_image = process_image(img_color_flipped, "picture", plot = False)

    screenshot_path = os.getcwd()+"/python/images/screenshot"+"_"+str(mass)+'.png'
    screenshot_color = cv2.imread(screenshot_path, 1)  # Retrieve real image in RGB
    screenshot_color = crop_center_percentage(screenshot_color, (85,85))
    screenshot_color = cv2.flip(screenshot_color, 1)
    screenshot_color = cv2.flip(screenshot_color, 0)
    image_screenshot, biggest_contour_screenshot = process_image(screenshot_color, "screenshot", plot = False)

    # Get bounding rectangles for both contours
    x_img, y_img, w_img, h_img = cv2.boundingRect(biggest_contour_image)
    x_scr, y_scr, w_scr, h_scr = cv2.boundingRect(biggest_contour_screenshot)

    # Compute scaling factor based on width or height
    scale_x = w_img / w_scr
    scale_y = h_img / h_scr
    scale = scale_x  # To preserve aspect ratio

    # Translate the screenshot contour so the origins align
    translated_screenshot_contour = biggest_contour_screenshot - np.array([x_scr, y_scr])

    # Scale the screenshot contour
    scaled_screenshot_contour = np.int32(translated_screenshot_contour * scale)

    # Translate the scaled screenshot contour to match the image contour's position
    final_screenshot_contour = scaled_screenshot_contour + np.array([x_img, y_img])

     # Create a blank image to draw the contours (same size as the original image)
    overlay = np.zeros_like(img_color)

    # Draw the first contour in one color (Webots contour)
    cv2.drawContours(overlay, [biggest_contour_image], -1, (255, 0, 0), 5)  # Blue for the first contour

    # Draw the second contour in another color (Real experiment contour)
    cv2.drawContours(overlay, [final_screenshot_contour], -1, (0, 255, 0), 5)  # Green for the second contour

    # Optional: Blend the overlay with one of the images to create a semi-transparent overlay effect
    blended = cv2.addWeighted(img_color, 0.7, overlay, 0.3, 0)

    # Display the image with contours using matplotlib and add a legend
    plt.imshow(cv2.cvtColor(blended, cv2.COLOR_BGR2RGB))

    # Convert contours to (x, y) points for plotting
    biggest_contour_points = biggest_contour_image[:, 0, :] 
    final_screenshot_points = final_screenshot_contour[:, 0, :] 

    # Plot the contours using plt.plot()
    plt.plot(biggest_contour_points[:, 0], biggest_contour_points[:, 1], color='red', label='Real Experiment Contour', linewidth=2)
    plt.plot(final_screenshot_points[:, 0], final_screenshot_points[:, 1], color='yellow', label='Webots Contour', linewidth=2)


    # Set the conversion factor for pixels to meters
    pixel_per_meter = 12.4  # 124 pixels = 0.01 meters => 1240 pixels = 1 meter

    # Get image dimensions
    img_height, img_width = img_color.shape[:2]

    # Define tick positions in meters corresponding to every 0.1 m interval (10 cm)
    meter_interval = 25  # Change this if you want different intervals
    xtick_positions = np.arange(0, img_width, pixel_per_meter * meter_interval)  # In pixels
    ytick_positions = np.arange(0, img_height, pixel_per_meter * meter_interval)  # In pixels

    # Set the ticks and their labels
    plt.xticks(xtick_positions, [f"{tick / pixel_per_meter:.0f}" for tick in xtick_positions])  # Convert to meters
    plt.yticks(ytick_positions, [f"{tick / pixel_per_meter:.0f}" for tick in ytick_positions])  # Convert to meters

    # Add a legend
    # plt.legend(loc='lower left')

    # # Add labels
    # plt.xlabel("X (mm)")
    # plt.ylabel("Y (mm)")

    # Display the plot
    plt.tight_layout(rect=[0, 0, 1, 0.9])
    # plt.tight_layout(pad=0.5, w_pad=0.5, h_pad=0.5)  # Adjust pad values as needed


    # Save the resulting overlay
    overlay_path = os.getcwd() + "/python/images/overlay_" + str(mass) + '.pdf'
    plt.savefig(overlay_path, bbox_inches='tight', pad_inches=0.1)
    print(f"Overlay image saved as {overlay_path}")

    plt.show()

webots_points = [[[0.0, 0.0], [152.00821446, -3.67460699], [301.98622939, -10.20109445], [447.07442003, -17.6453497], [595.93812027, -25.74465522], [743.85408806, -35.17155675], [899.60762971, -45.26285328]],
[[0.0, 0.0], [147.26146819, -8.18901614], [290.98203583, -23.1689507], [445.39077106, -42.6353958], [591.40999322, -62.49456895], [736.78725496, -87.44355226], [884.96657304, -113.61394954]],
[[0.0, 0.0], [145.96032887, -12.47326722], [296.88504365, -36.94223678], [436.75913124, -64.58712093], [582.30856234, -95.76985823], [725.3986883, -135.2314326], [864.91956674, -174.95453016]],
[[0.0, 0.0], [140.25267513, -15.91185469], [282.65902561, -46.78953823], [422.86118061, -84.03676274], [570.00727266, -126.53414614], [703.54433462, -176.78206234], [845.02678649, -231.85216141]],
[[0.0, 0.0], [145.10769693, -20.24243792], [289.4112627, -58.93973634], [427.25200556, -104.42522422], [561.81811104, -152.80872611], [694.53601018, -215.5937502], [828.25820209, -281.14049221]],
[[0.0, 0.0], [140.3472885, -22.9703855], [275.77926242, -65.80939157], [414.33456383, -119.9612932], [545.9585477, -176.13180924], [674.06659551, -248.72883456], [803.12461112, -324.63027464]],
[[0.0, 0.0], [141.75046664, -26.37811984], [273.84366682, -74.12104043], [406.53036971, -133.61254299], [536.81964009, -197.5242479], [659.44232735, -278.10139459], [780.68277994, -360.91294364]],
[[0.0, 0.0], [139.81100384, -28.92893368], [269.63759518, -81.36037637], [401.08583902, -147.47663149], [527.15382418, -216.98823568], [645.36030695, -305.06335948], [760.38759745, -394.29184394]],
[[0.0, 0.0], [139.11669791, -31.48879742], [268.49429689, -88.91211047], [393.87051093, -158.48800395], [516.49071508, -233.22277185], [628.97564142, -326.64194198], [728.10951284, -412.48759148]],
[[0.0, 0.0], [135.47285988, -33.12256383], [260.00495558, -93.10387043], [384.18833396, -168.1804216], [502.52282266, -246.90112272], [599.31584806, -335.37773111], [708.79232847, -439.88084225]],
[[0.0, 0.0], [131.96049268, -34.51707364], [255.09990486, -98.24842516], [376.15291345, -177.18617983], [493.02508321, -261.1974644], [584.16297939, -351.92719425], [686.67796862, -458.65899356]]]

def create_validation_plot(mass_values):
    for i, mass in enumerate(mass_values):
        image_path = os.getcwd()+"/python/images/"+str(parameters["direction"])+"_"+str(mass)+'.png'
        img_color = cv2.imread(image_path, 1)  # Retrieve real image in RGB
        img_color_flipped = cv2.flip(img_color, 0)
        image_mask, biggest_contour_image = process_image(img_color_flipped, "picture", plot = False)
        real_points = points_from_contour(biggest_contour_image)

        # Assume real_points is a list of points like [[x1, y1], [x2, y2], ...]
        first_point = real_points[0]
        # Subtract first_point from each point in real_points and change the sign of the x value
        real_points = [[-(x - first_point[0]), y - first_point[1]] for x, y in real_points]

        print(real_points)

        line_styles = ['-', '--']
        line_markers = ['o', 'x']


        # Plot 1: Real Angles Comparison
        # plt.figure(figsize=(10, 6))
        # Plot lines for real angles if there are enough points
        if len(real_points) > 1:
            plt.plot(
                [p[0] for p in real_points],
                [p[1] for p in real_points],
                color='red',
                linestyle=line_styles[0],
                marker=line_markers[0]
            )
            
        # Plot lines for Webots angles if there are enough points
        if len(webots_points[i]) > 1:
            plt.plot(
                [p[0] for p in webots_points[i]],
                [p[1] for p in webots_points[i]],
                color='green',
                linestyle=line_styles[1],
                marker=line_markers[1]
            )

    # Add title, labels, and legend
    plt.xlabel("X")
    plt.ylabel("Y")
    # plt.title("Real vs. Webots Angles Comparison for Each Mass")
    plt.grid(True)
    # plt.legend(loc='upper left')

    # Save or show the plot
    save = False  # Set this to True if you want to save the plot
    if save:
        plt.savefig('angles_comparison.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.show()

    
create_validation_plot(["0", "0.01", "0.02", "0.03", "0.04", "0.05", "0.06", "0.07", "0.08", "0.09", "0.1"])

# create_overlay("0")
# create_overlay("0.03")
# create_overlay("0.05")
# create_overlay("0.07")
# create_overlay("0.09")

# #Process images to obtain the angles between the joints
# # for mass in ["0", "0.01", "0.02", "0.03", "0.04"]:#, "0.05", "0.06", "0.07", "0.08", "0.09", "0.1"]:
# for mass in ["0.04"]:
#     # path = parameters["image_path"].replace("PICTURE",""+str(parameters["direction"])+"_"+str(mass))
#     path = os.getcwd()+"/python/images/"+str(parameters["direction"])+"_"+str(mass)+'.png'
#     img_color = cv2.imread(path, 1)  # Retrieve real image in RGB
#     image_mask, biggest_contour_image = process_image(img_color, "picture", plot = True)
#     points = np.array(points_from_contour(biggest_contour_image))
#     angles, length = inverse_kinematics(points)
#     # print(angles)
#     # print(sum(angles))
#     points = points - points[0]
#     # # all_points[str(mass)] = points


# path = os.getcwd()+"/python/images/passive_dynamic_downwards_40.mp4"
# print(process_video(path, 960))

passive_dynamic_data = {"0.02" : [10, 0.35],
                        "0.04" : [12, 0.425],
                        "0.06" : [13, 0.484375],
                        "0.1": [15, 0.5447916666666667]
}

# import ast

# file_name = str(parameters["overshoot_y_values"]).replace(".txt", "_particle_0") + ".txt"
# with open(file_name, "r") as file:
#     y_values = file.read()

# # Safely convert the string representation of a list into an actual list
# y_values = ast.literal_eval(y_values)
# process_y_values(np.array(y_values))

# path =
