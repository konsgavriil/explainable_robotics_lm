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

counterfactual_instruction = ("Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state"
                              " representation, generate three what-if queries that would change the current behaviour of the agent, three"
                              " corresponding explanations and three state permutations that indicate the representation permutations described"
                              " in the user query. Decision-making: If deploy is false and return is false, then the vehicle is idle with no activated"
                              " behaviour. If deploy is true and return is false, then the vehicle is surveying an area. If deploy is true and return is true,"
                              " then the vehicle is returning to its starting point. If deploy is true, return is false, obstacle name is not equal to none,"
                              " obstacle resolved is false and obstacle proximity has value nearby, close or very close, then the vehicle is surveying the area"
                              " while avoiding an obstacle. If deploy is true, return is true, obstacle name is not equal to none, obstacle resolved is false"
                              " and obstacle proximity has value nearby, close or very close, then the vehicle is returning to its starting point while"
                              " avoiding an obstacle. Here’s one example: Representation: {'objective': 'Go to points 0, 1, 2, 3 and then return to starting position.',"
                              " 'deploy': 'True', 'return': 'False', 'obstacle_name': none, 'obstacle_proximity': 'none', 'obstacle_resolved': 'False', 'behaviour_stage':"
                              " 'in-transit', 'next_point': 'point3', 'speed': 'very fast', 'heading': 'northwest', 'next_point_direction': 'northwest',"
                              " 'obstacle_direction': 'northwest', 'name': 'alpha', 'active_behaviour': 'waypt_survey'} User query: What if there’s obstacle_a"
                              " in close proximity which hasn’t been avoided? Explanation: If there was obstacle_a in close proximity, then the vehicle would continue"
                              " moving towards point 3 during its survey while avoiding the obstacle. State_permutation: obstacle_name = 'obstacle_a', 'obstacle_proximity':"
                              " 'close', obstacle_resolved = ‘False’ Do the same for the following representation: ") 	 	 	 	 	 	

class GPT3Annotator:

    def __init__(self):
        self.data = pd.read_csv("persistance/moos_ivp_csv/s1_alpha/s1_alpha_dataset_counterfactual.csv")

    @staticmethod
    def formulate_prompt(instruction, representation):
        prompt = "{} Representation: {} ".format(instruction, representation)
        return prompt

    def generate_annotation(self):
        for i in range(len(self.data)):
            prompt = self.formulate_prompt(counterfactual_instruction, self.data.iloc[i, 14])
            print(prompt)
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", engine=deployment_name, messages=[{"role": "user", "content": prompt}])
            print(response.choices[0].message.content)
            print("Done")
            explanation = response.choices[0].message.content
            self.data.at[i, "explanation"] = explanation
            time.sleep(10)
        self.save_dataset()

    def save_dataset(self):
        self.data.to_csv('persistance/moos_ivp_csv/s1_alpha/s1_alpha_dataset_counterfactual.csv', index=False)

    def retrieve_prompts(self):
        pass


gpt3_annotator = GPT3Annotator()
gpt3_annotator.generate_annotation()