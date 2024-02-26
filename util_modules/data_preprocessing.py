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
        train_df.to_csv("persistance/moos_ivp_csv/complete_datasets/contrastive/contrastive_train_dataset.csv", index=False)
        validation_df.to_csv("persistance/moos_ivp_csv/complete_datasets/contrastive/contrastive_validation_dataset.csv", index=False)
        test_df.to_csv("persistance/moos_ivp_csv/complete_datasets/contrastive/contrastive_test_dataset.csv", index=False)

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
            self.df.at[index, "behaviour_permutation"] = permutation

        self.save_dataset("persistance/moos_ivp_csv/s1_alpha/s1_alpha_dataset_contrast3.csv")

    def save_dataset(self, path):
        self.df.to_csv(path, index=False)

    def balance_mixed_dataset(self):
        num_entries = 0
        for index, row in self.df.iterrows():
            if row["user_query"].startswith("Generate"):
                num_entries += 1 
        causal_df = self.df[self.df["user_query"].str.startswith("Generate")]
        counterfactual_df = self.df[self.df["user_query"].str.startswith("What")]
        contrastive_df = self.df[self.df["user_query"].str.startswith("Why")]
        df1 = causal_df.sample(n=num_entries)
        df2 = counterfactual_df.sample(n=num_entries)
        df3 = contrastive_df.sample(n=num_entries)
        
        df1["order"] = range(0, len(df1))
        df2["order"] = range(0, len(df2))
        df3["order"] = range(0, len(df3))

        balanced_df = pd.concat([df1, df2, df3])

        sorted_df = balanced_df.sort_values(by='order')
        sorted_df = sorted_df.drop(columns=['order'])
        sorted_df = sorted_df.reset_index(drop=True)
        sorted_df.to_csv("persistance/moos_ivp_csv/complete_datasets/mixed/balanced_test_dataset.csv")

dp = DataProcessor("persistance/moos_ivp_csv/complete_datasets/mixed/test_dataset.csv")
# dp.shuffle_split_dataset()
# dp.separate_annotations()
dp.balance_mixed_dataset()