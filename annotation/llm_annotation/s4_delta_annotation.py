import os
import json
import time
import requests
import pandas as pd
import openai.api_resources.chat_completion

openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
openai.api_type = 'azure'
openai.api_version = '2023-05-15' # this may change in the future
deployment_name = 'gpt-35-turbo-601' #This will correspond to the custom name you chose for your deployment when you deployed a model.

no_bhv_instruction = ("Instruction: For the following user query and representation, generate a causal explanation that"
                      " justifies the activated behaviour based on the rest of the autonomous vehicle states. The"
                      " explanation should be no more than 3 sentences long. Here’s an example: Representation: "
                      "{'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then perform "
                      "the survey and finally return back to starting point', 'deploy': 'False', 'return': 'False', "
                      "'next_waypoint': 'none', 'behaviour_stage': 'none', 'next_loiter_point': 'none', "
                      "'gps_update_received': 'False', 'depth': 'on surface', 'vehicle_at_surface': 'True', "
                      "'periodic_ascend': 'False', 'waypoint_direction': 'none', 'loiter_point_direction': 'none', "
                      "'speed': 'idle', 'heading': 'south', 'name': 'henry', 'active_behaviour': 'none', 'what_if': "
                      "'none', 'predicted_behaviour': 'none', 'why_not': 'none', 'feature_justification': 'none'}"
                      " User query: Generate a causal explanation from the representation that indicates how the active "
                      "behaviour of henry is influenced by the rest of the vehicle states. Explanation: Henry currently "
                      "has no active behaviour as it has not been deployed. Consequently, the vessel remains at the "
                      "water surface, in an idle state, with a southward heading. Now do the same for the following input:")

loiter_instruction = ("Instruction: For the following user query and representation, generate a causal explanation that"
                      " justifies the activated behaviour based on the rest of the autonomous vehicle states. "
                      "The explanation should be no more than 3 sentences long. Here’s an example: Representation: "
                      "{'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then perform"
                      " the survey and finally return back to starting point', 'deploy': 'True', 'return': 'False', "
                      "'next_waypoint': 'none', 'behaviour_stage': 'none', 'next_loiter_point': 'point0', 'gps_update_received': "
                      "'False', 'depth': 'very deep', 'vehicle_at_surface': 'False', 'periodic_ascend': 'False', 'waypoint_direction':"
                      " 'none', 'loiter_point_direction': 'southeast', 'speed': 'fast', 'heading': 'southeast', 'name': "
                      "'henry', 'active_behaviour': 'maxdepth,loiter,bhv_const_depth', 'what_if': 'none', 'predicted_behaviour': "
                      "'none', 'why_not': 'none', 'feature_justification': 'none'} User query: Generate a causal explanation from"
                      " the representation that indicates how the active behaviour of henry is influenced by the rest of the"
                      " vehicle states. Explanation: Henry is currently loitering towards point 0, which is located southeast"
                      " of the vehicle while maintaining a constant depth within the configured depth tolerance. As a result,"
                      " the vessel is moving fast with southeast heading and very deep under sea level. Now do the same for the following input:")

loiter_surface_instruction = ("Instruction: For the following user query and representation, generate a causal explanation"
                              " that justifies the activated behaviour based on the rest of the autonomous vehicle states."
                              " The explanation should be no more than 3 sentences long. Here’s an example: Representation:"
                              " {'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then "
                              "perform the survey and finally return back to starting point', 'deploy': 'True', 'return': "
                              "'False', 'next_waypoint': 'none', 'behaviour_stage': 'none', 'next_loiter_point': 'point6', "
                              "'gps_update_received': 'True', 'depth': 'on surface', 'vehicle_at_surface': 'True', "
                              "'periodic_ascend': 'False', 'waypoint_direction': 'none', 'loiter_point_direction': "
                              "'northwest', 'speed': 'idle', 'heading': 'northwest', 'name': 'henry', 'active_behaviour':"
                              " 'maxdepth,loiter,bhv_periodic_surface,bhv_const_depth', 'what_if': 'none', 'predicted_behaviour':"
                              " 'none', 'why_not': 'none', 'feature_justification': 'none'} User query: Generate a causal"
                              " explanation from the representation that indicates how the active behaviour of henry is "
                              "influenced by the rest of the vehicle states. Explanation: Henry is currently en route to"
                              " point 6 in the northwest while in a loitering state. Simultaneously, it has ascended to"
                              " the water's surface and effectively transmitted an update on its GPS coordinates to command"
                              " and control. Consequently, the vessel is presently idle, at sea level, with a northwest"
                              " heading. Now do the same for the following input:")

