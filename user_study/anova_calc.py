# import pandas as pd
# import numpy as np
# from scipy.stats import f_oneway

# # Example data: Test scores from three groups of students using different study methods
# df = pd.read_csv("/home/dega/projects/explainable_robotics_lm/user_study/one_way_anova.csv")

# # Create a DataFrame
# # df = pd.DataFrame(data)

# # Perform ANOVA
# f_statistic, p_value = f_oneway(df["Causal"], df["Counterfactual"], df["Contrastive"])

# # Display the results
# anova_results = pd.DataFrame({
#     "F-Statistic": [f_statistic],
#     "P-Value": [p_value]
# })

# print(anova_results)

# Re-import necessary libraries after environment reset
import pandas as pd
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd

data_long = pd.read_csv("/home/dega/projects/explainable_robotics_lm/user_study/pairwise_exp_real_values.csv")

# Fit the ANOVA model
model = ols("Situation_Awareness ~ Explanation_Style", data=data_long).fit()	

# Perform Tukey's HSD post-hoc test for pairwise comparisons
tukey_results = pairwise_tukeyhsd(data_long["Situation_Awareness"], data_long["Explanation_Style"], alpha=0.05)

# Convert the results to a DataFrame for better readability
tukey_results_df = pd.DataFrame(data=tukey_results.summary().data[1:], columns=tukey_results.summary().data[0])

print(tukey_results_df)