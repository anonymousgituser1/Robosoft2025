# Soft Gripper Calibration and Simulation

## Introduction

Welcome to the Soft Gripper Calibration and Simulation repository, a project authored by Lars Hof in January 2024. This project focuses on conducting calibration experiments on a soft gripper with the main objective of optimizing and simulating gripper performance through careful parameter tuning.

## System Configuration

The code development and calibration routines were performed on a computer located in the DTPA lab, with the following specifications:
- **Computer Model:** dtpa-twr-002
- **Serial Number:** CZC929D5J6
- **Processor:** Intel(R) Core(TM) i7-8700 CPU @ 3.20GHz
- **Graphics:** Integrated UHD Graphics 630
- **OS:** Ubuntu 20.0

In addition to the aforementioned computer, the project code was also used on Mac OS and Windows. Webots version 2023b was used throughout this project.

## Installation

Let's start by cloning the git:

```bash
cd /DESIRED_LOCATION
git clone git@github.com:BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24.git
```

To run this project locally, ensure you have the required Python packages installed. You can install them by running the following command in your terminal:

```bash
cd /YOUR_LOCATION
pip install -r requirements.txt
```

## Usage Instructions

`MAIN_FILE.py` is the most important file for running calibration projects. In this script all the relevant parameters for the calibration routine can be set. Please read the following points carefully.

1. Open the `MAIN_FILE.py` to initiate simulations and calibration experiments. Configure parameters according to your specific requirements, with detailed comments provided for guidance.
2. Select your OS https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/a118038f49822e34f8fb46026bc9e25dca8b0071/python/MAIN_FILE.py#L30 
3. `MAIN_FILE.py` writes all calibration parameters to a dictionary accessible from Webots and other Python files. https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9cb0f9db46402089fd53b0514eaee79cf8ad226f/python/MAIN_FILE.py#L164-L170
4. The script launches an optimizer, either PSO or GA, to optimize the gripper's performance. https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9cb0f9db46402089fd53b0514eaee79cf8ad226f/python/MAIN_FILE.py#L273-L295
5. During fitness computation, the `soft_gripper_calibration.py` file is launched in the fitness computation of a proposed solution. https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9cb0f9db46402089fd53b0514eaee79cf8ad226f/python/particle_swarm_optimization.py#L57-L89
6. Inside `soft_gripper_calibration.py`, the `generate_proto.py` and `generate_world.py` files are used to create the Webots world and gripper proto, considering parameters from the optimizer and `MAIN_FILE.py`. For example, in the active calibration: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9cb0f9db46402089fd53b0514eaee79cf8ad226f/python/soft_gripper_calibration.py#L380-L383
7. The `soft_gripper_calibration.py` file then initiates Webots and conducts simulations. For example, in the active calibration: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9cb0f9db46402089fd53b0514eaee79cf8ad226f/python/soft_gripper_calibration.py#L542
8. Fitness calculations are made based on the experiment and returned to the optimizer. For example: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9cb0f9db46402089fd53b0514eaee79cf8ad226f/python/soft_gripper_calibration.py#L563-L577
9. Steps 4-8 are repeated until the maximum number of iterations is reached, and the data is saved in CSV files in the `/data` folder. Optionally, the convergence of the optimizer can be plotted. https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/86c80e09d0e813ad6ced56a045fe6f1821fd4033/python/MAIN_FILE.py#L286

## Configuration in MAIN_FILE.py

Be carefull with string inputs as they are *sensitive to capital letters*.

Before starting an automatic calibration routine, consider the following parameters in `MAIN_FILE.py`:
* The operating systems you're using: also change the path to Webots accordingly: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/86c80e09d0e813ad6ced56a045fe6f1821fd4033/python/MAIN_FILE.py#L29-L30
* In case of static passive experiments: select the masses you would like to use (in kilograms): https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/86c80e09d0e813ad6ced56a045fe6f1821fd4033/python/MAIN_FILE.py#L37
* Min and Max values for each of the parameters: the values that are selected now are derived by trial and error and initial PSO simulations, but feel free to change them: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/86c80e09d0e813ad6ced56a045fe6f1821fd4033/python/MAIN_FILE.py#L39-L57
* For passive direction: choose from upwards, downwards, or sideways. SELECT DOWNWARDS FOR ACTIVE EXPERIMENTS: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/86c80e09d0e813ad6ced56a045fe6f1821fd4033/python/MAIN_FILE.py#L66-L68
* Set calibration to spring or damping accordingly: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/86c80e09d0e813ad6ced56a045fe6f1821fd4033/python/MAIN_FILE.py#L70
* Set active or passive experiments as needed: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/86c80e09d0e813ad6ced56a045fe6f1821fd4033/python/MAIN_FILE.py#L72
* Specify the pressures that will be used in active experiments (in Pascals): https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/86c80e09d0e813ad6ced56a045fe6f1821fd4033/python/MAIN_FILE.py#L73
* Choose optimizer: PSO_globalbest PSO_localbest or GA or TEST to run a test with selected parameters. Global Best: Each particle updates its position based on the best position found by any particle in the entire swarm. Local Best: Each particle updates its position based on the best position found by its neighbors within a local subset of the swarm. GA (Genetic Algorithm): optimization algorithm inspired by natural selection and genetics. Uses selection, crossover, and mutation operations to evolve a population of potential solutions toward an optimal solution. For more information see https://pyswarms.readthedocs.io/en/latest/ and https://pygad.readthedocs.io/en/latest/ https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/86c80e09d0e813ad6ced56a045fe6f1821fd4033/python/MAIN_FILE.py#L76
* Set parameters for the Particle Swarm Optimization or GA if applicable: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/86c80e09d0e813ad6ced56a045fe6f1821fd4033/python/MAIN_FILE.py#L78-L103
* After that you can simply run the script and the other scripts will do the work for you

