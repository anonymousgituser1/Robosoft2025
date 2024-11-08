import csv
import pandas as pd
import numpy as np
# import os

# # Initialize variables
# particle_fitness = {}
# iteration_fitness = []

# settling_time_all = []
# overshoots_all = []
# fitness_all = []

# # Read the input text file
# with open(os.getcwd() + '/python/data/optimization_process_global_damping.txt', 'r') as file:
#     data = file.read()

# # Function to parse spring constants and fitness values
# lines = data.split('\n')
# particle = 0
# settling_time = []
# overshoots = []
# fitness = []
# for line in lines:
#     if line.startswith("Settling Time Difference: "):
#         settling_time.append(float(line.split(":")[1].strip()))
#     if line.startswith("Overshoot Difference: "):
#         overshoots.append(float(line.split(":")[1].strip()))
#     if line.startswith("fitness damping constants :  "):
#         fitness.append(float(line.split(":")[1].strip()))
#     if line.startswith(" DAMPING calibration FINISHED !"):
#         particle += 1
#     if particle == 14:
#         particle = 0
#         settling_time_all.append(settling_time.copy())
#         overshoots_all.append(overshoots.copy())
#         fitness_all.append(fitness.copy())
#         settling_time = []
#         overshoots = []
#         fitness = []

# # Write to CSV file
# with open(os.getcwd() + '/python/data/optimization_progress_settling_time.csv', 'w', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile)
#     csvwriter.writerows(settling_time_all)

# # Write to CSV file
# with open(os.getcwd() + '/python/data/optimization_progress_overshoots.csv', 'w', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile)
#     csvwriter.writerows(overshoots_all)

# # Write to CSV file
# with open(os.getcwd() + '/python/data/optimization_progress_fitness_sum.csv', 'w', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile)
#     csvwriter.writerows(fitness_all)

# print("CSV file created successfully.")

import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd
from scipy.stats import zscore
import os

# rows = settling_time_all
# rows = overshoots_all 
# rows = fitness_all
csv_file_path = os.getcwd() + '/python/data/optimization_progress_damping_upwards_overshoots.csv'

n_particles =14
df = pd.read_csv(csv_file_path, header=None, names=[f'Particle_{i}' for i in range(1, n_particles + 1)])

# # Calculate z-scores and set outliers to NaN
# z_scores = np.abs(zscore(df, axis=1))
# threshold = 3  # You can adjust this threshold as needed

# # Set values exceeding the threshold to NaN
# df[df > threshold] = np.nan

# df = df.dropna()

# Initialize df_personal_best with default values
df_personal_best = pd.DataFrame(columns=[f'Particle_{i}' for i in range(1, n_particles + 1)])
# Initialize df_personal_best with the first row of df
df_personal_best = df.iloc[[0]].copy()

# Iterate over rows and columns, skipping the first row because it's always the lowest fitness
for i in range(1, df.shape[0]):
    for j in range(df.shape[1]):
        # if the new fitness score of a particle is lower than the current best, update it
        df_personal_best.loc[i, f'Particle_{j+1}'] = min(df.iloc[i, j], df_personal_best.iloc[:, j].min())


df_global_best_fitness = df_personal_best.min(axis=1)

df_personal_best["Average"] = df_personal_best.mean(axis=1)
df_personal_best["STD"] = df_personal_best.std(axis=1)

df_swarm_fitness = pd.DataFrame()
df_swarm_fitness["Average"] = df.mean(axis=1)
df_swarm_fitness["STD"] = df.std(axis=1)

# Save the dataframes to a CSV file in the working directory +/data
df.to_csv(os.getcwd() + f'/python/data/raw_data_damping.csv', index=False)
df_personal_best.to_csv(os.getcwd() + f'/python/data/personal_best_damping.csv', index=False)
df_swarm_fitness.to_csv(os.getcwd() + f'/python/data/swarm_fitness_damping.csv', index=False)
df_global_best_fitness.to_csv(os.getcwd() + f'/python/data/df_global_best_fitness_damping.csv', index=False)

# Create a Seaborn line plot
plt.figure(figsize=(8, 6))  # Adjust the figure size if needed

# Plot best Cost
sns.lineplot(data=df_global_best_fitness, label='Global best fitness')

# Plot average Cost
sns.lineplot(data=df_swarm_fitness["Average"], label='Average swarm fitness',color = 'orange')
# plt.fill_between(
#     x=df_personal_best.index,
#     y1=df_swarm_fitness["Average"] - df_swarm_fitness["STD"],
#     y2=df_swarm_fitness["Average"] + df_swarm_fitness["STD"],
#     alpha=0.2,  # Adjust the transparency of the shaded area
#     color='orange'  # Adjust the color of the shaded area
# )

# Plot average particle best Cost with shaded area for standard deviation
sns.lineplot(data=df_personal_best["Average"], label='Average personal best fitness',color='green')
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
plt.savefig('PSO_results_passive_dynamic_experiment_overshoots.png', dpi=300)

# Show the plot
plt.show()
