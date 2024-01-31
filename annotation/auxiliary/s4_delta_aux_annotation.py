import json
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder

class S4AUXAnnotator:

    def __init__(self, path):
        self.representation = {}
        self.data = pd.read_csv(path)
        self.features = self.data.iloc[:343, :15]
        self.labels = self.data.iloc[:343, 15]
        # self.explanation_arguments = self.data.iloc[:342, 16:20]
        self.feature_names = self.features.columns
        # self.argument_columns = self.explanation_arguments.columns
        for feature in self.feature_names:
            self.representation[feature] = None
        self.representation["active_behaviour"] = None

        # for argument in self.argument_columns:
        #     self.representation[argument] = None
        print("Done")
        # self.dataset = pd.read_csv("persistance/moos_ivp_csv/s4_delta/s4_delta_dataset_causal.csv")
        # self.features = self.dataset.iloc[:, :9]
        # self.labels = self.dataset.iloc[:, -1]
        # self.enc = OrdinalEncoder()
        # self.l_enc = LabelEncoder()
        # self.enc.fit(self.features)
        # X = self.enc.transform(self.features)
        # self.l_enc.fit(self.labels)
        # Y = self.l_enc.transform(self.labels)
        # self.model = DTreeClassifier(X, Y)
        # self.model.load_model()
        # self.model = self.model.classifier

    def write_representation(self):
        for i in range(len(self.features)):
            self.representation["objectives"] = str(self.features.iloc[i, 0])
            self.representation["deploy"] = str(self.features.iloc[i, 1])
            self.representation["return"] = str(self.features.iloc[i, 2])
            self.representation["next_waypoint"] = str(self.features.iloc[i, 3])
            self.representation["behaviour_stage"] = str(self.features.iloc[i, 4])
            self.representation["next_loiter_point"] = str(self.features.iloc[i, 5])
            self.representation["gps_update_received"] = str(self.features.iloc[i, 6])
            self.representation["depth"] = str(self.features.iloc[i, 7])
            self.representation["vehicle_at_surface"] = str(self.features.iloc[i, 8])
            self.representation["periodic_ascend"] = str(self.features.iloc[i, 9])
            self.representation["waypoint_direction"] = str(self.features.iloc[i, 10])
            self.representation["loiter_point_direction"] = str(self.features.iloc[i, 11])
            self.representation["speed"] = str(self.features.iloc[i, 12])
            self.representation["heading"] = str(self.features.iloc[i, 13])
            self.representation["name"] = str(self.features.iloc[i, 14])
            self.representation["active_behaviour"] = str(self.labels[i])
            # self.representation["what_if"] = str(self.explanation_arguments.iloc[i, 0])
            # self.representation["predicted_behaviour"] = str(self.explanation_arguments.iloc[i, 1])
            # self.representation["why_not"] = str(self.explanation_arguments.iloc[i, 2])
            # self.representation["feature_justification"] = str(self.explanation_arguments.iloc[i, 3])
            representation = str(self.representation)
            self.data.at[i, "representation"] = representation

    # def append_cf_argument(self):
    #     deploy_values_list = self.features['deploy'].unique().tolist()
    #     return_values_list = self.features['return'].unique().tolist()
    #     next_wp_values_list = self.features['next_waypoint'].unique().tolist()
    #     bhv_stage_values_list = self.features['behaviour_stage'].unique().tolist()
    #     next_lp_values_list = self.features['next_loiter_point'].unique().tolist()
    #     gps_update_values_list = self.features['gps_update_received'].unique().tolist()
    #     depth_values_list = self.features['depth'].unique().tolist()
    #     at_surface_values_list = self.features['vehicle_at_surface'].unique().tolist()
    #     periodic_ascend_values_list = self.features['periodic_ascend'].unique().tolist()

    #     for i in range(len(self.data)):
    #         new_row = self.data.iloc[i].copy()
    #         deploy_modified_list = [x for x in deploy_values_list if x != new_row["deploy"]]
    #         return_modified_list = [x for x in return_values_list if x != new_row["return"]]
    #         next_wp_modified_list = [x for x in next_wp_values_list if x != new_row["next_waypoint"]]
    #         bhv_stage_modified_list = [x for x in bhv_stage_values_list if x != new_row["behaviour_stage"]]
    #         next_lp_modified_list = [x for x in next_lp_values_list if x != new_row["next_loiter_point"]]
    #         gps_update_modified_list = [x for x in gps_update_values_list if x != new_row["gps_update_received"]]
    #         depth_modified_list = [x for x in depth_values_list if x != new_row["depth"]]
    #         at_surface_modified_list = [x for x in at_surface_values_list if x != new_row["vehicle_at_surface"]]
    #         periodic_ascend_modified_list = [x for x in periodic_ascend_values_list if x != new_row["periodic_ascend"]]

    #         for item in deploy_modified_list:
    #             new_row["what_if"] = "deploy = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

    #         for item in return_modified_list:
    #             new_row["what_if"] = "return = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

    #         for item in next_wp_modified_list:
    #             new_row["what_if"] = "next_waypoint = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

    #         for item in bhv_stage_modified_list:
    #             new_row["what_if"] = "behaviour_stage = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

    #         for item in next_lp_modified_list:
    #             new_row["what_if"] = "next_loiter_point = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

    #         for item in gps_update_modified_list:
    #             new_row["what_if"] = "gps_update_received = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

    #         for item in depth_modified_list:
    #             new_row["what_if"] = "depth = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

    #         for item in at_surface_modified_list:
    #             new_row["what_if"] = "vehicle_at_surface = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

    #         for item in periodic_ascend_modified_list:
    #             new_row["what_if"] = "periodic_ascend = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

    # def append_contrastive_argument(self):
    #     behaviour_values_list = self.labels.unique().tolist()

    #     for i in range(0, 343):
    #         new_row = self.data.iloc[i].copy()
    #         behaviour_modified_list = [x for x in behaviour_values_list if x != new_row["ivphelm_bhv_active"]]

    #         for item in behaviour_modified_list:
    #             new_row["why_not"] = "behaviour_active = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

    # def append_cf_prediction(self):
    #     for i in range(len(self.data)):
    #         if self.data.iloc[i]["what_if"] != "none":
    #             feature_label, feature_value = self.data.iloc[i]["what_if"].split(" = ")
    #             conditional_row = self.data.iloc[i].copy()
    #             if feature_value == 'True' or feature_value == 'False':
    #                 feature_value = bool(feature_value)
    #             conditional_row[feature_label] = feature_value
    #             df_cond_row = conditional_row.to_frame()
    #             df_cond_row = df_cond_row.T
    #             df_cond_row = df_cond_row.iloc[:, 1:10]
    #             x = self.enc.transform(df_cond_row)
    #             c_value = self.l_enc.inverse_transform(self.model.predict(x))
    #             self.data.at[i, "predicted_behaviour"] = c_value

    def write_causal_query(self):
        for i in range(len(self.features)):
            user_query = ("Generate a causal explanation from the representation that indicates how the "
                          "active behaviour of henry is influenced by the rest of the vehicle states.")
            self.data.at[i, "user_query"] = user_query

    def save_dataset(self, path):
        self.data.to_csv(path, index=False)


a = S4AUXAnnotator("persistance/moos_ivp_csv/s4_delta/s4_delta_dataset_causal.csv")
# a.append_cf_prediction()
# a.append_contrastive_argument()
a.write_representation()
# a.write_causal_query()
# a.append_cf_argument()
a.save_dataset("persistance/moos_ivp_csv/s4_delta/s4_delta_dataset_causal.csv")
