import soft_gripper_calibration
import json
import numpy as np
import cv2
# Import PySwarms
import pyswarms as ps
from pyswarms.single.global_best import GlobalBestPSO
from pyswarms.single.local_best import LocalBestPSO
from pyswarms.utils.plotters import (plot_cost_history, plot_contour, plot_surface)
import pyswarms.backend as P
from pyswarms.backend.swarms import Swarm
from matplotlib import pyplot as plt
import os
import pandas as pd
from datetime import datetime
import threading
import time



with open("python/process_files/parameters.txt", 'r') as file:
    loaded_json_str = file.read()

# Deserialize the JSON string to a dictionary
parameters = json.loads(loaded_json_str)


def write_parameters(parameters):
    #Dump and write parameters
    json_parameters = json.dumps(parameters)
    # Specify the file path
    file_path = os.getcwd() + '/python/process_files/parameters.txt'
    # Write the JSON string to the text file
    with open(file_path, 'w') as file:
        file.write(json_parameters)


    #Also write the parameters to a location in the controllers file to avoid permission issues
    controller_file_path = os.getcwd() + '/controllers/parameters.txt'
    # Write the JSON string to the text file
    with open(controller_file_path, 'w') as file:
        file.write(json_parameters)

    # time.sleep(0.5)

current_date = datetime.now().date()

#Create bounds based on calibration and the direction the gripper is facing
if parameters["type"] == "passive":
    if parameters["calibration"] == "spring" and (parameters["direction"] == "upwards" or parameters["direction"] == "downwards"):
        bounds = (np.full(parameters["slices"],parameters["min_spring_hinge"]),np.full(parameters["slices"],parameters["max_spring_hinge"]))
    elif parameters["calibration"] == "spring" and parameters["direction"] == "sideways":
        bounds = (np.full(parameters["slices"],parameters["min_spring_joint"]),np.full(parameters["slices"],parameters["max_spring_joint"]))
    elif parameters["calibration"] == "damping" and (parameters["direction"] == "upwards" or parameters["direction"] == "downwards"):
        bounds = (np.full(parameters["slices"],parameters["min_damping_hinge"]),np.full(parameters["slices"],parameters["max_damping_hinge"]))
    elif parameters["calibration"] == "damping" and parameters["direction"] == "sideways":
        bounds = (np.full(parameters["slices"],parameters["min_damping_joint"]),np.full(parameters["slices"],parameters["max_damping_joint"]))
elif parameters["type"] == "active":
    bounds = (np.full(parameters["slices"],parameters["min_torque_coefficient"]),np.full(parameters["slices"],parameters["max_torque_coefficient"]))

# Initialize the optimizer
if parameters["optimizer"] == "PSO_globalbest":
    # Initialize a Swarm object
    swarm = Swarm(
        position=np.array(parameters["initial_positions"]), 
        velocity=np.array(parameters["initial_velocities"]), 
        n_particles=parameters["PSO_n_particles"], 
        dimensions=parameters["slices"]
    )

    # Initialize the GlobalBestPSO optimizer with the Swarm object
    optimizer = GlobalBestPSO(
        n_particles=parameters["PSO_n_particles"], 
        dimensions=parameters["slices"], 
        options=parameters["PSO_options"],
        bounds = bounds,
        # velocity_clamp = (-0.1,0.1),
        # bh_strategy = 'nearest'
    )
    # Assign the initialized Swarm object to the optimizer
    optimizer.swarm = swarm

elif parameters["optimizer"] == "PSO_localbest":
    # Initialize a Swarm object
    swarm = Swarm(
        position=np.array(parameters["initial_positions"]), 
        velocity=np.array(parameters["initial_velocities"]), 
        n_particles=parameters["PSO_n_particles"], 
        dimensions=parameters["slices"],
    )

    # Initialize the LocalBestPSO optimizer with the Swarm object
    optimizer = LocalBestPSO(
        n_particles=parameters["PSO_n_particles"], 
        dimensions=parameters["slices"], 
        options=parameters["PSO_options"],
        bounds = bounds,
        # velocity_clamp = (-0.1,0.1),
        # bh_strategy = 'nearest'
    )
    # Assign the initialized Swarm object to the optimizer
    optimizer.swarm = swarm

#Initialize a list in which all the cost/fitness can be stored
all_cost = []
#Specify file path
file_path = 'python/parameters.txt'

