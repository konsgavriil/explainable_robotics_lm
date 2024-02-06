import pandas as pd
from sklearn.model_selection import train_test_split
import random
import re

class DataProcessor:

    def __init__(self, path):
        # Load your dataset, assuming it's in a CSV file
        self.df = pd.read_csv(path)

    def shuffle_split_dataset(self):
        # Shuffle the dataset randomly
        self.df = self.df.sample(frac=1, random_state=42)
        # Split the dataset into train, validation, and test sets
        train_ratio = 0.8
        validation_ratio = 0.1
        test_ratio = 0.1
        train_df, temp_df = train_test_split(self.df, test_size=1 - train_ratio, random_state=42)
        validation_df, test_df = train_test_split(temp_df, test_size=test_ratio / (test_ratio + validation_ratio), random_state=42)
        # Save the split datasets into separate CSV files
        train_df.to_csv("persistance/moos_ivp_csv/complete_datasets/counterfactual/counterfactual_train_dataset.csv", index=False)
        validation_df.to_csv("persistance/moos_ivp_csv/complete_datasets/counterfactual/counterfactual_validation_dataset.csv", index=False)
        test_df.to_csv("persistance/moos_ivp_csv/complete_datasets/counterfactual/counterfactual_test_dataset.csv", index=False)

    def separate_annotations(self):
        for index, row in self.df.iterrows():
            my_list = re.split(r'\n\s*\n', row["explanation"])
            if len(my_list) == 3:
                user_query, explanation, permutation = my_list
            else:
                continue

            if user_query == "" or user_query == "" or permutation == "":
                continue

            self.df.at[index, "explanation"] = explanation
            self.df.at[index, "user_query"] = user_query
            self.df.at[index, "state_permutation"] = permutation

        self.save_dataset("persistance/moos_ivp_csv/s1_alpha/s1_alpha_dataset_cf3.csv")

    def save_dataset(self, path):
        self.df.to_csv(path, index=False)


dp = DataProcessor("persistance/moos_ivp_csv/complete_datasets/counterfactual/counterfactual_dataset.csv")
dp.shuffle_split_dataset()
# dp.separate_annotations()
