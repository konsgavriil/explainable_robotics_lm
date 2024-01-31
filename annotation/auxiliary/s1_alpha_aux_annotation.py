import json
import pandas as pd
# from util_modules.enums import MOOSIvPScenario
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder


class S1AlphaAUXAnnotator:

    def __init__(self, path):
        self.representation = {}
        self.data = pd.read_csv(path)
        self.features = self.data.iloc[:344, :13]
        self.labels = self.data.iloc[:344, 13]
        # self.explanation_arguments = self.data.iloc[:, 14:18]
        self.feature_names = self.features.columns
        # self.argument_columns = self.explanation_arguments.columns
        for feature in self.feature_names:
            self.representation[feature] = None
        self.representation["active_behaviour"] = None

        # for argument in self.argument_columns:
        #     self.representation[argument] = None
        print("Done")
        # self.dataset = pd.read_csv("persistance/moos_ivp_csv/s1_alpha_sm_training.csv")
        # self.features = self.dataset.iloc[:, :5]
        # self.labels = self.dataset.iloc[:, -1]
        # self.enc = OrdinalEncoder()
        # self.l_enc = LabelEncoder()
        # self.enc.fit(self.features)
        # X = self.enc.transform(self.features)
        # self.l_enc.fit(self.labels)
        # Y = self.l_enc.transform(self.labels)
        # self.model = NeuralNetwork(X, Y)
        # self.model.load_model()
        # self.model = self.model.classifier

    def write_representation(self):
        for i in range(len(self.features)):
            self.representation["objective"] = str(self.features.iloc[i, 0])
            self.representation["deploy"] = str(self.features.iloc[i, 1])
            self.representation["return"] = str(self.features.iloc[i, 2])
            self.representation["obstacle_name"] = str(self.features.iloc[i, 3])
            self.representation["obstacle_proximity"] = str(self.features.iloc[i, 4])
            self.representation["obstacle_resolved"] = str(self.features.iloc[i, 5])
            self.representation["behaviour_stage"] = str(self.features.iloc[i, 6])
            self.representation["next_point"] = str(self.features.iloc[i, 7])
            self.representation["speed"] = str(self.features.iloc[i, 8])
            self.representation["heading"] = str(self.features.iloc[i, 9])
            self.representation["next_point_direction"] = str(self.features.iloc[i, 10])
            self.representation["obstacle_direction"] = str(self.features.iloc[i, 11])
            self.representation["name"] = str(self.features.iloc[i, 12])
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
    #     obs_name_values_list = self.features['obstacle_name'].unique().tolist()
    #     obs_prox_values_list = self.features['obstacle_proximity'].unique().tolist()
    #     obs_res_values_list = self.features['obstacle_resolved'].unique().tolist()
    #     bhv_stage_values_list = self.features['behaviour_stage'].unique().tolist()
    #     next_point_values_list = self.features['next_point'].unique().tolist()

    #     for i in range(len(self.data)):
    #         new_row = self.data.iloc[i].copy()
    #         deploy_modified_list = [x for x in deploy_values_list if x != new_row["deploy"]]
    #         return_modified_list = [x for x in return_values_list if x != new_row["return"]]
    #         obs_name_modified_list = [x for x in obs_name_values_list if x != new_row["obstacle_name"]]
    #         obs_prox_modified_list = [x for x in obs_prox_values_list if x != new_row["obstacle_proximity"]]
    #         obs_res_modified_list = [x for x in obs_res_values_list if x != new_row["obstacle_resolved"]]
    #         # bhv_stage_modified_list = [x for x in bhv_stage_values_list if x != new_row["behaviour_stage"]]
    #         # next_point_modified_list = [x for x in next_point_values_list if x != new_row["next_point"]]

    #         for item in deploy_modified_list:
    #             new_row["what_if"] = "deploy = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

    #         for item in return_modified_list:
    #             new_row["what_if"] = "return = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

    #         for item in obs_name_modified_list:
    #             new_row["what_if"] = "obstacle_name = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

    #         for item in obs_prox_modified_list:
    #             new_row["what_if"] = "obstacle_proximity = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

    #         for item in obs_res_modified_list:
    #             new_row["what_if"] = "obstacle_resolved = {}".format(item)
    #             self.data = self.data.append(new_row, ignore_index=True)

            # for item in bhv_stage_modified_list:
            #     new_row["what_if"] = "behaviour_stage = {}".format(item)
            #     self.data = self.data.append(new_row, ignore_index=True)
            #
            # for item in next_point_modified_list:
            #     new_row["what_if"] = "next_point = {}".format(item)
            #     self.data = self.data.append(new_row, ignore_index=True)

    # def append_contrastive_argument(self):
    #     behaviour_values_list = self.labels.unique().tolist()

    #     for i in range(0, 344):
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
    #             df_cond_row = df_cond_row.iloc[:, 1:6]
    #             x = self.enc.transform(df_cond_row)
    #             c_value = self.l_enc.inverse_transform(self.model.predict(x))
    #             self.data.at[i, "predicted_behaviour"] = c_value



    def write_instruction(self, scenario, explanation_type, behaviour):
        pass

    def write_causal_query(self):
        for i in range(len(self.features)):
            user_query = ("Generate a causal explanation from the representation that indicates how the "
                          "active behaviour of alpha is influenced by the rest of the vehicle states.")
            self.data.at[i, "user_query"] = user_query

    def save_dataset(self, name):
        self.data.to_csv(name, index=False)


a = S1AlphaAUXAnnotator("persistance/moos_ivp_csv/s1_alpha_dataset_modified.csv")
# a.append_cf_argument()
# a.append_contrastive_argument()
# a.append_cf_prediction()
a.write_representation()
# a.write_causal_query()
a.save_dataset('persistance/moos_ivp_csv/s1_alpha_dataset_modified_2.csv')
