#Main file from which calibration experiments can be conducted
#Please read all comments carefully to see where which 
# calibration parameters can be set
#Author: Lars Hof
#Date: January 2024

import json
import numpy as np
import os
from matplotlib import pyplot as plt
from math import radians
import seaborn as sns
import pandas as pd
from scipy.stats import zscore
from datetime import datetime
import random
import soft_gripper_calibration

# This file should be used as the main file to start simulations from.
# All simulation parameters can be set here, 
# they are exported to a dictionairy that is to be used in the other files

def defaults(default_value, slices):
    ## This function takes a default value of some constant 
    # and creates a matrix of slices (number of joints) 
    defaults = np.full(slices, default_value)
    return defaults

def write_parameters(parameters):
    #Dump and write parameters
    json_parameters = json.dumps(parameters)
    # Specify the file path
    file_path = 'python/process_files/parameters.txt'
    # Write the JSON string to the text file
    with open(file_path, 'w') as file:
        file.write(json_parameters)
        os.fsync(file.fileno())

    #Also write the parameters to a location in the controllers file to avoid permission issues
    controller_file_path = 'controllers/parameters.txt'
    # Write the JSON string to the text file
    with open(controller_file_path, 'w') as file:
        file.write(json_parameters)
        os.fsync(file.fileno())

parameters={}

## SIMULATION PARAMETERS

# Operating System
OS = "Mac" #Mac (at home), Windows (at uni) or Linux (at uni). The relevant paths are exported to the parameter dict later on

parameters["timeout"] = 60 # Timeout for each iteration of spring or damping cst [sec]
parameters["slices"] = 7 #Number of joints/slices

#Extra mass on the tip of the gripper (for static passive experiments) (0/0.01/0.02/0.03/0.04)
parameters["extra_mass"] = ["0", "0.01", "0.02", "0.03", "0.04", "0.05", "0.06", "0.07", "0.08", "0.09", "0.1"]


# Spring cst range hinge
parameters["min_spring_hinge"] = 0.1 # Lowest value tested
parameters["max_spring_hinge"] = 0.6 # Highest value tested

# Spring cst range joint
parameters["min_spring_joint"] = 0.7 # Lowest value tested
parameters["max_spring_joint"] = 1.3  # Highest value tested

# Damping cst range hinge
parameters["min_damping_hinge"] = 1e-5 # Lowest value tested
parameters["max_damping_hinge"] = 2 * 1e-3 # Highest value tested

# Damping cst range joint
parameters["min_damping_joint"] = 1e-3 # Lowest value tested
parameters["max_damping_joint"] = 0.1  # Highest value tested

# Damping cst range joint
parameters["min_torque_coefficient"] = 0 # Lowest value tested
parameters["max_torque_coefficient"] = 1e-6   # Highest value tested

#Default values
parameters["default_spring_hinge"] = 0.5
parameters["default_damping_hinge"] = 0.1 #this is set high to make the static experiments faster
parameters["default_spring_joint"] = 1
parameters["default_damping_joint"] = 1
parameters["default_torque coefficient"] = 2.5*0.054/7/100000

#for passive direction: upwards, downwards, or sideways. SELECT DOWNWARDS FOR ACTIVE EXPERIMENTS
direction = "downwards"
parameters["direction"] = direction 
#set calibration to spring or damping accordingly
parameters["calibration"] = "spring" 
# set active or passive experiments
parameters["type"] = "passive"
parameters["pressures"] = [40000,80000] #pressure that is used in the active experiments

#THE FOLLOWING IMPLEMENTATION IS NOT COMPLETE YET, DO NOT USE
continue_latest = False #set to true or false indicating whether last simulations best parameters should be used
continuation_method = "best" #best: initializes one particle with the best known fitness score of the previous simulation.
                #latest initializes all particles with the best known fitness score of the previous simulation.

#Choose optimizer: PSO_globalbest PSO_localbest or GA or TEST to run a test with selected parameters
parameters["optimizer"] = "TEST"

#OPTIMIZER PARAMETERS FOR PSO
parameters["PSO_n_particles"] = 14
parameters["PSO_iterations"] = 100
#Initialize optimizer
if parameters["optimizer"] == "PSO_globalbest":  
    parameters["PSO_options"] = {'c1': 2, 'c2': 2, 'w': 0.4} 
