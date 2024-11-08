"""supervisor_active controller."""
#This supervisor has 4 functions
    # 1: return the force exerted on the object in grasping mode at counter=74
    # 2: take a screenshot in grasping mode at counter=49
    # 3: take a screenshot in release mode at counter=74
    # 4: exit the experiment

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor, Node, TouchSensor
import json
import os
import sys
import time

parameters_path = os.getcwd().replace("/supervisor_active","/parameters.txt")
with open(parameters_path, 'r') as file:
    loaded_json_str = file.read()
# Deserialize the JSON string to a dictionary
parameters = json.loads(loaded_json_str)

#create supervisor and camera instance
supervisor = Supervisor()
force_sensor = supervisor.getDevice("force")
force = force_sensor.enable(parameters["timestep"])

#Initialize time
t = 0
t_exp_start = 2.5
previous_force = 0
window = 100
current_window = 0

# Access command-line arguments
args = sys.argv

# Check if --gripper_orientation is in the arguments
if "--particle_index" in args:
    # Find the index of --gripper_orientation in the arguments
    index = args.index("--particle_index")

    # Get the value of the argument (upwards or downwards)
    particle_index = args[index + 1]

# Main loop:
# - perform simulation steps until Webots is stopping the controller
#   Communicate with the text file that is written to from the experiment controller
while supervisor.step(parameters["timestep"]) != -1:
    if t > t_exp_start:

        #Read force sensor
        force = force_sensor.getValues()
        force_x = force[0]
        force_y = force[1]
        force_z = force[2]
        # print(f"Force (x, y, z): ({force_x}, {force_y}, {force_z})")
        force = max([force_x, force_y, force_z])
        if abs(force-previous_force) < parameters["tolerance"]:
            current_window += 1
            if current_window > window:
                file_name = str(parameters["exerted_force"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
                file = open(file_name, "w")
                file.write(str(force))
                file.close()
                supervisor.simulationQuit(0) 
        else:
            current_window = 0

        previous_force = force
     
    t = t + parameters["timestep"]/1000.0
