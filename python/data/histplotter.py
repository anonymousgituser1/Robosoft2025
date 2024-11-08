import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

data = {
    'damping_constants': [
        [0.00054212, 0.00072955, 0.00020214, 0.00062585, 0.00023106, 0.00097749, 0.00024569],
        [0.00018976, 0.00091147, 0.0009325, 0.00025923, 0.00083185, 0.00055615, 0.00058172],
        [0.00028557, 0.00085037, 0.00045224, 0.00055851, 0.00035973, 0.00029688, 0.00040928],
        [0.00052602, 0.0005004, 0.00024436, 0.00088349, 0.00067869, 0.00052741, 0.0001441],
        [0.00049977, 0.00024988, 0.00081731, 0.00054934, 0.00053808, 0.00025618, 0.00094005]
    ],
    'settling_time_difference': [0.005000000000055627, 0.005000000000055627, 0.005000000000055627, 0.005000000000055627, 0.005000000000055627],
    'overshoot_difference': [3.0, 3.0, 3.0, 3.0, 3.0],
    'fitness_damping_constants': [0.010000000000111253,0.010000000000111253,0.010000000000111253,0.010000000000111253,0.010000000000111253]
}


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

data = {
    'damping_constants': [
        [0.00054212, 0.00072955, 0.00020214, 0.00062585, 0.00023106, 0.00097749, 0.00024569],
        [0.00018976, 0.00091147, 0.0009325, 0.00025923, 0.00083185, 0.00055615, 0.00058172],
        [0.00028557, 0.00085037, 0.00045224, 0.00055851, 0.00035973, 0.00029688, 0.00040928],
        [0.00052602, 0.0005004, 0.00024436, 0.00088349, 0.00067869, 0.00052741, 0.0001441],
        [0.00049977, 0.00024988, 0.00081731, 0.00054934, 0.00053808, 0.00025618, 0.00094005]
    ],
    'settling_time_difference': [0.005000000000055627, 0.005000000000055627, 0.005000000000055627, 0.005000000000055627, 0.005000000000055627],
    'overshoot_difference': [3.0, 3.0, 3.0, 3.0, 3.0],
    'fitness_damping_constants': [0.010000000000111253, 0.010000000000111253, 0.010000000000111253, 0.010000000000111253, 0.010000000000111253]
}

# Set the seaborn style for a more polished appearance
sns.set(style="whitegrid")

# Create a DataFrame
df = pd.DataFrame(data['damping_constants'], columns=[f'Hinge Joint {i+1}' for i in range(len(data['damping_constants'][0]))])
df['Settling_Time_Difference'] = data['settling_time_difference']
df['Overshoot_Difference'] = data['overshoot_difference']
df['Fitness_Damping_Constants'] = data['fitness_damping_constants']

# Melt the DataFrame for easier plotting with seaborn
df_melted = pd.melt(df, id_vars=['Settling_Time_Difference', 'Overshoot_Difference', 'Fitness_Damping_Constants'],
                    var_name='Hinge_Joint', value_name='Spring_Constant')

# Create the barplot using seaborn
plt.figure(figsize=(12, 8))
ax = sns.barplot(x='Spring_Constant', y='Hinge_Joint', hue='Fitness_Damping_Constants', data=df_melted, dodge=True, palette='viridis')

# plt.title('Barplot of Spring Constants in each hinge joint for the solutions with the five best Fitness Scores')
plt.xlabel('Damping Constant')
plt.ylabel('Hinge Joints')

# Format the legend labels with less precision
formatter = FuncFormatter(lambda x, _: f'{x:.3e}')
ax.get_legend().set_title('Fitness Score')
ax.get_legend().get_title().set_fontsize('11')
ax.get_legend().get_title().set_position((-5, 0))
[ax.get_legend().get_texts()[i].set_text(formatter(float(label.get_text()))) for i, label in enumerate(ax.get_legend().get_texts())]
plt.tight_layout()
plt.savefig('damping_constants.png', dpi=300)

plt.show()