elif parameters["optimizer"] == "PSO_localbest":  
    parameters["PSO_options"] = {'c1': 2, 'c2': 2, 'w': 0.4, 'k': 7, 'p': 2} 

parameters["PSO_max_threads"] = 4 #select the maximum number of parallel threads

#DEFAULT VALUES
#If an active experiment is conducted, the spring and damping values should be set here. These can either come from the passive experiments or default values
parameters["spring_constants_hinge"] = defaults(parameters["default_spring_hinge"], parameters["slices"]).tolist()
parameters["spring_constants_joint"] = defaults(parameters["default_spring_joint"], parameters["slices"]).tolist()
parameters["damping_constants_hinge"] = defaults(parameters["default_damping_hinge"], parameters["slices"]).tolist()
parameters["damping_constants_joint"] = defaults(parameters["default_damping_joint"], parameters["slices"]).tolist()

##Here we have some found solutions; both from experiments and emperically derived. They will overwrite previous definitions if selected
parameters["spring_constants_hinge"] = [0.190 , 0.176 , 0.311 , 0.517 , 0.103 , 0.484 , 0.401]
parameters["damping_constants_hinge"] = [0.00051057, 0.00040491, 0.00121697, 0.00079145, 0.00022654, 0.00024779, 0.00028148]
# parameters["torque_coefficients_particle_0"] = [5.74976165e-07, 7.10846158e-07, 4.75948643e-07, 6.34341678e-07, 9.07523158e-07, 1.89905322e-07, 4.91198532e-07]

def find_best_solution_per_particle(data):
    best_solutions = {}  # Dictionary to store the best solution for each particle

    # Iterate through each iteration
    for iteration_key, iteration in data.items():
        # Extract the iteration number
        iteration_number = int(iteration_key.split('_')[-1])

        # Iterate through each solution in the iteration
        for solution_key, fitness in iteration.items():
            if solution_key.startswith('fitness_'):
                # Extract the particle number
                particle_number = int(solution_key.split('_')[-1])

                # Extract the fitness score and corresponding solution
                current_fitness = fitness
                current_solution = iteration[solution_key.replace('fitness', 'solution')]

                # Check if this particle has a better fitness than previously seen
                if particle_number not in best_solutions or current_fitness < best_solutions[particle_number]['fitness']:
                    # Update the best solution for this particle
                    best_solutions[particle_number] = {'fitness': current_fitness,
                                                        'solution': current_solution,
                                                        'iteration': iteration_number}
    return best_solutions

if continue_latest:
    directory = os.getcwd() + f'/python/data'
    substring = f'raw_data_{str(parameters["direction"])}_{str(parameters["type"])}_{str(parameters["calibration"])}_'
    file_names = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)) and substring in filename:
            file_names.append(filename)

    dates = []
    for filename in file_names:
        date = filename.replace(".txt", "").split("_")[-1]
        dates.append(date)
    datetime_list = [datetime.strptime(date_str, '%Y-%m-%d') for date_str in dates]

    latest_date = max(datetime_list).date()

    latest_simulation_file = os.getcwd() + f'/python/data/raw_data_{str(parameters["direction"])}_{str(parameters["type"])}_{str(parameters["calibration"])}_{str(latest_date)}.txt' 
  
    with open(latest_simulation_file, 'r') as file:
        loaded_json_str = file.read()

    # Deserialize the JSON string to a dictionary
    data = json.loads(loaded_json_str)
    
    if continuation_method == "best":
        best_solutions = find_best_solution_per_particle(data)
        print(best_solutions)

        positions = []
        velocities = []
        initial_positions = []
        initial_velocities = []
        for particle in best_solutions.items():
            position = particle[1]["solution"]
            positions.append(position)
            # velocity = particle[1]["velocity"]
            # velocities.append(velocity)
        n=0
        for i in range(parameters["PSO_n_particles"]):
            initial_positions.append(positions[n])
            # initial_velocities.append(velocities[n])
            # if n == len(positions):
            #     n=0
            if n == 0:
                parameters["spring_constants_hinge"] = positions[n]
            n=+1
        parameters["initial_positions"] = initial_positions
        # parameters["initial_velocities"] = initial_velocities
        initial_velocities = []
        for i in range(parameters["PSO_n_particles"]):
            initial_velocities.append([random.uniform(-0.1, 0.1) for _ in range(parameters["slices"])])
        parameters["initial_velocities"] = initial_velocities

