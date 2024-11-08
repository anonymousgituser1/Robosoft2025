"""passive_exp1 controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Motor, Robot, PositionSensor, GPS
from math import pi
import time
import numpy as np
import json
import os
import csv
import sys
from decimal import Decimal, getcontext
from scipy.signal import find_peaks 

parameters_path = os.getcwd().replace("/passive_exp1","/parameters.txt")
with open(parameters_path, 'r') as file:
    loaded_json_str = file.read()

# Deserialize the JSON string to a dictionary
parameters = json.loads(loaded_json_str)

# create the Robot instance.
robot = Robot()

# Access command-line arguments
args = sys.argv

print(args)

# Check if --gripper_orientation is in the arguments
if "--experiment" in args:
    # Find the index of --gripper_orientation in the arguments
    index = args.index("--experiment")

    # Get the value of the argument (upwards or downwards)
    gripper_orientation = args[index + 1]

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



#Clear files
file_name = str(parameters["overshoots_simulation_file"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
with open(file_name, "w") as file:
    file.write("")

file_name = str(parameters["settling_time_file"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
with open(file_name, "w") as file:
    file.write("")

file_name = str(parameters["angles_file"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
with open(file_name, "w") as file:
    file.write("")

file_name = str(parameters["experiment_text_file"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
with open(file_name, "w") as file:
    file.write("")

file_name = str(parameters["overshoot_y_values"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
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

# Define the starting point
start_point = [0,0]
length = [0.0085, 0.0085, 0.0085, 0.0085, 0.0085, 0.0085, 0.013]

def still(pos, prev_pos):
    #Checks if the current position is the same as the previous position 
    #taking into account a globally defined tollerance
    return all(abs(pos[i] - prev_pos[i]) < parameters["tolerance"] for i in range(len(pos)))

def forward_kinematics(angles, length):
    x, y = start_point[0], start_point[1]
    points = [start_point]
    cumulative_angle = 0
    for i in range(len(angles)):
        cumulative_angle += angles[i]
        
        x += length[i] * np.cos(cumulative_angle)
        y -= length[i] * np.sin(cumulative_angle)
        points.append([x, y])
    #return y position at the end
    return points[-1][1]

def count_overshoots(y_values, t):
    tolerance = 1
    y_values = y_values * 1000
    # Count peaks in the smoothed signal
    peaks, _ = find_peaks(y_values, prominence=0.9, distance=30)#, threshold=tolerance)

    # Count valleys in the smoothed signal (inverted peaks)
    valleys, _ = find_peaks(-y_values, prominence=0.9, distance=30)#, threshold=tolerance)

    # Combine peaks and valleys into a single array of indices
    all_extrema_indices = np.sort(np.concatenate((peaks, valleys)))
    all_extrema_indices = np.insert(all_extrema_indices, 0, 0)

    if len(all_extrema_indices) > 2:
        # Count peaks in the smoothed signal
        # Initialize a list for filtered extreme indices
        extreme_indices = [all_extrema_indices[0]]
        # Loop through the combined extrema indices
        for i in range(1, len(all_extrema_indices)-1):
            # Ensure we have neighbors to compare
            current_value = y_values[all_extrema_indices[i]]
            previous_value = y_values[all_extrema_indices[i-1]]
            next_value = y_values[all_extrema_indices[i+1]]

            # Check the conditions with correct data types
            if abs(current_value - previous_value) > tolerance:
                if  abs(current_value - next_value) > tolerance:
                    extreme_indices.append(all_extrema_indices[i])

        # Overshoot count is the total number of valid peaks and valleys
        overshoot_count = len(extreme_indices)-1
        end_point = extreme_indices[-1]+round((extreme_indices[-1]-extreme_indices[-2])/2)
        frame_count = end_point - extreme_indices[0] 
        settling_time = frame_count / (1000/parameters["timestep"])

    else:
        overshoot_count = 0
        settling_time = t
    return overshoot_count, settling_time

#Write to text file to be checked in supervisor controller
file = open(parameters["experiment_text_file"], "w")
file.write("not Done")
file.close()

#Initialize for main loop
t=0
position = [0, 0, 0, 0, 0, 0, 0]
prev_position =[0, 99, 99, 99, 99, 99, 99]

arm_moving = True
release_weight = False
positions = []
y_values = []

consecutive_steps = 0  # counter for consecutive timesteps
threshold = 10  # number of consecutive steps required

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(parameters["timestep"]) != -1:
    #Only perform these steps if the simulation commences: at t=0 
    if t == 0:
        #Set the ur3e arm to a position such that the gripper is face gripping part upwards
        ur_motors[0].setPosition(0)
        ur_motors[1].setPosition(0)
        ur_motors[2].setPosition(-pi/2)
        ur_motors[3].setPosition(0)
        if gripper_orientation == "sideways":
            ur_motors[4].setPosition(-pi/2)

        #The wrist1 ([2]) joint determines how the gripper is faced 
        #and if it is still moving, get its position sensor
        ur_position = ur_motors[2].getPositionSensor()
        ur_position.enable(parameters["timestep"])

        if parameters["calibration"] == "damping":
            #set to initial position
            for i in range(parameters["slices"]):
                finger1_motor_z[i].setPosition(parameters["damping_angles"][str(mass)][i])

    #Check, for the globally defined tolerance if the ur3e arm is moving.
    #If the arm stopped moving, set the torque of all the grippers motors to zero such that it can "relax"
    #This is also where the experiment really starts
    if abs(ur_position.getValue()+pi/2) < parameters["tolerance"] and arm_moving:
        arm_moving = False
        #Write starting time of the experiment to text file
        t_start = t
  
        #Set torque to zero in each joint to asses dynamic response
        for i in range(parameters["slices"]):
            finger1_motor_z[i].setTorque(0)
    
    if arm_moving == False:
        for i in range(parameters["slices"]):
            prev_position[i] = position[i]

            position_sensor = finger1_motor_z[i].getPositionSensor()
            position_sensor.enable(parameters["timestep"])
            position[i] = position_sensor.getValue()
            
        # print(position) 
        if not np.any(np.isnan(position)):
            positions.append(position.copy())
            y_values.append(forward_kinematics(position,length))
 
    #Check if the gripper stopped moving, if it did: 
    #write this to the relevant text file to communicate with the supervisor controller.
    if still(position, prev_position):
        consecutive_steps += 1
    if consecutive_steps > threshold:
        consecutive_steps += 1
        if parameters["calibration"] == "damping":
            file_name = str(parameters["overshoot_y_values"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
            with open(file_name, "w") as file:
                file.write(str(y_values))
            overshoots, settling_time = count_overshoots(np.array(y_values), t_start-t)
            
            file_name = str(parameters["overshoots_simulation_file"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
            with open(file_name, "w") as file:
                file.write(str(overshoots))

            # #write settling time
            # with open(parameters["settling_time_file"], "a") as file:
            #     file.write(f"particle_{str(particle_index)}_mass_{str(mass)}: " + str(t-t_start) + "\n")

            file_name = str(parameters["settling_time_file"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
            with open(file_name, "w") as file:
                file.write(str(settling_time))

        # #write settling time
        # with open(parameters["angles_file"], "a") as file:
        #     file.write(f"particle_{str(particle_index)}_mass_{str(mass)}: " + str(positions[-1]) + "\n")

        file_name = str(parameters["angles_file"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
        with open(file_name, "w") as file:
            file.write(str(positions[-1]))

        #write that experiment is done
        with open(parameters["experiment_text_file"], "a") as file:
            file.write(f"particle_{str(particle_index)}_mass_{str(mass)}: " + "Done")

        file_name = str(parameters["experiment_text_file"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
        with open(file_name, "w") as file:
            file.write("Done")

        break
            
    t = t + parameters["timestep"]/1000.0