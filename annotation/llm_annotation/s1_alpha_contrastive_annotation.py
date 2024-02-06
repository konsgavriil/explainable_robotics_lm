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

none_instruction = """
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

Decision-Making Rules:
If deploy is false and return is false, the vehicle is idle with no activated behavior.
If deploy is true and return is false, the vehicle is surveying an area.
If deploy is true and return is true, the vehicle is returning to its starting point.
If deploy is true, return is false, obstacle name is not equal to none, obstacle resolved is false, and obstacle proximity has a value nearby, close, or very close, then the vehicle is surveying the area while avoiding an obstacle.
If deploy is true, return is true, obstacle name is not equal to none, obstacle resolved is false, and obstacle proximity has a value nearby, close, or very close, then the vehicle is returning to its starting point while avoiding an obstacle.

Available Behaviors:
None
Waypt_return
Waypt_survey
Waypt_survey,avoid_obstacle_avoid_obstacle_a
Waypt_survey,avoid_obstacle_avoid_obstacle_b
Waypt_survey,avoid_obstacle_avoid_obstacle_c
Waypt_survey,avoid_obstacle_avoid_obstacle_e
Waypt_survey,avoid_obstacle_avoid_obstacle_c,avoid_obstacle_avoid_obstacle_e

Here's one example:

Representation: {'objective': 'Go to points 0, 1, 2 and then return to starting position.', 'deploy': 'False', 'return': 'False', 'obstacle_name': 'none', 'obstacle_proximity': 'none', 'obstacle_resolved': 'False', 'behaviour_stage': 'none', 'next_point': 'none', 'speed': 'none', 'heading': 'none', 'next_point_direction': 'none', 'obstacle_direction': 'none', 'name': 'alpha', 'active_behaviour': 'none'}

User Query: Why is Alpha not surveying an area instead of having no active behaviour?

Explanation: Alpha needs to be deployed and have a designated point to move towards to. On the contrary, the vessel is currently idle waiting for further instructions. 

Behavior Permutation: Original: 'None', Modified: 'Waypt_survey'

Do the same for the following representation: 	

"""

survey_instruction = """
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

Decision-Making Rules:
If deploy is false and return is false, the vehicle is idle with no activated behavior.
If deploy is true and return is false, the vehicle is surveying an area.
If deploy is true and return is true, the vehicle is returning to its starting point.
If deploy is true, return is false, obstacle name is not equal to none, obstacle resolved is false, and obstacle proximity has a value nearby, close, or very close, then the vehicle is surveying the area while avoiding an obstacle.
If deploy is true, return is true, obstacle name is not equal to none, obstacle resolved is false, and obstacle proximity has a value nearby, close, or very close, then the vehicle is returning to its starting point while avoiding an obstacle.

Available Behaviors:
None
Waypt_return
Waypt_survey
Waypt_survey,avoid_obstacle_avoid_obstacle_a
Waypt_survey,avoid_obstacle_avoid_obstacle_b
Waypt_survey,avoid_obstacle_avoid_obstacle_c
Waypt_survey,avoid_obstacle_avoid_obstacle_e
Waypt_survey,avoid_obstacle_avoid_obstacle_c,avoid_obstacle_avoid_obstacle_e

Here's one example:

Representation: {'objective': 'Go to points 0, 1, 2, 3 and then return to starting position.', 'deploy': 'True', 'return': 'False', 'obstacle_name': none, 'obstacle_proximity': 'none', 'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point': 'point3', 'speed': 'very fast', 'heading': 'northwest', 'next_point_direction': 'northwest', 'obstacle_direction': 'northwest', 'name': 'alpha', 'active_behaviour': 'waypt_survey'}

User Query: Why is alpha surveying an area instead of returning to its starting point?

Explanation: Alpha is currently deployed to perform its objective, specifically moving towards point 3 with a northwest heading and at a very fast speed. To return to its starting point, it should first finish its objective or receive a command from C2.

Behavior Permutation: Original: Waypt_survey, Modified: Waypt_return

Do the same for the following representation: 	

"""