else:
    initial_positions = []
    initial_velocities = []
    for i in range(parameters["PSO_n_particles"]):
        if parameters["optimizer"] == "TEST":
            if parameters["calibration"] == "spring":
                initial_positions.append(parameters["spring_constants_hinge"])
            elif parameters["calibration"] == "damping":
                initial_positions.append(parameters["damping_constants_hinge"])
        else:
            if parameters["type"] == "passive": 
                min = "min_"+parameters["calibration"]+"_hinge"
                max = "max_"+parameters["calibration"]+"_hinge"
            else:
                min = "min_torque_coefficient"
                max = "max_torque_coefficient"

            initial_positions.append([random.uniform(parameters[min], parameters[max]) for _ in range(parameters["slices"])])
            v = (parameters[max]-parameters[min])/5
            initial_velocities.append([random.uniform(-v, v) for _ in range(parameters["slices"])])
    parameters["initial_positions"] = initial_positions
    parameters["initial_velocities"] = initial_velocities

#set the timestep and position tolerance
if parameters["calibration"] == "damping":
    parameters["timestep"] = 1
elif parameters["type"] == "active":
    parameters["timestep"] = 1
else:
    parameters["timestep"] = 32

#Tolerance to see if gripper is still moving
parameters["tolerance_overshoots"] = 0.001 #1mm
parameters["tolerance"] = 0.00001 
parameters["frame_rate"] = 960

##  FROM HERE THE CODE STARTS, NO FURTHER CHANGES FOR SIMULATION PARAMETERS ##
#DAMPING PARAMETERS
#Set all the relevant paths according to the operating system: ADJUST PATH IF NECESAIRY
if OS == "Windows": 
    parameters["path_to_webots"] = r"C:\Users\S4236610\AppData\Local\Programs\Webots\msys64\mingw64\bin\webotsw.exe"
elif OS == "Mac":
    parameters["path_to_webots"] = "/Applications/Webots.app/Contents/MacOS/webots"
elif OS == "Linux":
    parameters["path_to_webots"] = "/usr/local/webots/webots"
    # parameters["path_to_webots"] = ' '

#Set paths to the parameters dictionary such that they can be used from other files.
parameters["world_file"] = os.getcwd() + "/worlds/soft_finger_cad_slice_proto.wbt"
parameters["proto_file"] = os.getcwd() + "/protos/SoftGripper.proto"
parameters["screenshot_path"] = os.getcwd() + "/python/images/screenshot.png"
parameters["screenshot_stimulated_path"] = os.getcwd() + "/python/images/screenshot_stimulated.png"
parameters["screenshot_unstimulated_path"] = os.getcwd() + "/python/images/screenshot_unstimulated.png"
parameters["image_path"] = os.getcwd() + "/python/images/PICTURE.png"
parameters["settling_time_file"] = os.getcwd() + "/python/process_files/settling_time.txt"
parameters["experiment_text_file"] = os.getcwd() + "/python/process_files/experiment_finished.txt"
parameters["video_path"] = os.getcwd() + f"/python/images/passive_dynamic_{str(direction)}.mp4"
parameters["overshoots_simulation_file"] = os.getcwd() + "/python/process_files/overshoots_simulation_file.txt"
parameters["exerted_force"] = os.getcwd() + "/python/process_files/exerted_force.txt"
parameters["angles_file"] = os.getcwd() + "/python/process_files/angles_file.txt"
parameters["release_weight_file"] = os.getcwd() + "/python/process_files/release_weight_file.txt"
parameters["overshoot_y_values"] = os.getcwd() + "/python/process_files/overshoot_y_values.txt"

write_parameters(parameters)

