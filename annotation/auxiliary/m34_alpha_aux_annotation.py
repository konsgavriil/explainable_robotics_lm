import json
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder

class S4AUXAnnotator:

    def __init__(self, path):
        self.representation = {}
        self.data = pd.read_csv(path)
        self.features = self.data.iloc[:, :16]
        self.labels = self.data.iloc[:, 16]
        self.feature_names = self.features.columns
        for feature in self.feature_names:
            self.representation[feature] = None
        self.representation["active_behaviour"] = None
        print("Initialisation has been completed...")

    def write_representation(self):
        for i in range(len(self.features)):
            self.representation["objective"] = str(self.features.iloc[i, 0])
            self.representation["deploy"] = str(self.features.iloc[i, 1])
            self.representation["return"] = str(self.features.iloc[i, 2])
            self.representation["station_keep"] = str(self.features.iloc[i, 3])
            self.representation["next_loiter_point"] = str(self.features.iloc[i, 4])
            self.representation["obstacle_name"] = str(self.features.iloc[i, 5])
            self.representation["obstacle_proximity"] = str(self.features.iloc[i, 6])
            self.representation["contact_range"] = str(self.features.iloc[i, 7])
            self.representation["contact_resolved"] = str(self.features.iloc[i, 8])
            self.representation["collision_avoidance_mode"] = str(self.features.iloc[i, 9])
            self.representation["speed"] = str(self.features.iloc[i, 10])
            self.representation["heading"] = str(self.features.iloc[i, 11])
            self.representation["loiter_point_direction"] = str(self.features.iloc[i, 12])
            self.representation["new_loiter_area"] = str(self.features.iloc[i, 13])
            self.representation["obstacle_direction"] = str(self.features.iloc[i, 14])
            self.representation["name"] = str(self.features.iloc[i, 15])
            self.representation["active_behaviour"] = str(self.labels[i])
            representation = str(self.representation)
            self.data.at[i, "representation"] = representation

    def write_causal_query(self):
        for i in range(len(self.features)):
            user_query = ("Generate a causal explanation from the representation that indicates how the "
                          "active behaviour of Gilda is influenced by the rest of the vehicle states.")
            self.data.at[i, "user_query"] = user_query

    def save_dataset(self, path):
        self.data.to_csv(path, index=False)


a = S4AUXAnnotator("persistance/moos_ivp_csv/m34_alpha/m34_alpha_dataset_causal.csv")
a.write_representation()
a.write_causal_query()
a.save_dataset("persistance/moos_ivp_csv/m34_alpha/m34_alpha_dataset_causal_2.csv")