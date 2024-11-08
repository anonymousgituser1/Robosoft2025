import cv2
import os

# Parameters
frame_folder = "/Users/lars/Documents/GitHub/Lars_Hof_RUG_BaIP_AY_23_24/python/images/video_0.04"
output_video = "damping_video_webots_0.04.mp4"
output_frame_rate = 60  # Save the video at 60 FPS
recorded_frame_rate = 500  # Recorded frame rate

# Get all frame filenames, sorted by frame number
frames = sorted([f for f in os.listdir(frame_folder) if f.endswith(".png")])

# Read the first frame to determine the width and height
first_frame = cv2.imread(os.path.join(frame_folder, frames[0]))
height, width, layers = first_frame.shape

# Define the video writer with codec and parameters
fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Define codec (e.g., mp4v for .mp4 format)
video = cv2.VideoWriter(output_video, fourcc, output_frame_rate, (width, height))

# Calculate how many frames to skip
skip_frames = recorded_frame_rate // output_frame_rate  # This will be 16

# Add frames to the video, skipping frames to achieve 60 FPS playback
for i in range(0, len(frames), skip_frames):
    img = cv2.imread(os.path.join(frame_folder, frames[i]))
    video.write(img)  # Write the selected frame to the video

# Release the video writer
video.release()
print(f"Video saved as {output_video}")
