# Soft Gripper Calibration and Simulation

## Introduction

Welcome to the Soft Gripper Calibration and Simulation repository, a project authored by Lars Hof in 2024. This project focuses on conducting calibration experiments on a soft gripper with the main objective of optimizing and simulating gripper performance through careful parameter tuning.

## System Configuration

The code development and calibration routines were performed on a computer located in the XXXX, with the following specifications:
- **Computer Model:** XXXX
- **Serial Number:** CZC929D5J6
- **Processor:** Intel(R) Core(TM) i7-8700 CPU @ 3.20GHz
- **Graphics:** Integrated UHD Graphics 630
- **OS:** Ubuntu 20.0

In addition to the aforementioned computer, the project code was also used on Mac OS and Windows. Webots version 2023b was used throughout this project.

## Installation

Let's start by cloning the git:

```bash
cd /DESIRED_LOCATION
git clone git@github.com:larshof97/Robosoft2025.git
```

To run this project locally, ensure you have the required Python packages installed. You can install them by running the following command in your terminal:

```bash
cd /YOUR_LOCATION
pip install -r requirements.txt
```

## Usage Instructions

`MAIN_FILE.py` is the most important file for running calibration projects. In this script all the relevant parameters for the calibration routine can be set. Please read the following points carefully.

1. Open the `MAIN_FILE.py` to initiate simulations and calibration experiments. Configure parameters according to your specific requirements, with detailed comments provided for guidance.
2. Select your OS
3. `MAIN_FILE.py` writes all calibration parameters to a dictionary accessible from Webots and other Python files. 
4. The script launches an optimizer, either PSO or GA, to optimize the gripper's performance. 
5. During fitness computation, the `soft_gripper_calibration.py` file is launched in the fitness computation of a proposed solution. 
6. Inside `soft_gripper_calibration.py`, the `generate_proto.py` and `generate_world.py` files are used to create the Webots world and gripper proto, considering parameters from the optimizer and `MAIN_FILE.py`. For example, in the active calibration
7. The `soft_gripper_calibration.py` file then initiates Webots and conducts simulations. For example, in the active calibration: 
8. Fitness calculations are made based on the experiment and returned to the optimizer. For example
9. Steps 4-8 are repeated until the maximum number of iterations is reached, and the data is saved in CSV files in the `/data` folder. Optionally, the convergence of the optimizer can be plotted. 

## Configuration in MAIN_FILE.py

Be carefull with string inputs as they are *sensitive to capital letters*.

Before starting an automatic calibration routine, consider the following parameters in `MAIN_FILE.py`:
* The operating systems you're using: also change the path to Webots accordingly
* In case of static passive experiments: select the masses you would like to use (in kilograms)
* Min and Max values for each of the parameters: the values that are selected now are derived by trial and error and initial PSO simulations, but feel free to change them
* For passive direction: choose from upwards, downwards, or sideways. SELECT DOWNWARDS FOR ACTIVE EXPERIMENTS 
* Set calibration to spring or damping accordingly
* Set active or passive experiments as needed
* Specify the pressures that will be used in active experiments (in Pascals)
* Choose optimizer: PSO_globalbest PSO_localbest or GA or TEST to run a test with selected parameters. Global Best: Each particle updates its position based on the best position found by any particle in the entire swarm. Local Best: Each particle updates its position based on the best position found by its neighbors within a local subset of the swarm. GA (Genetic Algorithm): optimization algorithm inspired by natural selection and genetics. Uses selection, crossover, and mutation operations to evolve a population of potential solutions toward an optimal solution. For more information see https://pyswarms.readthedocs.io/en/latest/ and https://pygad.readthedocs.io/en/latest/ 
* Set parameters for the Particle Swarm Optimization or GA if applicable
* After that you can simply run the script and the other scripts will do the work for you

## Webots communication

All the parameters that are selected in the `MAIN_FILE.py` are written to a dictionary. Because of potential permission errors, this dictionary is written to two locations:
1. `../python`
2. `../controllers`

The Webots simulations are controlled from the controllers of the conducted experiment (passive/active). The controllers are used to control the robot in each of the experiments, while the supervisor controllers are used to communicate back to python and end the simulations when needed. Two way communication between Webots and Python is established as follows:
1. The controllers can get information about the simulation as command line arguments. For example: 
2. The controllers can get information about the simulation from the parameters dictionary. For example: 
3. `soft_gripper_calibration.py` can receive information from Webots through a series of text files in `../python`. For example, here the passive experiments controller writes the number of overshoots to a text file: 

All textfiles can be found in `..\python`

* The exerted force in the active experiments is written to `exerted_force.py` 
thereafter, it can be read from python 
* Other experimental results are also saved in this fashion in the `overshoots_simulation_file.txt` and `settling_time.txt` files in the same way
* `experiment_done.txt` is either set to 'not Done' or 'Done'. When a Webots simulation is commenced, the controller writes 'not Done' to the file: 
Subsequently, the supervisor will check if the file contains 'Done':
When the experiment is finsihed, the controller writes 'Done' to the file such that the supervisor knows it can quit the simulation: 
Python also needs to know the simulation is done. Therefore, when the supervisor quits the simulation it writes 'Ready' to `webots_image_ready.txt`
`soft_gripper_calibration.py` checks if this file is set to 'Ready' before it continues

## Plotting

* The `image_processing.py` and `plotting.py` files can be used to plot image processing steps and optimizers results can be plotted in the plotting file
* The `image_processing.py` script can also be used to play around with new image processing steps before implementing them into soft_gripper_calibration.py



