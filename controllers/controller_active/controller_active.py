"""active experiment controller."""

#"""passive_exp1 controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Motor, Robot, PositionSensor
from math import pi
import time
import numpy as np
import json
import os
import sys

parameters_path = os.getcwd().replace("/controller_active","/parameters.txt")
with open(parameters_path, 'r') as file:
    loaded_json_str = file.read()

# Deserialize the JSON string to a dictionary
parameters = json.loads(loaded_json_str)

# create the Robot instance.
robot = Robot()

# Access command-line arguments
args = sys.argv

# Check if --gripper_orientation is in the arguments
if "--experiment" in args:
    # Find the index of --gripper_orientation in the arguments
    index = args.index("--experiment")

    # Get the value of the argument (upwards or downwards)
    gripper_orientation = args[index + 1]

# Check if --gripper_orientation is in the arguments
if "--pressure" in args:
    # Find the index of --gripper_orientation in the arguments
    index = args.index("--pressure")

    pressure = float(args[index + 1])

# Check if --gripper_orientation is in the arguments
if "--particle_index" in args:
    # Find the index of --gripper_orientation in the arguments
    index = args.index("--particle_index")

    particle_index = int(args[index + 1])

file_name = str(parameters["settling_time_file"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
with open(file_name, "w") as file:
    file.write("")

# Initialize finger motors
finger1_motor_z = []
finger2_motor_z = []

#Get all the motors of both the arm and the hinges
for i in range(1, parameters["slices"] + 1):
    # Main motors Z
    finger1_z_motorname = f"finger1_rot_z_{i}"
    finger1_motor_z.append(robot.getDevice(finger1_z_motorname))

    finger2_z_motorname = f"finger2_rot_z_{i}"
    finger2_motor_z.append(robot.getDevice(finger2_z_motorname))

ur_motor_names = ["shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]
ur_motors = [robot.getDevice(name) for name in ur_motor_names]

if parameters["calibration"] == "damping":
    for i in range(parameters["slices"]):
        finger1_motor_z[i].setPosition(-parameters["average_angle"])

def still(pos, prev_pos):
    #Checks if the current position is the same as the previous position 
    #taking into account a globally defined tollerance
    return all(abs(pos[i] - prev_pos[i]) < parameters["tolerance"] for i in range(len(pos)))

#Write to text file to be checked in supervisor controller
file = open(parameters["experiment_text_file"], "w")
file.write("not Done")
file.close()

#Initialize for main loop
t=0
t_exp_start = 2
# Initialize ur_position before the loop
ur_position = ur_motors[2].getPositionSensor()
ur_position.enable(parameters["timestep"])

arm_moving = True
grasp = False

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(parameters["timestep"]) != -1:
    #Only perform these steps if the simulation commences: at t=0 
    if t == 0:
        #Set the ur3e arm to a position such that the gripper is face gripping part upwards
        ur_motors[0].setPosition(0)
        ur_motors[1].setPosition(0)
        ur_motors[2].setPosition(3*pi/2)
        ur_motors[3].setPosition(0)
        if gripper_orientation == "sideways":
            ur_motors[4].setPosition(-pi/2)

    if t > t_exp_start and grasp == False:
        print("Grasp")
        grasp = True
        for i in range(parameters["slices"]):
            finger1_motor_z[i].setTorque(parameters[f"torque_coefficients_particle_{particle_index}"][i]*pressure)

    t = t + parameters["timestep"]/1000.0