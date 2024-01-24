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

obstacle_avoidance_instruction = ("Instruction: For the following user query and representation, generate a causal"
                                  " explanation that justifies the activated behaviour based on the rest of the autonomous"
                                  " vehicle states. The explanation should be no more than 3 sentences long. Here’s an example: "
                                  "Representation:{'objective': 'Go to points 0, 1, 2 and then return to starting position.',"
                                  " 'deploy': 'True', 'return': 'False', 'obstacle_name': 'obstacle_a', 'obstacle_proximity':"
                                  " 'nearby', 'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point':"
                                  " 'point2', 'speed': 'very fast', 'heading': 'northwest', 'next_point_direction': "
                                  "'northwest', 'obstacle_direction': 'northwest', 'name': 'alpha', 'active_behaviour': "
                                  "'waypt_survey,avoid_obstacle_avoid_obstacle_a', 'what_if': 'none', 'predicted_behaviour': "
                                  "'none', 'why_not': 'none', 'feature_justification': 'none'} User query: Generate a"
                                  " causal explanation from the representation that indicates how the active behaviour "
                                  "of alpha is influenced by the rest of the vehicle states. Explanation: While in "
                                  "transit towards point 2 during its survey, alpha came across obstacle a, located "
                                  "nearby and northwest of the vehicle. As a result, alpha is moving very fast around "
                                  "the obstacle with a northwest heading. Now do the same for the following input: ")

no_bhv_instruction = ("Instruction: For the following user query and representation, generate a causal explanation "
                      "that justifies the activated behaviour based on the rest of the autonomous vehicle states."
                      " The explanation should be no more than 3 sentences long. Here’s an example: Representation:"
                      " {'objective': 'Go to points 0, 1, 2 and then return to starting position.', 'deploy': 'False',"
                      " 'return': 'False', 'obstacle_name': 'none', 'obstacle_proximity': 'none', 'obstacle_resolved': "
                      "'False', 'behaviour_stage': 'none', 'next_point': 'none', 'speed': 'none', 'heading': 'none', "
                      "'next_point_direction': 'none', 'obstacle_direction': 'none', 'name': 'alpha', 'active_behaviour':"
                      " 'none', 'what_if': 'none', 'predicted_behaviour': 'none', 'why_not': 'none', 'feature_justification':"
                      " 'none'} User query: Generate a causal explanation from the representation that indicates how the"
                      " active behaviour of alpha is influenced by the rest of the vehicle states. Explanation: Alpha "
                      "hasn’t been deployed yet. As a result, no behaviour is active and the vessel currently has no "
                      "speed or heading. Now do the same for the following input: ")

return_instruction = ("Instruction: For the following user query and representation, generate a causal explanation that"
                      " justifies the activated behaviour based on the rest of the autonomous vehicle states. The "
                      "explanation should be no more than 3 sentences long. Here’s an example: Representation: "
                      "{'objective': 'Go to points 0, 1, 2 and then return to starting position.', 'deploy': 'True', "
                      "'return': 'True', 'obstacle_name': 'obstacle_a', 'obstacle_proximity': 'nearby', "
                      "'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point': 'starting_point', "
                      "'speed': 'very fast', 'heading': 'northwest', 'next_point_direction': 'northwest', "
                      "'obstacle_direction': 'southeast', 'name': 'alpha', 'active_behaviour': 'waypt_return', "
                      "'what_if': 'none', 'predicted_behaviour': 'none', 'why_not': 'none', 'feature_justification': "
                      "'none'} User query: Generate a causal explanation from the representation that indicates how the"
                      " active behaviour of alpha is influenced by the rest of the vehicle states. Explanation: Alpha "
                      "is currently returning to its starting point with a very fast speed and a northwest heading."
                      " Even though obstacle A is located nearby to the southeast, there’s no need for obstacle "
                      "avoidance. Now do the same for the following input:")

survey_instruction = ("Instruction: For the following user query and representation, generate a causal explanation that"
                      " justifies the activated behaviour based on the rest of the autonomous vehicle states. The "
                      "explanation should be no more than 3 sentences long. Here’s an example: Representation: "
                      "{'objective': 'Go to points 0, 1, 2 and then return to starting position.', 'deploy': 'True', "
                      "'return': 'False', 'obstacle_name': 'obstacle_a', 'obstacle_proximity': 'nearby', "
                      "'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point': 'point2', 'speed': "
                      "'very fast', 'heading': 'northwest', 'next_point_direction': 'northwest', 'obstacle_direction': "
                      "'northwest', 'name': 'alpha', 'active_behaviour': 'waypt_survey', 'what_if': 'none', "
                      "'predicted_behaviour': 'none', 'why_not': 'none', 'feature_justification': 'none'} User query: "
                      "Generate a causal explanation from the representation that indicates how the active behaviour of"
                      " alpha is influenced by the rest of the vehicle states. Explanation: Alpha is currently doing a "
                      "survey moving towards point 2. Even though obstacle A  is nearby, the vessel continues its course"
                      " moving very fast with a northwest heading. Now do the same for the following input:")


class GPT3Annotator:

    def __init__(self):
        self.data = pd.read_csv("../../persistance/moos_ivp_csv/s1_alpha_dataset_modified.csv")

    @staticmethod
    def formulate_prompt(instruction, user_query, representation):
        prompt = "{} User Query: {} Representation: {} ".format(instruction, user_query, representation)
        return prompt

    def generate_annotation(self):
        for i in range(len(self.data)):
            prompt = ""
            if "avoid_obstacle_avoid_obstacle" in self.data.iloc[i, 13]:
                prompt = self.formulate_prompt(obstacle_avoidance_instruction, self.data.iloc[i, 19], self.data.iloc[i, 18])
            if "none" in self.data.iloc[i, 13]:
                prompt = self.formulate_prompt(no_bhv_instruction, self.data.iloc[i, 19], self.data.iloc[i, 18])
            elif "waypt_return" in self.data.iloc[i, 13]:
                prompt = self.formulate_prompt(return_instruction, self.data.iloc[i, 19], self.data.iloc[i, 18])
            elif "waypt_survey" in self.data.iloc[i, 13]:
                prompt = self.formulate_prompt(survey_instruction, self.data.iloc[i, 21], self.data.iloc[i, 20])
            print(prompt)
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", engine=deployment_name, messages=[{"role": "user", "content": prompt}])
            print(response.choices[0].message.content)
            print("Done")
            explanation = response.choices[0].message.content
            self.data.at[i, "explanation"] = explanation
            time.sleep(10)
        self.save_dataset()

    def save_dataset(self):
        self.data.to_csv('../../persistance/moos_ivp_csv/s1_alpha_dataset_modified.csv', index=False)

    def retrieve_prompts(self):
        pass


gpt3_annotator = GPT3Annotator()
gpt3_annotator.generate_annotation()