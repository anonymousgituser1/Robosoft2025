## Digital playground that can be used for plotting.
# No implementation to the automatic calibration routine
# Plots PSO results.
# For plotting image processing steps or validation, please go to image_processing.py

#Author: Lars Hof
#Date: January 2024

import seaborn as sns
from matplotlib import pyplot as plt
from scipy.stats import zscore
import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt
import json
import random
import time
import matplotlib.ticker as ticker
from matplotlib.ticker import FuncFormatter

save = True

with open("python/process_files/parameters.txt", 'r') as file:
    loaded_json_str = file.read()

# Deserialize the JSON string to a dictionary
parameters = json.loads(loaded_json_str)

csv_file_path = os.getcwd() + '/python/data/raw_data_downwards_passive_spring_2024-09-14.txt'
# csv_file_path = os.getcwd() + '/python/data/raw_data_downwards_passive_damping_2024-10-09.txt'
csv_file_path = os.getcwd() + '/python/data/raw_data_downwards_active_spring_2024-10-14.txt'
print(csv_file_path)
n_particles = 14
n_joint = 7

# Use LaTeX for text rendering (ensure you have LaTeX installed)
# Factors rescale the figures in x and y direction.
facx = 1.75
facy = 1.75
# Configure LaTeX settings
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 24,
    "axes.labelsize": 24,
    "axes.titlesize": 24,
    "legend.fontsize": 24,
    "xtick.labelsize": 24,
    "ytick.labelsize": 24,
    "lines.linewidth": 1,
    "lines.markersize": 3,
    "figure.figsize": (8, 6),  # Adjusted for better aspect ratio
    "axes.grid": True,  # Enable grid
    "grid.alpha": 0.3,  # Grid transparency
    "grid.linestyle": '--'  # Grid style
})
line_styles = [
    "-",      # Solid line
    "--",     # Dashed line
    "-.",     # Dash-dot line
    ":",      # Dotted line
    "solid",  # Solid line (equivalent to "-")
    "dashed", # Dashed line (equivalent to "--")
    "dashdot",# Dash-dot line (equivalent to "-.")
    "dotted", # Dotted line (equivalent to ":")
]
colors = []
random.seed(time.time())
for i in range(10):
    colors.append('#%06X' % random.randint(0, 0xFFFFFF))
colors = [
    "#1f77b4",  # Blue
    "#ff7f0e",  # Orange
    "#2ca02c",  # Green
    "#d62728",  # Red
    "#9467bd",  # Purple
    "#8c564b",  # Brown
    "#e377c2",  # Pink
    "#7f7f7f",  # Gray
    "#bcbd22",  # Olive
    "#17becf"   # Cyan
]
line_markers = [
    ".",    # Point marker
    ",",    # Pixel marker
    "o",    # Circle marker
    "v",    # Triangle down marker
    "^",    # Triangle up marker
    "<",    # Triangle left markercolumn_names
    ">",    # Triangle right marker
    "1",    # Tri down marker
    "2",    # Tri up marker
    "3",    # Tri left marker
    "4",    # Tri right marker
    "s",    # Square marker
    "p",    # Pentagon marker
    "*",    # Star marker
    "h",    # Hexagon1 marker
    "H",    # Hexagon2 marker
    "+",    # Plus marker
    "x",    # X marker
    "D",    # Diamond marker
    "d",    # Thin diamond marker
]

