# This code does a calibration based on parameters selected by the optimizer
# Author: Lars Hof
# Date January 2024

import image_processing # import python file with image processing functions
import generate_world # import python file that creates the Webots world
import generate_proto # import python file that creates the Webots proto


import numpy as np
import time
import os
import cv2
import json
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
import math
import subprocess
from scipy.signal import find_peaks
import sys

# Redirect stderr to /dev/null
# sys.stderr = open(os.devnull, 'w')

with open("python/process_files/parameters.txt", 'r') as file:
    loaded_json_str = file.read()

# Deserialize the JSON string to a dictionary
parameters = json.loads(loaded_json_str)

#Specify bounds for the HSV mask
lower_bound_picture = np.array([0, 40, 0])
upper_bound_picture = np.array([80, 255, 255])


lower_bound_screenshot = np.array([0, 200, 160])
upper_bound_screenshot = np.array([100, 255, 255])

#Set kernel size for different images
kernel_size_screenshot = 8
kernel_size_picture = 10

#The damping simulation take somewhat longer to launch, therefore some extra time is added
if parameters["calibration"] == "spring":
    webots_launchtime = 20
elif parameters["calibration"] == "damping":
    webots_launchtime = 40

all_points = {}

def initialize(mass):
    path = parameters["image_path"].replace("PICTURE",str(parameters["direction"])+"_"+str(mass))
    img_color = cv2.imread(path, 1)  # Retrieve real image in RGB
    image_mask, biggest_contour_image = image_processing.process_image(img_color, "picture")
    points = np.array(image_processing.points_from_contour(biggest_contour_image))
    points = points - points[0]
    all_points[str(mass)] = points

# #Process images to obtain the angles between the joints
# for mass in ["0", "0.01", "0.02", "0.03", "0.04"]:
#     path = parameters["image_path"].replace("PICTURE",str(parameters["direction"])+"_"+str(mass))
#     img_color = cv2.imread(path, 1)  # Retrieve real image in RGB
#     image_mask, biggest_contour_image = image_processing.process_image(img_color, "picture")
#     points = np.array(image_processing.points_from_contour(biggest_contour_image))
#     points = points - points[0]
#     all_points[str(mass)] = points


def calculate_error(real_points, webots_points):
    real_predicted = real_points[:, 1]
    webots_predicted = webots_points[:, 1]

    error = mean_squared_error(real_predicted, webots_predicted)
    # print("Mean Squared Error:", error)
    return error

def calculate_error_weighted(real_angles, webots_angles):
    error = 0
    for i in range(len(real_angles)):
        error += (parameters["slices"]-i)*(real_angles[i]-webots_angles[i])
    return error