## Webots communication

All the parameters that are selected in the `MAIN_FILE.py` are written to a dictionary. Because of potential permission errors, this dictionary is written to two locations:
1. `../python`
2. `../controllers`

The Webots simulations are controlled from the controllers of the conducted experiment (passive/active). The controllers are used to control the robot in each of the experiments, while the supervisor controllers are used to communicate back to python and end the simulations when needed. Two way communication between Webots and Python is established as follows:
1. The controllers can get information about the simulation as command line arguments. For example: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9b59a13b9b1cec78cd49fc937ee26b0ba0886ef2/controllers/passive_exp1/passive_exp1.py#L28-L34
2. The controllers can get information about the simulation from the parameters dictionary. For example: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9b59a13b9b1cec78cd49fc937ee26b0ba0886ef2/controllers/passive_exp1/passive_exp1.py#L15-L20
3. `soft_gripper_calibration.py` can receive information from Webots through a series of text files in `../python`. For example, here the passive experiments controller writes the number of overshoots to a text file: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9b59a13b9b1cec78cd49fc937ee26b0ba0886ef2/controllers/passive_exp1/passive_exp1.py#L163-L165 and this can be read here: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9b59a13b9b1cec78cd49fc937ee26b0ba0886ef2/python/soft_gripper_calibration.py#L481-L483

All textfiles can be found in `..\python`

* The exerted force in the active experiments is written to `exerted_force.py` https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9b59a13b9b1cec78cd49fc937ee26b0ba0886ef2/controllers/supervisor_active/supervisor_active.py#L44-L46
thereafter, it can be read from python https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9b59a13b9b1cec78cd49fc937ee26b0ba0886ef2/python/soft_gripper_calibration.py#L559-L560
* Other experimental results are also saved in this fashion in the `overshoots_simulation_file.txt` and `settling_time.txt` files in the same way
* `experiment_done.txt` is either set to 'not Done' or 'Done'. When a Webots simulation is commenced, the controller writes 'not Done' to the file: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9b59a13b9b1cec78cd49fc937ee26b0ba0886ef2/controllers/passive_exp1/passive_exp1.py#L104-L107
Subsequently, the supervisor will check if the file contains 'Done':
https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9b59a13b9b1cec78cd49fc937ee26b0ba0886ef2/controllers/supervisor_passive_exp1/supervisor_passive_exp1.py#L31-L36
When the experiment is finsihed, the controller writes 'Done' to the file such that the supervisor knows it can quit the simulation: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9b59a13b9b1cec78cd49fc937ee26b0ba0886ef2/controllers/passive_exp1/passive_exp1.py#L172-L174
Python also needs to know the simulation is done. Therefore, when the supervisor quits the simulation it writes 'Ready' to `webots_image_ready.txt`
https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9b59a13b9b1cec78cd49fc937ee26b0ba0886ef2/controllers/supervisor_passive_exp1/supervisor_passive_exp1.py#L41-L44
`soft_gripper_calibration.py` checks if this file is set to 'Ready' before it continues
https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/9b59a13b9b1cec78cd49fc937ee26b0ba0886ef2/python/soft_gripper_calibration.py#L350-L355

## Plotting

* The `image_processing.py` and `plotting.py` files can be used to plot image processing steps: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/4f6b12b1ada62f9329bfdf15067512eaf0337571/python/image_processing.py#L12-L159 or optimizers results: https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/4f6b12b1ada62f9329bfdf15067512eaf0337571/python/plotting.py#L59-L106
* The `image_processing.py` script can also be used to play around with new image processing steps before implementing them into soft_gripper_calibration.py
* `histplotter.py` can be used to plot a barplot of 5 best solutions and their values in each of the hingejoints. https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/4f6b12b1ada62f9329bfdf15067512eaf0337571/python/data/histplotter.py
* The `WrongDataFixer.py` files can be used when you still want to use the printed outputs in the case of an error (to use as results). Values are copied to lists https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/4f6b12b1ada62f9329bfdf15067512eaf0337571/python/data/WrongDataFixerActive.py#L21-L34 the data is then processed to the desired format https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/4f6b12b1ada62f9329bfdf15067512eaf0337571/python/data/WrongDataFixerActive.py#L67C-L92C The data can also be used to create optimizer plots https://github.com/BaharsGit/Lars_Hof_RUG_BaIP_AY_23_24/blob/4f6b12b1ada62f9329bfdf15067512eaf0337571/python/data/WrongDataFixerActive.py#L102-L143

*These files are not part of the automatic calibration routine.*

