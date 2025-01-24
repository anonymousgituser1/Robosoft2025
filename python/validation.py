#Author: Lars Hof
#Date: July 2024

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
    "font.size": 28,
    "axes.labelsize": 28,
    "axes.titlesize": 28,
    "legend.fontsize": 28,
    "xtick.labelsize": 28,
    "ytick.labelsize": 28,
    "lines.linewidth": 1.5,
    "lines.markersize": 8,
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

force_dict_webots= {
    "0": 0.0,
    "10000":0.21121229101944278,
    "20000":0.407571598495338,
    "30000":0.6047536779427027,
    "40000":0.8079305995560084,
    "50000":1.0104398211006664,
    "60000":1.2235102406611669,
    "70000":1.4392843595107907,
    "80000":1.6546990233715206 ,
    "90000":1.8925246112339253,
    "100000": 2.1140037060785235
}


passive_dynamic_data = {"0.02" : [10, 0.35],
                        "0.04" : [12, 0.425],
                        "0.06" : [13, 0.484375],
                        "0.1": [15, 0.5447916666666667]
}

passive_dynamic_webots = {"0.02" : [7, 0.365],
                        "0.04" : [8, 0.414],
                        "0.06" : [9, 0.463],
                        "0.1": [10, 0.511]
}

# Extract time and force values for real-life and Webots, converting force to kN
time_real_life = [int(t)/ 1000 for t in force_dict.keys()]
force_real_life = [v  for v in force_dict.values()]

time_webots = [int(t) / 1000 for t in force_dict_webots.keys()]
force_webots = [v for v in force_dict_webots.values()]

# Plot real-life data
plt.plot(time_real_life, force_real_life, label="Real Experiments", color='red', linestyle=line_styles[1], marker=line_markers[0])

# Plot Webots data
plt.plot(time_webots, force_webots, label="Webots Experiment", color='green', linestyle=line_styles[1], marker=line_markers[0])

# Add title and labels
plt.xlabel("Pressure (KPa)")
plt.ylabel("Force (N)")

# Add grid
plt.grid(True)

# Add legend
plt.legend(loc='upper left')


# Optionally save the plot
if save:
    plt.savefig('pressure_vs_force_comparison.pdf', bbox_inches='tight',pad_inches=0.1)
# Show plot
plt.show()

# Extract pressure values (x-axis)
mass_values = [float(m) * 1000 for m in passive_dynamic_data.keys()]

# Extract overshoots and settling times for real-life and Webots
overshoots_real_life = [v[0] for v in passive_dynamic_data.values()]
settling_time_real_life = [v[1] for v in passive_dynamic_data.values()]

overshoots_webots = [v[0] for v in passive_dynamic_webots.values()]
settling_time_webots = [v[1] for v in passive_dynamic_webots.values()]

# Define a consistent figure size for both plots
# figsize = (6, 4)

# Plot 1: Number of Overshoots
# plt.figure(figsize=figsize)
plt.plot(mass_values, overshoots_real_life, label="Real Experiments", color='red', linestyle=line_styles[1], marker=line_markers[0])
plt.plot(mass_values, overshoots_webots, label="Webots Experiment", color='green', linestyle=line_styles[1], marker=line_markers[0])

# Add title and labels
plt.xlabel("Mass (g)")
plt.ylabel("Number of Overshoots")
plt.grid(True)
plt.legend(loc='upper left')

# Save and show plot
if save:
    plt.savefig('overshoots_comparison.pdf', bbox_inches='tight', pad_inches=0.1)
plt.show()

# Plot 2: Settling Time
# plt.figure(figsize=figsize)
plt.plot(mass_values, settling_time_real_life, label="Real Experiment", color='red', linestyle=line_styles[1], marker=line_markers[0])
plt.plot(mass_values, settling_time_webots, label="Webots Experiment", color='green', linestyle=line_styles[1], marker=line_markers[0])

# Add title and labels
plt.xlabel("Mass (g)")
plt.ylabel("Settling Time (s)")
plt.grid(True)
plt.legend(loc='upper left')

# Save and show plot
if save:
    plt.savefig('settling_time_comparison.pdf', bbox_inches='tight', pad_inches=0.1)
plt.show()