def data_to_csv(data, plot=True):
    solutions = []
    fitness_scores = []

   # Initialize lists to store the personal best (pbest) solutions and fitness scores for each particle
    pbest_solutions = []  # List to store lists of best solutions for each iteration
    pbest_fitness_scores = []  # List to store lists of best fitness scores for each iteration

    # Iterate through each iteration
    for iteration_key, iteration in data.items():
        # Extract the iteration number
        iteration_number = int(iteration_key.split('_')[-1])

        # Initialize solutions_iteration and fitness_scores_iteration lists
        solutions_iteration = []
        fitness_scores_iteration = []

        # Initialize temporary lists for this iteration
        current_pbest_solutions = [None] * n_particles  # List to store the best solution for each particle
        current_pbest_fitness_scores = [float('inf')] * n_particles  # List to store the best fitness for each particle

        if iteration_number >= 36:
            # Iterate through each solution in the iteration
            for solution_key, fitness in iteration.items():
                if solution_key.startswith('fitness_'):
                    # Extract the particle number
                    particle_number = int(solution_key.split('_')[-1])

                    # Check if the particle_number is within the valid range
                    if particle_number < n_particles:
                        # Extract the current fitness score and corresponding solution
                        current_fitness = fitness
                        current_solution = iteration[solution_key.replace('fitness', 'solution')]

                        # Append current solution and fitness score to their respective lists
                        solutions_iteration.append(current_solution)
                        fitness_scores_iteration.append(current_fitness)

                        # Check if the current fitness is better (lower) than the personal best fitness
                        if current_fitness < current_pbest_fitness_scores[particle_number]:
                            # Update the personal best fitness and solution for this particle
                            current_pbest_fitness_scores[particle_number] = current_fitness
                            current_pbest_solutions[particle_number] = current_solution

            # Append solutions_iteration and fitness_scores_iteration to main lists
            solutions.append(solutions_iteration)
            fitness_scores.append(fitness_scores_iteration)    
            # After processing all solutions for the iteration, append the current bests to the cumulative lists
            pbest_fitness_scores.append(current_pbest_fitness_scores)
            pbest_solutions.append(current_pbest_solutions)

    # After finding the personal best solutions, create box plots
    n_iterations = len(solutions)
    n_joint = len(solutions[0][0])

    # Create a figure with subplots for each joint (one subplot per joint)
    fig, axs = plt.subplots(n_joint, 1, figsize=(8, 8), sharex=True)

    for joint in range(0, n_joint):
        grouped_values = []  # To store lists of values for each group of iterations

        # Calculate averages and std deviations every 10 iterations (or use pbest directly if preferred)
        group_size = 10

        for iteration in range(0, n_iterations, group_size):
            spring_values = []
            for i in range(iteration, min(iteration + group_size, n_iterations)):
                for particle in range(n_particles):
                    spring_values.append(pbest_solutions[i][particle][joint])  # Use pbest solution for each particle
            grouped_values.append(spring_values)  # Append the values for the current group

        # # Create a box plot for the joint
        sns.boxplot(data=grouped_values, ax=axs[joint], fliersize=1, color="red")

        # Set custom x-tick labels for groups
        axs[joint].set_xticks(range(len(grouped_values)))  # Set tick positions
        axs[joint].set_xticklabels([f'{(i + 1) * group_size}' for i in range(len(grouped_values))])  # Group label

    plt.subplots_adjust(hspace=0.6) 
    # Set a common y-label for all subplots
    fig.text(0.05, 0.5, 'Torque Constant', va='center', rotation='vertical')

    # Set a common x-label for all subplots
    plt.xlabel('Iteration')

    plt.savefig(f'PSO_boxplots_passive_spring.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.show()


    df = pd.DataFrame(fitness_scores, dtype="float64")

    df_personal_best = df.cummin(axis=0)

    df_global_best_fitness = df_personal_best.min(axis=1)
    df_global_worst_fitness = df_personal_best.max(axis=1)

    df_personal_best["Average"] = df_personal_best.mean(axis=1)
    df_personal_best["STD"] = df_personal_best.std(axis=1)

    df_swarm_fitness = pd.DataFrame()
    df_swarm_fitness["Average"] = df.mean(axis=1)
    df_swarm_fitness["STD"] = df.std(axis=1)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)  

    # # Save the DataFrames to CSV files in the working directory + /python/data
    # df.to_csv(os.getcwd() + f'/python/data/raw_data_{str(parameters["type"])}_{str(parameters["calibration"])}.csv', index=False)
    # df_personal_best.to_csv(os.getcwd() + f'/python/data/personal_best_{str(parameters["type"])}_{str(parameters["calibration"])}.csv', index=False)
    # df_swarm_fitness.to_csv(os.getcwd() + f'/python/data/swarm_fitness_{str(parameters["type"])}_{str(parameters["calibration"])}.csv', index=False)
    # df_global_best_fitness.to_csv(os.getcwd() + f'/python/data/df_global_best_fitness_{str(parameters["type"])}_{str(parameters["calibration"])}.csv', index=False)

    # Generate a Seaborn line plot if 'plot' is True
    if plot:
        # plt.figure(figsize=(8, 6))  # Adjust the figure size if needed

        # Plot global best fitness
        sns.lineplot(data=df_global_best_fitness, label='Global best fitness', color = 'blue')

        #STD SHADED AREA
        # # Plot average swarm fitness with shaded area for standard deviation
        # sns.lineplot(data=df_swarm_fitness["Average"], label='Average swarm fitness', color='orange')
        # plt.fill_between(
        #     x=df_personal_best.index,
        #     y1=df_swarm_fitness["Average"] - df_swarm_fitness["STD"],
        #     y2=df_swarm_fitness["Average"] + df_swarm_fitness["STD"],
        #     alpha=0.2,  # Adjust the transparency of the shaded area
        #     color='orange'  # Adjust the color of the shaded area
        # )


        # Plot average particle best fitness with shaded area for standard deviation
        sns.lineplot(data=df_personal_best["Average"], label='Average particle best fitness', color='red')

        # STD Lineplot
        # sns.lineplot(data=df_personal_best["STD"], label='Standard deviation particle best fitness', color='orange')

        #SCATTER
        # Scatter all personal best points in each iteration
        # for column in df_personal_best.columns[:-2]:  # Exclude 'Average' and 'STD'
        #     plt.scatter(
        #         x=df_personal_best.index, 
        #         y=df_personal_best[column], 
        #         alpha=0.2,  # Adjust transparency to avoid overcrowding
        #         marker = 'x',
        #         s=10,             # Adjust the size of the crosses
        #         color='red'     # Set color to black for visibility
        #     )

        # sns.lineplot(data=df.mean(axis=1), label='Average particle fitness', color='red')
        for column in df:  # Exclude 'Average' and 'STD'
            plt.scatter(
                x=df.index, 
                y=df[column], 
                alpha=0.2,  # Adjust transparency to avoid overcrowding
                marker = 'x',
                s=10,             # Adjust the size of the crosses
                color='red',     # Set color to black for visibility
            )
        
        #WORST TO BEST
        # # Clip both y1 and y2 to ensure no negative values
        # y1 = df_global_best_fitness
        # y2 = df_global_worst_fitness

        # plt.fill_between(
        #     x=df_personal_best.index,
        #     y1=y1,  # Use the clipped y1
        #     y2=y2,  # Use the clipped y2
        #     alpha=0.1,  # Adjust the transparency of the shaded area
        #     color='red'  # Adjust the color of the shaded area
        # )

        # Set plot labels and title
        plt.xlabel('Iteration')
        plt.ylabel('Fitness')
        # plt.ylim(-0.1,1)

        # Display legend
        plt.legend(loc='upper right')

        # Add grid lines
        plt.grid(True, linestyle='--', alpha=0.7)

        # Remove the right and top spines for aesthetics
        sns.despine()

        # Tight layout for better spacing
        plt.tight_layout()
        
        # Set y-axis to logarithmic scale
        # plt.yscale('log')
        # plt.ylim(0,None)

        if save:
            # Save the plot as a PNG file for Overleaf (optional)
            plt.savefig(f'PSO_results_log_{str(parameters["type"])}_spring.pdf', bbox_inches='tight', pad_inches=0.1,dpi=300)

        # Show the plot
        plt.show()



