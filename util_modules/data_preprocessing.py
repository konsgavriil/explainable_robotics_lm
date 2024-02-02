import pandas as pd
from sklearn.model_selection import train_test_split
import random

class DataProcessor:

    def __init__(self):
        # Load your dataset, assuming it's in a CSV file
        self.file_path = "persistance/moos_ivp_csv/initial_llm_training_set.csv"
        self.df = pd.read_csv(self.file_path)

    def shuffle_split_dataset(self):
        # Shuffle the dataset randomly
        df = df.sample(frac=1, random_state=42)
        # Split the dataset into train, validation, and test sets
        train_ratio = 0.8
        validation_ratio = 0.1
        test_ratio = 0.1
        train_df, temp_df = train_test_split(self.df, test_size=1 - train_ratio, random_state=42)
        validation_df, test_df = train_test_split(temp_df, test_size=test_ratio / (test_ratio + validation_ratio), random_state=42)
        # Save the split datasets into separate CSV files
        train_df.to_csv("persistance/moos_ivp_csv/causal_train_dataset.csv", index=False)
        validation_df.to_csv("persistance/moos_ivp_csv/causal_validation_dataset.csv", index=False)
        test_df.to_csv("persistance/moos_ivp_csv/causal_test_dataset.csv", index=False)
