import os
import json
import time
import requests
import pandas as pd
import openai.api_resources.chat_completion
from tqdm import tqdm

openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
openai.api_type = 'azure'
openai.api_version = '2023-05-15' # this may change in the future
deployment_name = 'gpt-35-turbo-601' #This will correspond to the custom name you chose for your deployment when you deployed a model.

# contrastive_instruction = ("Instruction: Given the autonomous vehicle's decision-making logic and available behaviors, along with a provided vehicle state"
#                            " representation, perform the following tasks: \n Generate five 'why-not' queries that inquire about alternative active behaviors"
#                            " the agent could exhibit based on the active behaviour in the provided representation. \n Provide three corresponding explanations"
#                            " for each query, elucidating the reasons behind the active behavior and the potential alternatives. \n Present three behavior"
#                            " permutations reflecting the potential changes in behavior described in the user queries. \n Decision-Making Rules: \n If deploy"
#                            " is false and return is false, the vehicle is idle with no activated behavior. \n If deploy is true and return is false, the vehicle"
#                            " is surveying an area. \n If deploy is true and return is true, the vehicle is returning to its starting point. \n If deploy is true,"
#                            " return is false, obstacle name is not equal to none, obstacle resolved is false, and obstacle proximity has a value nearby, close,"
#                            " or very close, then the vehicle is surveying the area while avoiding an obstacle. \n If deploy is true, return is true, obstacle"
#                            " name is not equal to none, obstacle resolved is false, and obstacle proximity has a value nearby, close, or very close, then"
#                            " the vehicle is returning to its starting point while avoiding an obstacle. \n Available Behaviors: \n 1) None \n 2) Waypt_return \n 3)" 
#                            " Waypt_survey \n 4) Waypt_survey,avoid_obstacle_avoid_obstacle_a \n 5) Waypt_survey,avoid_obstacle_avoid_obstacle_b \n" 
#                            " 6) Waypt_survey,avoid_obstacle_avoid_obstacle_c \n 7) Waypt_survey,avoid_obstacle_avoid_obstacle_c,avoid_obstacle_avoid_obstacle_e \n"
#                            " 8) waypt_survey,avoid_obstacle_avoid_obstacle_c,avoid_obstacle_avoid_obstacle_e. \n Example Representation: \n {'objective': 'Go to"
#                            " points 0, 1, 2, 3 and then return to starting position.', 'deploy': 'True', 'return': 'False', 'obstacle_name': none,"
#                            " 'obstacle_proximity': 'none', 'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point': 'point3', 'speed':"
#                            " 'very fast', 'heading': 'northwest', 'next_point_direction': 'northwest', 'obstacle_direction': 'northwest', 'name': 'alpha',"
#                            " 'active_behaviour': 'waypt_survey'} \n User Query: Why is alpha surveying an area instead of returning to its starting point?"
#                            "\n Explanation: Alpha is currently deployed to perform its objective, specifically moving towards point 3 with a northwest heading"
#                            " and at a very fast speed. To return to its starting point, it should first finish its objective or receive a command from C2."
#                            "\n Behavior Permutation: Original: waypt_survey Modified: waypt_return. \n Proceed with the same format for the next representation: \n") 	 	 	 	 	 	

contrastive_instruction = """
Instruction:
Given the autonomous vehicle's decision-making logic and available behaviors, along with a provided vehicle state representation, perform the following tasks:

1) Generate five "why-not" queries that inquire about alternative active behaviors the agent could exhibit based on the active behaviour in the provided representation.
2) Provide three corresponding explanations for each query, elucidating the reasons behind the active behavior and the potential alternatives.
3) Present three behavior permutations reflecting the potential changes in behavior described in the user queries.

Decision-Making Rules:

1) If deploy is false and return is false, the vehicle is idle with no activated behavior.
2) If deploy is true and return is false, the vehicle is surveying an area.
3) If deploy is true and return is true, the vehicle is returning to its starting point.
4) If deploy is true, return is false, obstacle name is not equal to none, obstacle resolved is false, and obstacle proximity has a value nearby, close, or very close, then the vehicle is surveying the area while avoiding an obstacle.
5) If deploy is true, return is true, obstacle name is not equal to none, obstacle resolved is false, and obstacle proximity has a value nearby, close, or very close, then the vehicle is returning to its starting point while avoiding an obstacle.

Available Behaviors:

1) None
2) Waypt_return
3) Waypt_survey
4) Waypt_survey,avoid_obstacle_avoid_obstacle_a
5) Waypt_survey,avoid_obstacle_avoid_obstacle_b
6) Waypt_survey,avoid_obstacle_avoid_obstacle_c
7) Waypt_survey,avoid_obstacle_avoid_obstacle_e
8) Waypt_survey,avoid_obstacle_avoid_obstacle_c,avoid_obstacle_avoid_obstacle_e

Example Representation: 
{'objective': 'Go to points 0, 1, 2, 3 and then return to starting position.', 'deploy': 'True', 'return': 'False', 'obstacle_name': none, 'obstacle_proximity': 'none', 'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point': 'point3', 'speed': 'very fast', 'heading': 'northwest', 'next_point_direction': 'northwest', 'obstacle_direction': 'northwest', 'name': 'alpha', 'active_behaviour': 'waypt_survey'}

User Query: 
Why is alpha not returning to its starting point instead of surveying an area?

Explanation: 
Alpha is currently deployed to perform its objective, specifically moving towards point 3 with a northwest heading and at a very fast speed. To return to its starting point, it should first finish its objective or receive a command from C2.

Behavior Permutation:
Original: waypt_survey
Modified: waypt_return

Proceed with the same format for the next representation.

"""

class GPT3Annotator:

    def __init__(self):
        self.data = pd.read_csv("persistance/moos_ivp_csv/s1_alpha/s1_alpha_dataset_contrastive.csv")

    @staticmethod
    def formulate_prompt(instruction, representation):
        prompt = "{} Representation: {} ".format(instruction, representation)
        return prompt

    def generate_annotation(self):
        for i in tqdm(range(len(self.data)), desc="Annotating", unit="iteration"):
            prompt = self.formulate_prompt(contrastive_instruction, self.data.iloc[i, 14])
            print(prompt)
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", engine=deployment_name, messages=[{"role": "user", "content": prompt}])
            print(response.choices[0].message.content)
            print("Done")
            explanation = response.choices[0].message.content
            self.data.at[i, "explanation"] = explanation
            time.sleep(10)
        self.save_dataset()

    def save_dataset(self):
        self.data.to_csv('persistance/moos_ivp_csv/s1_alpha/s1_alpha_dataset_contrastive.csv', index=False)

gpt3_annotator = GPT3Annotator()
gpt3_annotator.generate_annotation()