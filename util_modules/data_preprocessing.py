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
        train_ratio = 0.9
        # validation_ratio = 0.1
        # test_ratio = 0.1
        train_df, validation_df = train_test_split(self.df, test_size=1 - train_ratio, random_state=42)
        # train_df, temp_df = train_test_split(self.df, test_size=1 - train_ratio, random_state=42)
        # validation_df, test_df = train_test_split(temp_df, test_size=test_ratio / (test_ratio + validation_ratio), random_state=42)
        # Save the split datasets into separate CSV files
        train_df.to_csv("persistance/moos_ivp_csv/complete_datasets/contrastive/train.csv", index=False)
        validation_df.to_csv("persistance/moos_ivp_csv/complete_datasets/contrastive/validation.csv", index=False)
        # test_df.to_csv("persistance/moos_ivp_csv/complete_datasets/contrastive/contrastive_test_dataset.csv", index=False)

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

    # Count the number of entries that start with a newline character
    def count_new_lines(self):
        count = 0
        for index, row in self.df.iterrows():
            # if row["representation"].startswith("\n") or row["user_query"].startswith("\n") or row["explanation"].startswith("\n") or row["permutation"].startswith("\n"):

            if row["representation"].startswith("\n") or row["user_query"].startswith("\n") or row["explanation"].startswith("\n"):
                count += 1
        print(count)

    def generate_sample_dataset(self, path):
        sample_df = self.df.sample(n=10)
        sample_df.to_csv(path, index=False)


    # Removes newlines from the start of columns
    def remove_new_lines(self):            
        self.df['representation'] = self.df['representation'].str.lstrip()
        self.df['user_query'] = self.df['user_query'].str.lstrip()
        self.df['explanation'] = self.df['explanation'].str.lstrip()
        self.df['permutation'] = self.df['permutation'].str.lstrip()
        self.df['representation'] = self.df['representation'].str.rstrip()
        self.df['user_query'] = self.df['user_query'].str.rstrip()
        self.df['explanation'] = self.df['explanation'].str.rstrip()
        self.df['permutation'] = self.df['permutation'].str.rstrip()

    def remove_redundant_chars(self):
        # Replacing chars with empty strings
        for ch in ['{','}', "'", '"']:
            self.df['user_query'] = self.df['user_query'].str.replace(ch, "")
            self.df['explanation'] = self.df['explanation'].str.replace(ch, "")
            self.df['permutation'] = self.df['permutation'].str.replace(ch, "")
        # Replacing chars with other signs
        self.df['user_query'] = self.df['user_query'].str.replace(":", "=")
        self.df['permutation'] = self.df['permutation'].str.replace(":", "=")
        # Replacing capital letter Booleans
        self.df['explanation'] = self.df['explanation'].str.replace("TRUE", "True")
        self.df['user_query'] = self.df['user_query'].str.replace("TRUE", "True")
        self.df['permutation'] = self.df['permutation'].str.replace("TRUE", "True")
        self.df['explanation'] = self.df['explanation'].str.replace("FALSE", "False")
        self.df['user_query'] = self.df['user_query'].str.replace("FALSE", "False")
        self.df['permutation'] = self.df['permutation'].str.replace("FALSE", "False")

dp = DataProcessor("persistance/moos_ivp_csv/complete_datasets/contrastive/contrastive_dataset.csv")
dp.shuffle_split_dataset()
# dp.separate_annotations()
# dp.balance_mixed_dataset()
# dp.count_new_lines()
# dp.remove_redundant_chars()
# dp.remove_new_lines()
# dp.save_dataset("persistance/moos_ivp_csv/complete_datasets/contrastive/contrastive_dataset_v2.csv")