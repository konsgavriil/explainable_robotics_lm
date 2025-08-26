import pandas as pd
from statsmodels.stats.multitest import multipletests
from itertools import combinations
from scipy.stats import ttest_ind

# Example dataset
df = pd.read_csv("/home/dega/projects/explainable_robotics_lm/user_study/bonferroni_test.csv")

# Get unique groups
groups = df['Group'].unique()

# Perform pairwise t-tests for all combinations
pairwise_pvalues = []
group_pairs = []
for g1, g2 in combinations(groups, 2):
    group1_values = df[df['Group'] == g1]['Value']
    group2_values = df[df['Group'] == g2]['Value']
    t_stat, p_value = ttest_ind(group1_values, group2_values)
    pairwise_pvalues.append(p_value)
    group_pairs.append((g1, g2))

# Apply Bonferroni correction
adjusted_results = multipletests(pairwise_pvalues, method='bonferroni')

# Display the results
results_df = pd.DataFrame({
    "Group1": [pair[0] for pair in group_pairs],
    "Group2": [pair[1] for pair in group_pairs],
    "Raw P-Value": pairwise_pvalues,
    "Adjusted P-Value": adjusted_results[1],
    "Reject Null (Bonferroni)": adjusted_results[0]
})

print(results_df)