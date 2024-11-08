import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Draw sample from a distribution  
loc, scale = 2, 0.1
samples = np.random.gumbel(loc, scale, 1000)

# Apply the transformation: log(x)
# Apply the transformation: sqrt(x)
samples= np.power(samples, 2)
samples= np.power(samples, 2)
samples= np.power(samples, 2)

# samples = np.exp(samples)
# samples = np.exp(samples)


# Plot the histogram of the transformed samples
count, bins, ignored = plt.hist(samples, 100, density=True)
plt.title('Histogram of log(x)')
plt.show()