import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm

# Create a dataframe 
df = pd.read_csv("/home/dega/projects/explainable_robotics_lm/user_study/two_way_anova.csv")

# Fit the two-way ANOVA model including interaction
model = ols('Situation_Awareness ~ C(Explanation_Style) + C(Scenario) + C(Explanation_Style):C(Scenario)', data=df).fit()

# Perform the ANOVA
anova_results = anova_lm(model)

# Display the ANOVA table
print(anova_results)