def fitness_spring(mass, particle_index,time_max):
    initialize(mass)

    is_timeout = False
    while is_timeout == False:

        file_name = str(parameters["angles_file"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
        #obtain angles from webots (last simulation)
        with open(file_name, 'r') as file:
            # Read the content of the file
            line = file.readlines()
            webots_angles = [float(num) for num in line[0].strip('[').strip(']').split(',')]
            webots_angles = webots_angles[:-1] # Remove last item because it is not measured in the real world

            #get the webots points wrt the length of the points from the image by using forward kinematics and the angles measured in webots
            webots_points = np.array(image_processing.forward_kinematics(webots_angles, image_processing.get_length(all_points[str(mass)])))
            print(webots_points)
            error = calculate_error(np.array(all_points[str(mass)]), webots_points)

            # real_angles = image_processing.inverse_kinematics(all_points[str(mass)])
            # error = calculate_error_weighted(real_angles, webots_angles)

            return error


def springcalibration(timeout, spring_constants_hinge, damping_constants_hinge, spring_constants_joint, damping_constants_joint, particle_index):
    with open("python/process_files/parameters.txt", 'r') as file:
        loaded_json_str = file.read()
    parameters = json.loads(loaded_json_str)
    ## Takes a grid of spring constants for both the hinges and joints. Number of hinge joints is defined globally. 
    # Based on this, the number to be tested parameter settings and the default damping values. 
    # Appropriate grids with dampings constants are created with these defaults and specified size
    print ("\n SPRING calibration started\n")

    #Set controller for the experiment
    if parameters["type"] == "passive":
        controller = "passive_exp1"
    else:
        raise ValueError("No controller for this experiment yet")

    #Iterate over the number of different sets of parameters that should be tested
    #Initialize model checks
    time_max = time.time() + timeout + webots_launchtime

    if parameters["direction"] == "upwards" or parameters["direction"] == "downwards":
        print("spring cst tested : ", str(spring_constants_hinge))
    elif parameters["direction"] == "sideways":
        print("spring cst joint tested : ", str(spring_constants_joint))

    fitness_list_spring_constants = []
    world_file = parameters["world_file"].strip('.wbt')+"_particle_"+str(particle_index)+'.wbt'
    proto_file = parameters["proto_file"].strip('.proto')+"_particle_"+str(particle_index)+'.proto'
    for mass in parameters["extra_mass"]:
        ### This function call another python file, that will create the dedicated Webots world file
        generate_world.main(world_file, controller, "supervisor_passive_exp1", parameters["direction"], parameters["timestep"], parameters["type"], mass, particle_index=particle_index)
        ### This function call another python file, that will create the dedicated Webots proto file
        generate_proto.main(proto_file, "spring", spring_constants_hinge, damping_constants_hinge, spring_constants_joint, damping_constants_joint, parameters["slices"], float(mass),particle_index=particle_index)
        ### This launches Webots simulator with the dedicated world file
        # Construct the command as a list of separate elements
        # command = [parameters["path_to_webots"], "--mode=fast", world_file]
        command = [parameters["path_to_webots"], "--minimize", "--mode=fast", world_file]

        # Execute the command using subprocess
        subprocess.check_call(command, stderr=sys.stderr)

        fitness_spring_constants_stimulated = fitness_spring(mass, particle_index, time_max)
        print (f'fitness stimulated with {mass} spring constants : ', fitness_spring_constants_stimulated)

        fitness_list_spring_constants.append(fitness_spring_constants_stimulated)

    #Get product of fitness scores
    fitness_sum = sum(fitness_list_spring_constants)
    # for fitness in fitness_list_spring_constants:
    #     fitness_sum *= fitness
    # fitness_spring_constants = sum(fitness_list_spring_constants)/len(fitness_list_spring_constants)
    print ('fitness sum spring constants : ', fitness_sum)
    print ("\n SPRING calibration FINISHED !\n")
        
    return fitness_sum

passive_dynamic_data = {"0.02" : [10, 0.35],
                        "0.04" : [12, 0.425],
                        "0.06" : [13, 0.484375],
                        "0.1": [15, 0.5447916666666667]
}


def damping_calibration(timeout, spring_constants_hinge, damping_constants_hinge, spring_constants_joint, damping_constants_joint,particle_index):
    with open("python/process_files/parameters.txt", 'r') as file:
        loaded_json_str = file.read()
    parameters = json.loads(loaded_json_str)
    #This function takes a set of (preferable earlier determined) spring constants and damping constants given by some optimazation algorithm
    #It also takes the type of experiment, and a timeout in seconds. The function then creates a world and starts a simulation.
    #The simulation determines the settling time which is returned. This settling time can be compared to that of real world experiments.

    print ("\n DAMPING calibration started\n")

    #Set controller for the experiment
    if parameters["type"] == "passive":
        controller = "passive_exp1"
    else:
        raise ValueError("No controller for this experiment yet")

    fitness_list_damping_constants = []

    if parameters["direction"] == "upwards" or parameters["direction"] == "downwards":
        print("damping cst tested : ", str(damping_constants_hinge))
    elif parameters["direction"] == "sideways":
        print("damping cst joint tested : ", str(damping_constants_joint))


    world_file = parameters["world_file"].strip('.wbt')+"_particle_"+str(particle_index)+'.wbt'
    proto_file = parameters["proto_file"].strip('.proto')+"_particle_"+str(particle_index)+'.proto'

    for mass in parameters["extra_mass"]:
        ### This function call another python file, that will create the dedicated Webots world file
        generate_world.main(world_file, controller, "supervisor_passive_exp1", parameters["direction"], parameters["timestep"], parameters["type"], mass, particle_index=particle_index)
        ### This function call another python file, that will create the dedicated Webots proto file
        generate_proto.main(proto_file, "damping", spring_constants_hinge, damping_constants_hinge, spring_constants_joint, damping_constants_joint, parameters["slices"], extra_mass=mass,particle_index=particle_index)
        ### This launches Webots simulator with the dedicated world file
        # Construct the command as a list of separate elements
        # command = [parameters["path_to_webots"], "--mode=fast", world_file]
        command = [parameters["path_to_webots"], "--minimize", "--mode=fast", world_file]

        # Execute the command using subprocess
        subprocess.check_call(command, stderr=sys.stderr)
    
   
        # #Calculates the fitness function by comparing the settling time
        file_name = str(parameters["settling_time_file"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
        with open(file_name, "r") as file:
            settling_time_simulation = float(file.read())
        file.close()

        file_name = str(parameters["overshoots_simulation_file"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
        with open(file_name, "r") as file:
            overshoots_simulation = float(file.read())
        file.close()


        print(settling_time_simulation)
        print(overshoots_simulation)

        overshoots_real = passive_dynamic_data[mass][0]
        settling_time_real = passive_dynamic_data[mass][1]

        settling_time_difference = abs(settling_time_real-settling_time_simulation)
        overshoot_difference = abs(overshoots_simulation-overshoots_real)
        # Print statements to display the differences
        print("Settling Time Difference:", settling_time_difference)
        print("Overshoot Difference:", overshoot_difference)

        fitness_damping_constants = (settling_time_difference)*(1+overshoot_difference)
        print ('fitness damping constants : ', fitness_damping_constants)

        fitness_list_damping_constants.append(fitness_damping_constants)
    #Get product of fitness scores
    fitness_sum = sum(fitness_list_damping_constants)
    # for fitness in fitness_list_spring_constants:
    #     fitness_sum *= fitness
    # fitness_spring_constants = sum(fitness_list_spring_constants)/len(fitness_list_spring_constants)
    print ('fitness sum damping constants : ', fitness_sum)
    print ("\n DAMPING calibration FINISHED !\n")
        
    return fitness_sum     


#Dictionary with the exerted forces from the real experiment at different pressures
force_dict = {
    "0": 0.0,
    "10000": 0.188133,
    "20000": 0.377502,
    "30000": 0.584083,
    "40000": 0.807874,
    "50000": 1.048877,
    "60000": 1.307090,
    "70000": 1.582514,
    "80000": 1.875150,
    "90000": 2.184996,
    "100000": 2.512053
}

def active_calibration(timeout, spring_constants_hinge, damping_constants_hinge, spring_constants_joint, damping_constants_joint, particle_index):
    with open("python/process_files/parameters.txt", 'r') as file:
        loaded_json_str = file.read()
    parameters = json.loads(loaded_json_str)
    #This function takes a set of (preferable earlier determined) spring constants and damping constants given by some optimazation algorithm
    #It also takes the type of experiment, and a timeout in seconds. The function then creates a world and starts a simulation.
    #The simulation determines the settling time which is returned. This settling time can be compared to that of real world experiments.

    print ("\n ACTIVE calibration started\n")

    # print("torque coefficients tested : ", parameters[f"torque_coefficients_particle_{particle_index}"])

    fitness_list = []
    world_file = parameters["world_file"].strip('.wbt')+"_particle_"+str(particle_index)+'.wbt'
    proto_file = parameters["proto_file"].strip('.proto')+"_particle_"+str(particle_index)+'.proto'
    for pressure in parameters["pressures"]:
        ### This function call another python file, that will create the dedicated Webots world file
        generate_world.main(world_file, "controller_active", "supervisor_active", parameters["direction"], parameters["timestep"], parameters["type"], mass= 0, particle_index=particle_index, pressure=pressure)
        ### This function call another python file, that will create the dedicated Webots proto file
        generate_proto.main(proto_file, "active", spring_constants_hinge, damping_constants_hinge, spring_constants_joint, damping_constants_joint, parameters["slices"], 0, particle_index)
        ### This launches Webots simulator with the dedicated world file
        # command = [parameters["path_to_webots"], "--mode=fast", world_file]
        command = [parameters["path_to_webots"], "--minimize", "--mode=fast", world_file]

        # Execute the command using subprocess
        subprocess.check_call(command, stderr=sys.stderr)

        file_name = str(parameters["exerted_force"]).replace(".txt",f"_particle_{str(particle_index)}")+".txt"
        #Fitness calulation
        with open(file_name, "r") as file:
            force_experiment = float(file.read())
            print(force_experiment)

        force_real = force_dict[str(pressure)]
        fitness_pressure_constants = abs(force_real-force_experiment)
        fitness_list.append(fitness_pressure_constants)
        string = f"torque_coefficients_particle_{particle_index}"  
        print("Torque coefficients tested : ", parameters[string])
        print("Fitness Torque Constants:", fitness_pressure_constants)


    #Get product of fitness scores
    fitness_sum = 1
    for fitness in fitness_list:
        fitness_sum *= fitness
        
    print("Fitness Sum Pressure Constants:", fitness_sum)
    print ("\n ACTIVE calibration FINISHED !\n")

    return fitness_sum