survey_obs_avoid_instruction = """	
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

Decision-Making Rules:
If deploy is false and return is false, the vehicle is idle with no activated behavior.
If deploy is true and return is false, the vehicle is surveying an area.
If deploy is true and return is true, the vehicle is returning to its starting point.
If deploy is true, return is false, obstacle name is not equal to none, obstacle resolved is false, and obstacle proximity has a value nearby, close, or very close, then the vehicle is surveying the area while avoiding an obstacle.
If deploy is true, return is true, obstacle name is not equal to none, obstacle resolved is false, and obstacle proximity has a value nearby, close, or very close, then the vehicle is returning to its starting point while avoiding an obstacle.

Available Behaviors:
None
Waypt_return
Waypt_survey
Waypt_survey,avoid_obstacle_avoid_obstacle_a
Waypt_survey,avoid_obstacle_avoid_obstacle_b
Waypt_survey,avoid_obstacle_avoid_obstacle_c
Waypt_survey,avoid_obstacle_avoid_obstacle_e
Waypt_survey,avoid_obstacle_avoid_obstacle_c,avoid_obstacle_avoid_obstacle_e

Here's one example:

Representation: {'objective': 'Go to points 0, 1, 2 and then return to starting position.', 'deploy': 'True', 'return': 'False', 'obstacle_name': 'obstacle_a', 'obstacle_proximity': 'very close', 'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point': 'point2', 'speed': 'very fast', 'heading': 'northwest', 'next_point_direction': 'northwest', 'obstacle_direction': 'northwest', 'name': 'alpha', 'active_behaviour': 'waypt_survey,avoid_obstacle_avoid_obstacle_a'}

User Query: Why is alpha surveying an area with a modified trajectory while avoiding obstacle a instead of staying idle?

Explanation: Once Alpha spots an obstacle during its survey it has the capacity to avoid the obstacle by moving around it while executing its task. It currently avoids obstacle A with a northwest heading and moving very fast. The only reason for the vessel to stay idle would be to no longer be deployed.

Behavior Permutation: Original: 'Waypt_survey,avoid_obstacle_avoid_obstacle_a', Modified: 'None'

Do the same for the following representation: 	

"""

return_instruction = """
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

Decision-Making Rules:
If deploy is false and return is false, the vehicle is idle with no activated behavior.
If deploy is true and return is false, the vehicle is surveying an area.
If deploy is true and return is true, the vehicle is returning to its starting point.
If deploy is true, return is false, obstacle name is not equal to none, obstacle resolved is false, and obstacle proximity has a value nearby, close, or very close, then the vehicle is surveying the area while avoiding an obstacle.
If deploy is true, return is true, obstacle name is not equal to none, obstacle resolved is false, and obstacle proximity has a value nearby, close, or very close, then the vehicle is returning to its starting point while avoiding an obstacle.

Available Behaviors:
None
Waypt_return
Waypt_survey
Waypt_survey,avoid_obstacle_avoid_obstacle_a
Waypt_survey,avoid_obstacle_avoid_obstacle_b
Waypt_survey,avoid_obstacle_avoid_obstacle_c
Waypt_survey,avoid_obstacle_avoid_obstacle_e
Waypt_survey,avoid_obstacle_avoid_obstacle_c,avoid_obstacle_avoid_obstacle_e

Here's one example:

Representation: {'objective': 'Go to points 0, 1, 2, 3, 4, 5 and then return to starting position.', 'deploy': 'True', 'return': 'True', 'obstacle_name': 'obstacle_a', 'obstacle_proximity': 'far', 'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point': 'pointstart', 'speed': 'very fast', 'heading': 'northwest', 'next_point_direction': 'northwest', 'obstacle_direction': 'southeast', 'name': 'alpha', 'active_behaviour': 'waypt_return'}

User Query: Why is alpha returning to its starting point instead of surveying?

Explanation: Alpha has either finished with its survey or has been asked by the operator to return to its starting point. To start another survey again, it would need further instructions from command and control.

Behavior Permutation: Original: 'Waypt_return', Modified: 'Waypt_survey'

Do the same for the following representation: 	

"""

class GPT3Annotator:

    def __init__(self):
        self.data = pd.read_csv("persistance/moos_ivp_csv/s1_alpha/s1_alpha_dataset_contrast.csv")

    @staticmethod
    def formulate_prompt(instruction, representation):
        prompt = "{} Representation: {} ".format(instruction, representation)
        return prompt

    def generate_annotation(self):
        for i in tqdm(range(len(self.data)), desc="Annotating", unit="iteration"):
            if "none" in self.data.iloc[i, 13]:
                prompt = self.formulate_prompt(none_instruction, self.data.iloc[i, 14])
            elif "waypt_return" in self.data.iloc[i, 13]:
                prompt = self.formulate_prompt(return_instruction, self.data.iloc[i, 14])
            elif "waypt_survey,avoid_obstacle" in self.data.iloc[i, 13]:
                prompt = self.formulate_prompt(survey_obs_avoid_instruction, self.data.iloc[i, 14])
            elif "waypt_survey" in self.data.iloc[i, 13]:
                prompt = self.formulate_prompt(survey_instruction, self.data.iloc[i, 14])
            # print(prompt)
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", engine=deployment_name, messages=[{"role": "user", "content": prompt}])
            # print(response.choices[0].message.content)
            # print("Done")
            explanation = response.choices[0].message.content
            self.data.at[i, "explanation"] = explanation
            time.sleep(10)
        self.save_dataset()

    def save_dataset(self):
        self.data.to_csv('persistance/moos_ivp_csv/s1_alpha/s1_alpha_dataset_contrast2.csv', index=False)

gpt3_annotator = GPT3Annotator()
gpt3_annotator.generate_annotation()