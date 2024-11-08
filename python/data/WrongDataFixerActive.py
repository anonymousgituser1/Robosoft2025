import csv
import pandas as pd
import numpy as np
import os

# # Initialize variables
# particle_fitness = {}
# iteration_fitness = []
n_particles = 14

# fitness_all = []

# # Read the input text file
# with open('/home/Lars/Documents/Soft_Gripper/python/data/active_exp_data.txt', 'r') as file:
#     data = file.read()

# # Function to parse spring constants and fitness values
# lines = data.split('\n')
# particle = 0
# fitness = []
# for line in lines:
#     if line.startswith("Fitness Pressure Constants: "):
#         if float(line.split(":")[1].strip()) > 2.571528:
#             fitness.append(2.571528)
#         else:
#             fitness.append(float(line.split(":")[1].strip()))
#         particle += 1
#     if line.startswith("TIME OUT"):
#         fitness.append(2.571528)
#         particle += 1
#     if particle == n_particles:
#         particle = 0
#         fitness_all.append(fitness.copy())
#         fitness = []

# Write to CSV file
# with open(os.getcwd() + '/python/data/particle_fitness_active.csv', 'w', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile)
#     csvwriter.writerows(fitness_all)


# print("CSV file created successfully.")

import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd
from scipy.stats import zscore

csv_file_path = os.getcwd() + '/python/data/optimization_progress_active.csv'

n_particles =14
df = pd.read_csv(csv_file_path, header=None, names=[f'Particle_{i}' for i in range(1, n_particles + 1)])

print(df.shape)

# Calculate z-scores and set outliers to NaN
z_scores = np.abs(zscore(df, axis=1))
threshold = 3  # You can adjust this threshold as needed

# Set values exceeding the threshold to NaN
df[df > threshold] = np.nan

# Replace NaN values with 2.57
df.fillna(2.571528, inplace=True)


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
df.to_csv(os.getcwd() + f'/python/data/raw_data_active.csv', index=False)
df_personal_best.to_csv(os.getcwd() + f'/python/data/personal_best_active.csv', index=False)
df_swarm_fitness.to_csv(os.getcwd() + f'/python/data/swarm_fitness_active.csv', index=False)
df_global_best_fitness.to_csv(os.getcwd() + f'/python/data/df_global_best_fitness_active.csv', index=False)



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
sns.lineplot(data=df_personal_best["Average"], label='Average particle best fitness',color='green')
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
plt.savefig('PSO_results_active_experiment.png', dpi=300)

# Show the plot
plt.show()
