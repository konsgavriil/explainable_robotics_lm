import os
import json
import time
import requests
import pandas as pd
from tqdm import tqdm
import openai.api_resources.chat_completion

openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
openai.api_type = 'azure'
openai.api_version = '2023-05-15' # this may change in the future
deployment_name = 'gpt-35-turbo-601' #This will correspond to the custom name you chose for your deployment when you deployed a model.

no_bhv_instruction = """
Instruction: For the following user query and representation, generate a causal explanation that justifies the activated behaviour based on the rest of the autonomous vehicle states. The explanation should be at most 3 sentences long. 

Here's an example:

Representation:
{'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'False', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'none', 'obstacle_name': 'none', 'obstacle_proximity': 'none', 'contact_range': 'none', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'idle', 'heading': 'north', 'loiter_point_direction': 'none', 'new_loiter_area': 'False', 'obstacle_direction': 'none', 'name': 'gilda', 'active_behaviour': 'none'}

User query: 
Generate a causal explanation from the representation that indicates how the active behaviour of Gilda is influenced by the rest of the vehicle states. 	 

Explanation: 
Gilda currently has no active behaviour as it has not been deployed. Consequently, the vessel remains in an idle state, with a north heading.

Now do the same for the following input:

"""

loiter_instruction = """
Instruction: For the following user query and representation, generate a causal explanation that justifies the activated behaviour based on the rest of the autonomous vehicle states. The explanation should be at most 3 sentences long. 

Here's an example:

Representation:
{'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'point0', 'obstacle_name': 'obstacle_2', 'obstacle_proximity': 'very far', 'contact_range': 'far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'southwest', 'loiter_point_direction': 'southwest', 'new_loiter_area': 'False', 'obstacle_direction': 'southwest', 'name': 'gilda', 'active_behaviour': 'loiter'}

User query: 
Generate a causal explanation from the representation that indicates how the active behaviour of Gilda is influenced by the rest of the vehicle states. 	 

Explanation: 
Gilda currently just loiters fast towards point 0 with a southwest heading. There is currently an obstacle and another vessel at a far distance, so there’s no need to avoid those.

Now do the same for the following input:

"""

loiter_obs_avd_instruction = """
Instruction: For the following user query and representation, generate a causal explanation that justifies the activated behaviour based on the rest of the autonomous vehicle states. The explanation should be at most 3 sentences long. 

Here's an example:

Representation:
{'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'point7', 'obstacle_name': 'obstacle_2', 'obstacle_proximity': 'nearby', 'contact_range': 'nearby', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'southwest', 'loiter_point_direction': 'northwest', 'new_loiter_area': 'False', 'obstacle_direction': 'northwest', 'name': 'gilda', 'active_behaviour': 'loiter,avd_obstacles_avd_obstacles_ob_0,avd_obstacles_avd_obstacles_ob_2'}

User query: 
Generate a causal explanation from the representation that indicates how the active behaviour of Gilda is influenced by the rest of the vehicle states. 	 

Explanation: 
Gilda currently loiters fast towards point 7 with a southwest heading while avoiding obstacle 2. Before that, it also avoided obstacle 0 which was close to the current obstacle.

Now do the same for the following input: 

"""

loiter_avd_col_instruction = """
Instruction: For the following user query and representation, generate a causal explanation that justifies the activated behaviour based on the rest of the autonomous vehicle states. The explanation should be at most 3 sentences long. 

Here's an example:

Representation:
{'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'point7', 'obstacle_name': 'obstacle_0', 'obstacle_proximity': 'nearby', 'contact_range': 'close', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'northwest', 'loiter_point_direction': 'southwest', 'new_loiter_area': 'False', 'obstacle_direction': 'northwest', 'name': 'gilda', 'active_behaviour': 'loiter,avd_obstacles_avd_obstacles_ob_0,avdcol_henry'}

User query: 
Generate a causal explanation from the representation that indicates how the active behaviour of Gilda is influenced by the rest of the vehicle states. 	 

Explanation: 
Gilda is currently swiftly navigating in a loiter pattern towards point 7 with a northwest heading, avoiding obstacle 0 and ensuring collision avoidance with another nearby vessel. Before this, Gilda successfully manoeuvred to avoid obstacle 0, which was in close proximity to the current obstacle.

Now do the same for the following input: 

"""

station_keep_instruction = """
Instruction: For the following user query and representation, generate a causal explanation that justifies the activated behaviour based on the rest of the autonomous vehicle states. The explanation should be at most 3 sentences long. 

Here's an example:

Representation:
{'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'True', 'next_loiter_point': 'none', 'obstacle_name': 'obstacle_2', 'obstacle_proximity': 'very far', 'contact_range': 'very far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'moderate', 'heading': 'southeast', 'loiter_point_direction': 'none', 'new_loiter_area': 'True', 'obstacle_direction': 'southwest', 'name': 'gilda', 'active_behaviour': 'station-keep'}

User query: 
Generate a causal explanation from the representation that indicates how the active behaviour of Gilda is influenced by the rest of the vehicle states. 	 

Explanation: 
Gilda is presently maintaining its position as per a user request, awaiting further instructions. Simultaneously, both obstacle 2 and another vehicle are at a considerable distance, presenting no imminent danger.

Now do the same for the following input:

"""

