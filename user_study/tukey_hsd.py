import pandas as pd

from statsmodels.stats.multicomp import pairwise_tukeyhsd

import matplotlib.pyplot as plt

# Example dataset

df = pd.read_csv("/home/dega/projects/explainable_robotics_lm/user_study/bonferroni_test.csv")

# Perform Tukey's HSD test

tukey_result = pairwise_tukeyhsd(endog=df["Value"], groups=df["Group"], alpha=0.05)

# Print the result

print(tukey_result)

# Visualize the Tukey's HSD results

tukey_result.plot_simultaneous(comparison_name='A1B1', ylabel='Group')

plt.title("Tukey's HSD Test Results")

plt.show()