#Find the initial angles for damping experiment by subjecting the gripper to the mass used in the experiment
if parameters["calibration"] == "damping":

    data = os.getcwd() + "/ython/data/raw_data_downwards_passive_spring_2024-09-14.txt"
    with open(data, 'r') as file:
        loaded_json_str = file.read()
    # Deserialize the JSON string to a dictionary
    data = json.loads(loaded_json_str)
    best_solutions = find_best_solution_per_particle(data)
    positions = []
    initial_positions = []
    for particle in best_solutions.items():
        position = particle[1]["solution"]
        positions.append(position)
    n=0
    parameters["spring_constants_hinge"] = positions[0]
    damping_extra_mass = parameters["extra_mass"]
    parameters["damping_angles"] = {}
    parameters["calibration"] = "spring"
    parameters["timestep"] = 32

    for mass in damping_extra_mass:
        write_parameters(parameters)
        import soft_gripper_calibration
        soft_gripper_calibration.springcalibration(parameters["timeout"], parameters["spring_constants_hinge"], defaults(parameters["default_damping_hinge"], parameters["slices"]).tolist(), parameters["spring_constants_joint"], parameters["damping_constants_joint"],0)
        file_name = str(parameters["angles_file"]).replace(".txt",f"_particle_0")+".txt"
        #obtain angles from webots (last simulation)
        with open(file_name, 'r') as file:
            # Read the content of the file
            line = file.readlines()
            webots_angles = [float(num) for num in line[0].strip('[').strip(']').split(',')]
        parameters["damping_angles"][str(mass)] = webots_angles

    parameters["calibration"] = "damping"
    parameters["timestep"] = 1

    #write parameters
    write_parameters(parameters)

if parameters["type"] == "active":
    for i in range(parameters["PSO_n_particles"]):
        string = f"torque_coefficients_particle_{i}"
        print(string)
        if string not in parameters:
            parameters[string] = [0.0] * parameters["slices"]  # Or appropriate initialization
    write_parameters(parameters)

# This function writes the data to CSV files and optionally generates a Seaborn line plot for visualization.
def data_to_csv(data, plot=True):
    solutions = []
    fitness_scores = []

    # Iterate through each iteration
    for iteration_key, iteration in data.items():
        # Extract the iteration number
        iteration_number = int(iteration_key.split('_')[-1])

        # Initialize solutions_iteration and fitness_scores_iteration lists
        solutions_iteration = []
        fitness_scores_iteration = []

        # Iterate through each solution in the iteration
        for solution_key, fitness in iteration.items():
            if solution_key.startswith('fitness_'):
                # Extract the particle number
                particle_number = int(solution_key.split('_')[-1])

                # Extract the fitness score and corresponding solution
                current_fitness = fitness
                current_solution = iteration[solution_key.replace('fitness', 'solution')]

                # Append current solution and fitness score to their respective lists
                solutions_iteration.append(current_solution)
                fitness_scores_iteration.append(current_fitness)

        # Append solutions_iteration and fitness_scores_iteration to main lists
        solutions.append(solutions_iteration)
        fitness_scores.append(fitness_scores_iteration)


    df = pd.DataFrame(fitness_scores, dtype="float64")

    df_personal_best = df.cummin(axis=0)

    df_global_best_fitness = df_personal_best.min(axis=1)

    df_personal_best["Average"] = df_personal_best.mean(axis=1)
    df_personal_best["STD"] = df_personal_best.std(axis=1)

    df_swarm_fitness = pd.DataFrame()
    df_swarm_fitness["Average"] = df.mean(axis=1)
    df_swarm_fitness["STD"] = df.std(axis=1)

    # # Save the DataFrames to CSV files in the working directory + /python/data
    df.to_csv(os.getcwd() + f'/python/data/raw_data_{str(parameters["type"])}_{str(parameters["calibration"])}.csv', index=False)
    df_personal_best.to_csv(os.getcwd() + f'/python/data/personal_best_{str(parameters["type"])}_{str(parameters["calibration"])}.csv', index=False)
    df_swarm_fitness.to_csv(os.getcwd() + f'/python/data/swarm_fitness_{str(parameters["type"])}_{str(parameters["calibration"])}.csv', index=False)
    df_global_best_fitness.to_csv(os.getcwd() + f'/python/data/df_global_best_fitness_{str(parameters["type"])}_{str(parameters["calibration"])}.csv', index=False)

    # Generate a Seaborn line plot if 'plot' is True
    if plot:
        plt.figure(figsize=(8, 6))  # Adjust the figure size if needed

        # Plot global best fitness
        sns.lineplot(data=df_global_best_fitness, label='Global best fitness')

        # Plot average swarm fitness with shaded area for standard deviation
        sns.lineplot(data=df_swarm_fitness["Average"], label='Average swarm fitness', color='orange')
        plt.fill_between(
            x=df_personal_best.index,
            y1=df_swarm_fitness["Average"] - df_swarm_fitness["STD"],
            y2=df_swarm_fitness["Average"] + df_swarm_fitness["STD"],
            alpha=0.2,  # Adjust the transparency of the shaded area
            color='orange'  # Adjust the color of the shaded area
        )

        # Plot average particle best fitness with shaded area for standard deviation
        sns.lineplot(data=df_personal_best["Average"], label='Average particle best fitness', color='green')
        plt.fill_between(
            x=df_personal_best.index,
            y1=df_personal_best["Average"] - df_personal_best["STD"],
            y2=df_personal_best["Average"] + df_personal_best["STD"],
            alpha=0.2,  # Adjust the transparency of the shaded area
            color='green'  # Adjust the color of the shaded area
        )

        # Set plot labels and title
        plt.xlabel('Iteration', fontsize=12)
        plt.ylabel('Fitness', fontsize=12)
        plt.suptitle('PSO Results', fontsize=14)

        # Display legend
        plt.legend()

        # Add grid lines
        plt.grid(True, linestyle='--', alpha=0.7)

        # Remove the right and top spines for aesthetics
        sns.despine()

        # Tight layout for better spacing
        plt.tight_layout()

        # Save the plot as a PNG file for Overleaf (optional)
        plt.savefig(f'PSO_results_active_experiment__{str(parameters["type"])}_{str(parameters["calibration"])}.png', dpi=300)

        # Show the plot
        plt.show()