return_instruction = """
Instruction: For the following user query and representation, generate a causal explanation that justifies the activated behaviour based on the rest of the autonomous vehicle states. The explanation should be at most 3 sentences long. 

Here's an example:

Representation:
{'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'True', 'station_keep': 'False', 'next_loiter_point': 'none', 'obstacle_name': 'obstacle_2', 'obstacle_proximity': 'very far', 'contact_range': 'very far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'southeast', 'loiter_point_direction': 'none', 'new_loiter_area': 'False', 'obstacle_direction': 'southwest', 'name': 'gilda', 'active_behaviour': 'waypt_return'}

User query: 
Generate a causal explanation from the representation that indicates how the active behaviour of Gilda is influenced by the rest of the vehicle states. 	 

Explanation: 
Gilda is currently returning to its starting point moving very fast, with a southeast heading and without having any obstacles or contacts in close proximity.

Now do the same for the following input:

"""

return_obs_avoid_instruction = """
Instruction: For the following user query and representation, generate a causal explanation that justifies the activated behaviour based on the rest of the autonomous vehicle states. The explanation should be at most 3 sentences long. 

Here's an example:

Representation:
{'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'True', 'station_keep': 'False', 'next_loiter_point': 'none', 'obstacle_name': 'obstacle_3', 'obstacle_proximity': 'far', 'contact_range': 'far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'northeast', 'loiter_point_direction': 'none', 'new_loiter_area': 'False', 'obstacle_direction': 'northeast', 'name': 'gilda', 'active_behaviour': 'waypt_return,avd_obstacles_avd_obstacles_ob_3'}

User query: 
Generate a causal explanation from the representation that indicates how the active behaviour of Gilda is influenced by the rest of the vehicle states. 	 

Explanation: 
Gilda is currently returning to its starting point moving fast with a northeast heading. Concurrently, it’s moving around obstacle 3 to avoid any collision. 

Now do the same for the following input:

"""


class GPT3Annotator:

    def __init__(self):
        self.data = pd.read_csv("persistance/moos_ivp_csv/m34_alpha/m34_alpha_dataset_causal.csv")

    @staticmethod
    def formulate_prompt(instruction, user_query, representation):
        prompt = "{} User Query: {} Representation: {} ".format(instruction, user_query, representation)
        return prompt

    def generate_annotation(self):
        for i in tqdm(range(len(self.data)), desc="Annotating", unit="iteration"):
            if "none" in self.data.iloc[i, 16]:
                prompt = self.formulate_prompt(no_bhv_instruction, self.data.iloc[i, 18], self.data.iloc[i, 17])
            elif "station-keep" in self.data.iloc[i, 16]:
                prompt = self.formulate_prompt(station_keep_instruction, self.data.iloc[i, 18], self.data.iloc[i, 17])
            elif "waypt_return,avd_obstacles" in self.data.iloc[i, 16]:
                prompt = self.formulate_prompt(return_obs_avoid_instruction, self.data.iloc[i, 18], self.data.iloc[i, 17])
            elif "waypt_return" in self.data.iloc[i, 16]:
                prompt = self.formulate_prompt(return_instruction, self.data.iloc[i, 18], self.data.iloc[i, 17])
            elif "avdcol_henry" in self.data.iloc[i, 16]:
                prompt = self.formulate_prompt(loiter_avd_col_instruction, self.data.iloc[i, 18], self.data.iloc[i, 17])
            elif "loiter,avd_obstacles" in self.data.iloc[i, 16]:
                prompt = self.formulate_prompt(loiter_obs_avd_instruction, self.data.iloc[i, 18], self.data.iloc[i, 17])
            elif "loiter" in self.data.iloc[i, 16]:
                prompt = self.formulate_prompt(loiter_instruction, self.data.iloc[i, 18], self.data.iloc[i, 17])
            # print(prompt)
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", engine=deployment_name, messages=[{"role": "user", "content": prompt}])
            # print(response.choices[0].message.content)
            # print("Done")
            explanation = response.choices[0].message.content
            self.data.at[i, "explanation"] = explanation
            time.sleep(10)
        self.save_dataset("persistance/moos_ivp_csv/m34_alpha/m34_alpha_dataset_causal.csv")

    def save_dataset(self, path):
        self.data.to_csv(path, index=False)


gpt3_annotator = GPT3Annotator()
gpt3_annotator.generate_annotation()