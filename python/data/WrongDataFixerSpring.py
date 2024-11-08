# import csv
# import pandas as pd
# import numpy as np

# # Initialize variables
# particle_fitness = {}
# iteration_fitness = []

# fitness_0_all = []
# fitness_20_all = []
# fitness_40_all = []
# fitness_sum_all = []

# # Read the input text file
# with open('/Users/lars/Downloads/Github/Soft__Gripper/python/data/optimization_progress_global_0_20_40.txt', 'r') as file:
#     data = file.read()

# # Function to parse spring constants and fitness values
# lines = data.split('\n')
# particle = 0
# fitness_0 = []
# fitness_20 = []
# fitness_40 = []
# fitness_sum = []
# for line in lines:
#     if line.startswith("fitness unstimulated spring constants :  "):
#         fitness_0.append(float(line.split(":")[1].strip()))
#     if line.startswith("fitness stimulated with 0.02 spring constants :  "):
#         fitness_20.append(float(line.split(":")[1].strip()))
#     if line.startswith("fitness stimulated with 0.04 spring constants :  "):
#         fitness_40.append(float(line.split(":")[1].strip()))
#     if line.startswith("fitness sum spring constants :  "):
#         fitness_sum.append(float(line.split(":")[1].strip()))
#     if line.startswith(" SPRING calibration FINISHED !"):
#         particle += 1
#     if particle == 14:
#         particle = 0
#         fitness_0_all.append(fitness_0.copy())
#         fitness_20_all.append(fitness_20.copy())
#         fitness_40_all.append(fitness_40.copy())
#         fitness_sum_all.append(fitness_sum.copy())
#         fitness_0 = []
#         fitness_20 = []
#         fitness_40 = []
#         fitness_sum = []

# # Write to CSV file
# with open('/Users/lars/Downloads/Github/Soft__Gripper/python/data/optimization_progress_spring_upwards_0.csv', 'w', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile)
#     csvwriter.writerows(fitness_0_all)

# # Write to CSV file
# with open('/Users/lars/Downloads/Github/Soft__Gripper/python/data/optimization_progress_spring_upwards_20.csv', 'w', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile)
#     csvwriter.writerows(fitness_20_all)

# # Write to CSV file
# with open('/Users/lars/Downloads/Github/Soft__Gripper/python/data/optimization_progress_spring_upwards_40.csv', 'w', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile)
#     csvwriter.writerows(fitness_40_all)

# # Write to CSV file
# with open('/Users/lars/Downloads/Github/Soft__Gripper/python/data/optimization_progress_spring_upwards_sum.csv', 'w', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile)
#     csvwriter.writerows(fitness_sum_all)

# print("CSV file created successfully.")

import seaborn as sns
from matplotlib import pyplot as plt
from scipy.stats import zscore

import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt

csv_file_path = os.getcwd() + '/python/data/optimization_progress_spring_upwards_sum.csv'

n_particles =14
df = pd.read_csv(csv_file_path, header=None, names=[f'Particle_{i}' for i in range(1, n_particles + 1)])

# Calculate z-scores and set outliers to NaN
z_scores = np.abs(zscore(df, axis=1))
threshold = 3  # You can adjust this threshold as needed

# Set values exceeding the threshold to NaN
df[df > threshold] = np.nan

df = df.dropna()

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
df.to_csv(os.getcwd() + f'/python/data/raw_data_spring.csv', index=False)
df_personal_best.to_csv(os.getcwd() + f'/python/data/personal_best_spring.csv', index=False)
df_swarm_fitness.to_csv(os.getcwd() + f'/python/data/swarm_fitness_spring.csv', index=False)
df_global_best_fitness.to_csv(os.getcwd() + f'/python/data/df_global_best_fitness_spring.csv', index=False)

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
plt.savefig('PSO_results_passive_static_experiment.png', dpi=300)

# Show the plot
plt.show()