# Execute different optimization or calibration methods based on the specified optimizer in parameters
if (parameters["optimizer"] == "PSO_localbest" or parameters["optimizer"] == "PSO_globalbest"):
    # Write the JSON string to the text file
    write_parameters(parameters)

    # Import the particle swarm optimization module
    import particle_swarm_optimization
    # Run Particle Swarm Optimization
    particle_swarm_optimization.PSO()

    current_date = datetime.today().date()
    # Process and visualize results using the data_to_csv function
    data_file = os.getcwd() + f'/python/data/raw_data_{str(parameters["direction"])}_{str(parameters["type"])}_{str(parameters["calibration"])}_{str(current_date)}.txt'
    with open(data_file, 'r') as file:
        loaded_json_str = file.read()
    # Deserialize the JSON string to a dictionary
    data = json.loads(loaded_json_str)
    data_to_csv(data, plot=True)

elif parameters["optimizer"] == "TEST":
    # Import the soft gripper calibration module for testing purposes
    import soft_gripper_calibration
    
    # Check calibration type and execute the corresponding calibration function
    if (parameters["type"] == "passive" and parameters["calibration"] == "spring"):
        import cv2
        img_color = cv2.imread(parameters["image_path"], 1)
        soft_gripper_calibration.springcalibration(parameters["timeout"], parameters["spring_constants_hinge"], parameters["damping_constants_hinge"], parameters["spring_constants_joint"], parameters["damping_constants_joint"],particle_index=0)
    
    elif (parameters["type"] == "passive" and parameters["calibration"] == "damping"):
        #write parameters to text files
        write_parameters(parameters)
        
        # Run damping calibration
        soft_gripper_calibration.damping_calibration(parameters["timeout"], parameters["spring_constants_hinge"], parameters["damping_constants_hinge"], parameters["spring_constants_joint"], parameters["damping_constants_joint"], 0)
    
    elif parameters["type"] == "active":
        # Run active calibration
        soft_gripper_calibration.active_calibration(parameters["timeout"], parameters["spring_constants_hinge"], parameters["damping_constants_hinge"], parameters["spring_constants_joint"], parameters["damping_constants_joint"], 0)
