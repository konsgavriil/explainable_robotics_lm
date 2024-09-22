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
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query. 

Decision-making: 
If deploy is false and return is false, then the vehicle is idle with no activated behaviour.
If deploy is true and return is false, then the vehicle is surveying an area. 
If deploy is true and return is true, then the vehicle is returning to its starting point. 
If deploy is true, return is false, obstacle name is not equal to none, obstacle resolved is false and obstacle proximity has value nearby, close or very close, then the vehicle is surveying the area while avoiding an obstacle.
If deploy is true, return is true, obstacle name is not equal to none, obstacle resolved is false and obstacle proximity has value nearby, close or very close, then the vehicle is returning to its starting point while avoiding an obstacle.

Here's one example:

Representation: {'objective': 'Go to points 0, 1, 2 and then return to starting position.', 'deploy': 'False', 'return': 'False', 'obstacle_name': 'none', 'obstacle_proximity': 'none', 'obstacle_resolved': 'False', 'behaviour_stage': 'none', 'next_point': 'none', 'speed': 'none', 'heading': 'none', 'next_point_direction': 'none', 'obstacle_direction': 'none', 'name': 'alpha', 'active_behaviour': 'none'}

User query: What if Alpha is deployed and next_point = point0?

Explanation: If Alpha gets deployed towards point 0, it would activate its survey behaviour that configures the vehicle to move between a set of waypoints starting from point 0.

State_permutation: deploy = 'True', 'next_point': 'point0'

Do the same for the following representation: 	

"""

survey_instruction = """
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query.

Decision-making: 
If deploy is false and return is false, then the vehicle is idle with no activated behaviour.
If deploy is true and return is false, then the vehicle is surveying an area. 
If deploy is true and return is true, then the vehicle is returning to its starting point. 
If deploy is true, return is false, obstacle name is not equal to none, obstacle resolved is false and obstacle proximity has value nearby, close or very close, then the vehicle is surveying the area while avoiding an obstacle.
If deploy is true, return is true, obstacle name is not equal to none, obstacle resolved is false and obstacle proximity has value nearby, close or very close, then the vehicle is returning to its starting point while avoiding an obstacle.

Here's one example:

Representation: {'objective': 'Go to points 0, 1, 2, 3 and then return to starting position.', 'deploy': 'True', 'return': 'False', 'obstacle_name': none, 'obstacle_proximity': 'none', 'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point': 'point3', 'speed': 'very fast', 'heading': 'northwest', 'next_point_direction': 'northwest', 'obstacle_direction': 'northwest', 'name': 'alpha', 'active_behaviour': 'waypt_survey'}

User query: What if there's obstacle_a in close proximity which hasn't been avoided?

Explanation: If there was obstacle_a in close proximity, then the vehicle would continue moving towards point 3 during its survey while avoiding the obstacle.

State_permutation: obstacle_name = 'obstacle_a', 'obstacle_proximity': 'close', obstacle_resolved = 'False'

Do the same for the following representation: 

"""

survey_obs_avoid_instruction = """
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query. 

Decision-making: 
If deploy is false and return is false, then the vehicle is idle with no activated behaviour.
If deploy is true and return is false, then the vehicle is surveying an area. 
If deploy is true and return is true, then the vehicle is returning to its starting point. 
If deploy is true, return is false, obstacle name is not equal to none, obstacle resolved is false and obstacle proximity has value nearby, close or very close, then the vehicle is surveying the area while avoiding an obstacle.
If deploy is true, return is true, obstacle name is not equal to none, obstacle resolved is false and obstacle proximity has value nearby, close or very close, then the vehicle is returning to its starting point while avoiding an obstacle.

Here's one example:

Representation: {'objective': 'Go to points 0, 1, 2, 3, 4 and then return to starting position.', 'deploy': 'True', 'return': 'False', 'obstacle_name': 'obstacle_c', 'obstacle_proximity': 'very close', 'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point': 'point1', 'speed': 'very fast', 'heading': 'southeast', 'next_point_direction': 'southeast', 'obstacle_direction': 'northeast', 'name': 'alpha', 'active_behaviour': 'waypt_survey,avoid_obstacle_avoid_obstacle_c'}

User query: What if obstacle c is very far from Alpha?

Explanation: If Alpha is very far from obstacle c, it will no longer need to modify its trajectory and move directly towards point1 to continue with its survey.

State_permutation: 'obstacle_proximity': 'very far'

Do the same for the following representation: 	

"""

return_instruction = """
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query.

Decision-making: 
If deploy is false and return is false, then the vehicle is idle with no activated behaviour.
If deploy is true and return is false, then the vehicle is surveying an area. 
If deploy is true and return is true, then the vehicle is returning to its starting point. 
If deploy is true, return is false, obstacle name is not equal to none, obstacle resolved is false and obstacle proximity has value nearby, close or very close, then the vehicle is surveying the area while avoiding an obstacle.
If deploy is true, return is true, obstacle name is not equal to none, obstacle resolved is false and obstacle proximity has value nearby, close or very close, then the vehicle is returning to its starting point while avoiding an obstacle.

Here's one example:

Representation: {'objective': 'Go to points 0, 1, 2, 3, 4, 5 and then return to starting position.', 'deploy': 'True', 'return': 'True', 'obstacle_name': 'obstacle_a', 'obstacle_proximity': 'very far', 'obstacle_resolved': 'False', 'behaviour_stage': 'in-transit', 'next_point': 'pointstart', 'speed': 'max speed', 'heading': 'northwest', 'next_point_direction': 'northwest', 'obstacle_direction': 'southeast', 'name': 'alpha', 'active_behaviour': 'waypt_return'}

User query: What if Alpha stops being deployed all of a sudden?

Explanation: Alpha would interrupt its return and stay idle without any active behaviour. Additionally, obstacle A is very far from the vessel and there is no risk of collision.

State_permutation: 'deploy': 'False'

Do the same for the following representation: 	 	

"""

class GPT3Annotator:

    def __init__(self):
        self.data = pd.read_csv("persistance/moos_ivp_csv/s1_alpha/s1_alpha_dataset_cf.csv")

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
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", engine=deployment_name, messages=[{"role": "user", "content": prompt}])
            explanation = response.choices[0].message.content
            self.data.at[i, "explanation"] = explanation
            time.sleep(10)
        self.save_dataset()

    def save_dataset(self):
        self.data.to_csv('persistance/moos_ivp_csv/s1_alpha/s1_alpha_dataset_cf2.csv', index=False)

gpt3_annotator = GPT3Annotator()
gpt3_annotator.generate_annotation()