survey_instruction = ("Instruction: For the following user query and representation, generate a causal explanation that"
                      " justifies the activated behaviour based on the rest of the autonomous vehicle states. The "
                      "explanation should be no more than 3 sentences long. Here’s an example: Representation: "
                      "{'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then perform"
                      " the survey and finally return back to starting point', 'deploy': 'True', 'return': 'False', "
                      "'next_waypoint': 'point4', 'behaviour_stage': 'in-transit', 'next_loiter_point': 'none', "
                      "'gps_update_received': 'False', 'depth': 'very deep', 'vehicle_at_surface': 'False', 'periodic_ascend':"
                      " 'False', 'waypoint_direction': 'southeast', 'loiter_point_direction': 'none', 'speed': 'very fast',"
                      " 'heading': 'northeast', 'name': 'henry', 'active_behaviour': 'maxdepth,bhv_const_depth,waypt_survey', "
                      "'what_if': 'none', 'predicted_behaviour': 'none', 'why_not': 'none', 'feature_justification': 'none'}"
                      " User query: Generate a causal explanation from the representation that indicates how the active "
                      "behaviour of henry is influenced by the rest of the vehicle states. Explanation: Henry is in "
                      "transit towards point 4 in the southeast, conducting a survey while consistently maintaining an "
                      "approved depth range. As a result, the vessel is moving very fast under sea level but with a "
                      "northeast heading as it turns around. Now do the same for the following input:")

return_instruction = ("Instruction: For the following user query and representation, generate a causal explanation that"
                      " justifies the activated behaviour based on the rest of the autonomous vehicle states. The "
                      "explanation should be no more than 3 sentences long. Here’s an example: Representation: {'objectives':"
                      " 'Loiter between points 0 to 7 until a survey objective is provided, then perform the survey and "
                      "finally return back to starting point', 'deploy': 'True', 'return': 'True', 'next_waypoint': 'starting_point',"
                      " 'behaviour_stage': 'in-transit', 'next_loiter_point': 'none', 'gps_update_received': 'False', 'depth':"
                      " 'very deep', 'vehicle_at_surface': 'False', 'periodic_ascend': 'True', 'waypoint_direction': 'northeast',"
                      " 'loiter_point_direction': 'none', 'speed': 'very fast', 'heading': 'northeast', 'name': 'henry',"
                      " 'active_behaviour': 'maxdepth,waypt_return,bhv_const_depth', 'what_if': 'none', 'predicted_behaviour':"
                      " 'none', 'why_not': 'none', 'feature_justification': 'none'} User query: Generate a causal explanation"
                      " from the representation that indicates how the active behaviour of henry is influenced by the "
                      "rest of the vehicle states. Explanation: Henry is returning swiftly to its starting point, navigating"
                      " beneath sea level with a northeast heading. As it nears the final destination, the vessel ascends"
                      " to reach the surface. Now do the same for the following input:")


class GPT3Annotator:

    def __init__(self):
        self.data = pd.read_csv("persistance/moos_ivp_csv/s4_delta_dataset_modified.csv")
        self.data = self.data.iloc[:343, :]

    @staticmethod
    def formulate_prompt(instruction, user_query, representation):
        prompt = "{} User Query: {} Representation: {} ".format(instruction, user_query, representation)
        return prompt

    def generate_annotation(self):
        for i in range(len(self.data)):
            if "none" in self.data.iloc[i, 15]:
                prompt = self.formulate_prompt(no_bhv_instruction, self.data.iloc[i, 21], self.data.iloc[i, 20])
            elif "maxdepth,loiter,bhv_const_depth" in self.data.iloc[i, 15]:
                prompt = self.formulate_prompt(loiter_instruction, self.data.iloc[i, 21], self.data.iloc[i, 20])
            elif "maxdepth,loiter,bhv_periodic_surface,bhv_const_depth" in self.data.iloc[i, 15]:
                prompt = self.formulate_prompt(loiter_surface_instruction, self.data.iloc[i, 21], self.data.iloc[i, 20])
            elif "maxdepth,bhv_const_depth,waypt_survey" in self.data.iloc[i, 15]:
                prompt = self.formulate_prompt(survey_instruction, self.data.iloc[i, 21], self.data.iloc[i, 20])
            elif "maxdepth,waypt_return,bhv_const_depth" in self.data.iloc[i, 15]:
                prompt = self.formulate_prompt(return_instruction, self.data.iloc[i, 21], self.data.iloc[i, 20])
            print(prompt)
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", engine=deployment_name, messages=[{"role": "user", "content": prompt}])
            print(response.choices[0].message.content)
            print("Done")
            explanation = response.choices[0].message.content
            self.data.at[i, "explanation"] = explanation
            time.sleep(10)
        self.save_dataset()

    def save_dataset(self):
        self.data.to_csv('persistance/moos_ivp_csv/s4_delta_dataset_modified.csv', index=False)

    def retrieve_prompts(self):
        pass


gpt3_annotator = GPT3Annotator()
gpt3_annotator.generate_annotation()
