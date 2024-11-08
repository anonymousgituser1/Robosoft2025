"""supervisor_passive_exp1 controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor, Camera, Node
import json
import os
import time
import sys

screenshot = False
video = True

parameters_path = os.getcwd().replace("/supervisor_passive_exp1","/parameters.txt")
with open(parameters_path, 'r') as file:
    loaded_json_str = file.read()

# Deserialize the JSON string to a dictionary
parameters = json.loads(loaded_json_str)

#create supervisor and camera instance
supervisor = Supervisor()
camera = Camera("camera1")
# ball_joint = supervisor.getFromDef("added_weight")

#Initialize time
t = 0
#The time max is the current time together with the timeout that is set in the main file
time_max = time.time() + parameters["timeout"]

# Access command-line arguments
args = sys.argv

# Check if --gripper_orientation is in the arguments
if "--particle_index" in args:
    # Find the index of --gripper_orientation in the arguments
    index = args.index("--particle_index")

    # Get the value of the argument (upwards or downwards)
    particle_index = args[index + 1]

# Check if --gripper_orientation is in the arguments
if "--mass" in args:
    # Find the index of --gripper_orientation in the arguments
    index = args.index("--mass")

    # Get the value of the argument (upwards or downwards)
    mass = args[index + 1]

experiment_text_file = str(parameters["experiment_text_file"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"

frame_counter = 0

gripper_moving = False
# Main loop:
# - perform simulation steps until Webots is stopping the controller
#   Communicate with the text file that is written to from the experiment controller
while supervisor.step(parameters["timestep"]) != -1:
    if os.path.exists(experiment_text_file):
        with open(experiment_text_file, 'r') as file:
            # Read the content of the file
            lines = file.readlines()

            # Convert the string to a list of floats
            for line in lines:
                if line.startswith("Done"):
                    if screenshot:
                        camera.enable(parameters["timestep"])
                        image_filename = parameters["screenshot_path"].replace(".png",f"_{mass}.png")
                        camera.getImage()  # Capture the image
                        camera.saveImage(image_filename, 100)  # Save the image with 100% quality
                        print(f"Screenshot saved as {image_filename}")
                    #quit the simulation
                    supervisor.simulationQuit(0)
                    break  # Exit the loop if foun
                else:
                    file.close()
    if video:
        # Save each frame as an image
        frame_filename = os.getcwd().replace("/supervisor_passive_exp1","/python/images/video_0.04" + f"/{frame_counter}.png")
        print(frame_filename)
        camera.getImage()
        camera.saveImage(frame_filename, 100)  # Save frame with 100% quality
        frame_counter = frame_counter + 1  # Increment frame counter

    if t > time_max:
        print("Supervisor timeout")
        supervisor.simulationQuit(0)
     
    t = t + parameters["timestep"]/1000.0