def active_experiment(df):
    # Normalize actual pressure for plotting
    df['actual pressure'] = df['actual pressure'] / 10
    
    # Scatter plot of actual pressure vs force
    plt.figure()
    plt.scatter(df['actual pressure'], df['force'], marker='o', linestyle='-', color='r')
    
    # Perform polynomial fit of order 2
    coefficients = np.polyfit(df['actual pressure'], df['force'], 2)
    
    # Create a polynomial function from the coefficients
    poly_func = np.poly1d(coefficients)
    
    # Generate x values for plotting the polynomial line
    x_fit = np.linspace(df['actual pressure'].min(), df['actual pressure'].max(), 100)
    y_fit = poly_func(x_fit)
    
    # Plot the polynomial fit
    plt.plot(x_fit, y_fit, color='blue', alpha=0.7, lw=2, label='Polynomial Fit')
    
    # Configure the plot
    plt.xlabel('Actual Pressure [KPa]')
    plt.ylabel('Force (N)')
    plt.legend()
    plt.savefig(f'real_active_experiment.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.show()
    
    return coefficients  # Return coefficients for further use

# # Specify the path to the CSV file
# active_data = os.getcwd() + '/python/data/active_cal.csv'

# # Load the data into a DataFrame and perform the experiment
# if os.path.isfile(active_data):
#     df = pd.read_csv(active_data)  # Read the CSV file into a DataFrame
#     coefficients = active_experiment(df)  # Pass the DataFrame to the function

#     # Define the force dictionary
#     force_dict = {
#         "0": 0.0,
#         "10000": 0.193911,
#         "20000": 0.394035,
#         "30000": 0.615414,
#         "40000": 0.850854,
#         "50000": 1.102644,
#         "60000": 1.381248,
#         "70000": 1.684377,
#         "80000": 1.973445,
#         "90000": 2.300445,
#         "100000": 2.571528
#     }
    
#     # Calculate corresponding forces for the given pressures
#     pressure_values = np.array(list(map(int, force_dict.keys()))) / 1000  # Convert keys to float and normalize
#     calculated_forces = np.poly1d(coefficients)(pressure_values)  # Evaluate polynomial at these pressures
    
#     # Create a mapping of pressures to calculated forces
#     pressure_force_mapping = dict(zip(force_dict.keys(), calculated_forces))
    
#     print("Calculated Forces for Given Pressures:")
#     for pressure, force in pressure_force_mapping.items():
#         print(f"Pressure: {pressure} KPa, Calculated Force: {force:.6f} N")




with open(csv_file_path, 'r') as file:
    loaded_json_str = file.read()

# Deserialize the JSON string to a dictionary
data = json.loads(loaded_json_str)
data_to_csv(data, plot=True)