def iteration_to_dict(swarm, solution, fitness):
    output_file = os.getcwd() + f'/python/data/raw_data_{str(parameters["direction"])}_{str(parameters["type"])}_{str(parameters["calibration"])}_{str(current_date)}.txt'  # Different output filename
    # Create DataFrame with solution and fitness data
    data_new = {}
    for i in range(len(solution)):
        data_new[f"solution_{i}"] = list(solution[i])
        data_new[f"velocity_{i}"] = list(swarm.velocity[i])
        data_new[f"fitness_{i}"] = fitness[i]

    # Check if the output file already exists
    if os.path.exists(output_file):
        # Append data to existing file
        with open(output_file, 'r') as file:
            loaded_json_str = file.read()
        # Deserialize the JSON string to a dictionary
        data = json.loads(loaded_json_str)
        data[f"Iteration_{len(data)}"] = data_new
    else:
        data = {'Iteration_0' : data_new}
        #dump parameters to dict

    #Dump and write data
    json_parameters = json.dumps(data)
    # Write the JSON string to the text file
    with open(output_file, 'w') as file:
        file.write(json_parameters)
    



#The fitness function iterates over the number of particles and does a calibration based on the selection in MAIN_FILE.oy
def fitness_func(solution):
    #clear all the communication text files
    with open(parameters["experiment_text_file"], "w") as file:
        file.write("")
    with open(parameters["overshoots_simulation_file"], "w") as file:
        file.write("")
    with open(parameters["settling_time_file"], "w") as file:
        file.write("")
    with open(parameters["angles_file"], "w") as file:
        file.write("")
    with open(parameters["experiment_text_file"], "w") as file:
        file.write("")

    fitness = np.zeros(parameters["PSO_n_particles"])

    # Define a function to calculate fitness for a single particle
    def calculate_fitness(i):
        if parameters["type"] == "passive":
            if parameters["calibration"] == "spring" and (parameters["direction"] == "upwards" or parameters["direction"] == "downwards"):
                import soft_gripper_calibration
                result = soft_gripper_calibration.springcalibration(parameters["timeout"], solution[i], parameters["damping_constants_hinge"], parameters["spring_constants_joint"], parameters["damping_constants_joint"],i)
                fitness[i] = result
            elif parameters["calibration"] == "spring" and parameters["direction"] == "sideways":
                import soft_gripper_calibration
                result = soft_gripper_calibration.springcalibration(parameters["timeout"], parameters["spring_constants_hinge"], parameters["damping_constants_hinge"], solution[i], parameters["damping_constants_joint"],i)
                fitness[i] = result
            elif parameters["calibration"] == "damping" and (parameters["direction"] == "upwards" or parameters["direction"] == "downwards"):
                import soft_gripper_calibration
                result = soft_gripper_calibration.damping_calibration(parameters["timeout"], parameters["spring_constants_hinge"], solution[i], parameters["spring_constants_joint"], parameters["damping_constants_joint"],i)
                fitness[i] = result
            elif parameters["calibration"] == "damping" and parameters["direction"] == "sideways":
                import soft_gripper_calibration
                result = soft_gripper_calibration.damping_calibration(parameters["timeout"], parameters["spring_constants_hinge"], parameters["damping_constants_hinge"], parameters["spring_constants_joint"], solution[i],i)
                fitness[i] = result
        elif parameters["type"] == "active":
            # Write torque coefficients to parameters dict and dump the dict
            string = f"torque_coefficients_particle_{i}"
            with lock:
                parameters[string] = list(solution[i])
                write_parameters(parameters)
            import soft_gripper_calibration  
            # Obtain fitness score
            result = soft_gripper_calibration.active_calibration(parameters["timeout"], parameters["spring_constants_hinge"], parameters["damping_constants_hinge"], parameters["spring_constants_joint"], parameters["damping_constants_joint"], i)
            fitness[i] = result
    # Define a function to control the number of active threads
    def thread_worker():
        while True:
            # Get the index of the next particle to calculate fitness for
            with lock:
                nonlocal next_particle_index
                particle_index = next_particle_index
                next_particle_index += 1

            # If all particles have been processed, exit
            if particle_index >= parameters["PSO_n_particles"]:
                break

            # Calculate fitness for the particle
            calculate_fitness(particle_index)

    # Create a lock to synchronize access to shared data
    lock = threading.Lock()

    # Create a list to hold the thread objects
    threads = []
    # Index of the next particle to process
    next_particle_index = 0

    while next_particle_index <= parameters["PSO_n_particles"]:

        # Start the threads
        for _ in range(max_threads):
            thread = threading.Thread(target=thread_worker)
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    iteration_to_dict(optimizer.swarm, solution, fitness)

    all_cost.append(list(fitness))
    print(f"FITNESS TEST: {fitness}")
    return fitness

# Number of threads to use
max_threads = min(parameters["PSO_n_particles"],parameters["PSO_max_threads"])

#Main function
def PSO():
    optimizer.optimize(fitness_func, parameters["PSO_iterations"])