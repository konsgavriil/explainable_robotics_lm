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
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query. 

Decision-making: 
If deploy is False:
Outcome: The vessel is idle.
If station_keep is True:
Outcome: The vehicle will stay in place until further notice.
If deploy is True and next_loiter_point is not 'none':
Outcome: The vehicle is loitering.
If deploy is True, next_loiter_point is not 'none', and obstacle_proximity is 'nearby' or 'close' or 'very_close':
Outcome: The vehicle is loitering while avoiding an obstacle.
If deploy is True, next_loiter_point is not 'none', and contact_range is 'close' or 'very_close':
Outcome: The vehicle is loitering while avoiding another vessel.
If deploy is True and return is True:
Outcome: The vehicle is returning to its starting point.
If deploy is True, return is True, and obstacle_proximity is 'nearby' or 'close' or 'very_close':
Outcome: The vehicle returns to its starting point while avoiding an obstacle.

Here's one example:

Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'False', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'none', 'obstacle_name': 'none', 'obstacle_proximity': 'none', 'contact_range': 'none', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'idle', 'heading': 'north', 'loiter_point_direction': 'none', 'new_loiter_area': 'False', 'obstacle_direction': 'none', 'name': 'gilda', 'active_behaviour': 'none'}
	 	
User query: What if Gilda is deployed towards point 0?

Explanation: Gilda would get configured for loitering starting from point 0 until a new loiter area is defined, the vessel is asked to return to its starting point or is asked to stay put until further notice. At all times it should also avoid any obstacles or collisions with other vehicles.

State_permutation: 'deploy': 'True', 'next_loiter_point': 'point0'

Do the same for the following representation:

"""

loiter_instruction = """
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query. 

Decision-making: 
If deploy is False:
Outcome: The vessel is idle.
If station_keep is True:
Outcome: The vehicle will stay in place until further notice.
If deploy is True and next_loiter_point is not 'none':
Outcome: The vehicle is loitering.
If deploy is True, next_loiter_point is not 'none', and obstacle_proximity is 'nearby' or 'close' or 'very_close':
Outcome: The vehicle is loitering while avoiding an obstacle.
If deploy is True, next_loiter_point is not 'none', and contact_range is 'close' or 'very_close':
Outcome: The vehicle is loitering while avoiding another vessel.
If deploy is True and return is True:
Outcome: The vehicle is returning to its starting point.
If deploy is True, return is True, and obstacle_proximity is 'nearby' or 'close' or 'very_close':
Outcome: The vehicle returns to its starting point while avoiding an obstacle.

Here's one example:

Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'point0', 'obstacle_name': 'none', 'obstacle_proximity': 'none', 'contact_range': 'very far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'northwest', 'loiter_point_direction': 'southwest', 'new_loiter_area': 'False', 'obstacle_direction': 'none', 'name': 'gilda', 'active_behaviour': 'loiter'}
	 	
User query: What if a contact was in very close proximity?

Explanation: Gilda would loiter towards point 0 while also avoiding the other vessel using the COLREGS protocol. This protocol describes how each vehicle should modify its trajectory and speed to avoid any collisions. 

State_permutation: 'contact_range': 'very close' 

Do the same for the following representation:

"""

loiter_obs_avd_instruction = """
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query. 

Decision-making: 
If deploy is False:
Outcome: The vessel is idle.
If station_keep is True:
Outcome: The vehicle will stay in place until further notice.
If deploy is True and next_loiter_point is not 'none':
Outcome: The vehicle is loitering.
If deploy is True, next_loiter_point is not 'none', and obstacle_proximity is 'nearby' or 'close' or 'very_close':
Outcome: The vehicle is loitering while avoiding an obstacle.
If deploy is True, next_loiter_point is not 'none', and contact_range is 'close' or 'very_close':
Outcome: The vehicle is loitering while avoiding another vessel.
If deploy is True and return is True:
Outcome: The vehicle is returning to its starting point.
If deploy is True, return is True, and obstacle_proximity is 'nearby' or 'close' or 'very_close':
Outcome: The vehicle returns to its starting point while avoiding an obstacle.

Here's one example:

Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'point0', 'obstacle_name': 'obstacle_2', 'obstacle_proximity': 'close', 'contact_range': 'nearby', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'northwest', 'loiter_point_direction': 'northwest', 'new_loiter_area': 'False', 'obstacle_direction': 'southwest', 'name': 'gilda', 'active_behaviour': 'loiter,avd_obstacles_avd_obstacles_ob_2'}
	 	
User query: What if the obstacle was very far?

Explanation: Gilda will seamlessly proceed towards point 0 without requiring any trajectory adjustments to navigate around obstacles, followed by engaging in loitering around multiple waypoints.

State_permutation: 'obstacle_proximity': 'very_far'

Do the same for the following representation:

"""

loiter_avd_col_instruction = """
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query. 

Decision-making: 
If deploy is False:
Outcome: The vessel is idle.
If station_keep is True:
Outcome: The vehicle will stay in place until further notice.
If deploy is True and next_loiter_point is not 'none':
Outcome: The vehicle is loitering.
If deploy is True, next_loiter_point is not 'none', and obstacle_proximity is 'nearby' or 'close' or 'very_close':
Outcome: The vehicle is loitering while avoiding an obstacle.
If deploy is True, next_loiter_point is not 'none', and contact_range is 'close' or 'very_close':
Outcome: The vehicle is loitering while avoiding another vessel.
If deploy is True and return is True:
Outcome: The vehicle is returning to its starting point.
If deploy is True, return is True, and obstacle_proximity is 'nearby' or 'close' or 'very_close':
Outcome: The vehicle returns to its starting point while avoiding an obstacle.

Here's one example:

Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'point7', 'obstacle_name': 'obstacle_0', 'obstacle_proximity': 'nearby', 'contact_range': 'close', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'northwest', 'loiter_point_direction': 'southwest', 'new_loiter_area': 'False', 'obstacle_direction': 'northwest', 'name': 'gilda', 'active_behaviour': 'loiter,avdcol_henry'}
	 	
User query: What if the operator commands the vessel to stay in place?

Explanation: Gilda would immediately activate its station-keeping staying idle. The other vessel would then need to detect this and adjust its trajectory to avoid the collision.

State_permutation: 'station_keep': 'True'

Do the same for the following representation:

"""

station_keep_instruction = """
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query. 

Decision-making: 
If deploy is False:
Outcome: The vessel is idle.
If station_keep is True:
Outcome: The vehicle will stay in place until further notice.
If deploy is True and next_loiter_point is not 'none':
Outcome: The vehicle is loitering.
If deploy is True, next_loiter_point is not 'none', and obstacle_proximity is 'nearby' or 'close' or 'very_close':
Outcome: The vehicle is loitering while avoiding an obstacle.
If deploy is True, next_loiter_point is not 'none', and contact_range is 'close' or 'very_close':
Outcome: The vehicle is loitering while avoiding another vessel.
If deploy is True and return is True:
Outcome: The vehicle is returning to its starting point.
If deploy is True, return is True, and obstacle_proximity is 'nearby' or 'close' or 'very_close':
Outcome: The vehicle returns to its starting point while avoiding an obstacle.

Here's one example:

Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'True', 'next_loiter_point': 'none', 'obstacle_name': 'obstacle_2', 'obstacle_proximity': 'very far', 'contact_range': 'far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'moderate', 'heading': 'southeast', 'loiter_point_direction': 'none', 'new_loiter_area': 'False', 'obstacle_direction': 'southwest', 'name': 'gilda', 'active_behaviour': 'station-keep'}
	 	
User query: What if the operator wants to end the mission?

Explanation: Gilda would start moving again with a heading towards its starting point. At the moment all obstacles and contacts are far away and no avoidance is necessary.

State_permutation: 'station_keep': 'False', return = 'True'

Do the same for the following representation:

"""

return_instruction = """
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query. 

Decision-making: 
If deploy is False:
Outcome: The vessel is idle.
If station_keep is True:
Outcome: The vehicle will stay in place until further notice.
If deploy is True and next_loiter_point is not 'none':
Outcome: The vehicle is loitering.
If deploy is True, next_loiter_point is not 'none', and obstacle_proximity is 'nearby' or 'close' or 'very_close':
Outcome: The vehicle is loitering while avoiding an obstacle.
If deploy is True, next_loiter_point is not 'none', and contact_range is 'close' or 'very_close':
Outcome: The vehicle is loitering while avoiding another vessel.
If deploy is True and return is True:
Outcome: The vehicle is returning to its starting point.
If deploy is True, return is True, and obstacle_proximity is 'nearby' or 'close' or 'very_close':
Outcome: The vehicle returns to its starting point while avoiding an obstacle.

Here's one example:

Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'True', 'station_keep': 'False', 'next_loiter_point': 'none', 'obstacle_name': 'obstacle_2', 'obstacle_proximity': 'very far', 'contact_range': 'far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'low', 'heading': 'southeast', 'loiter_point_direction': 'none', 'new_loiter_area': 'False', 'obstacle_direction': 'southwest', 'name': 'gilda', 'active_behaviour': 'waypt_return'}
	 	
User query: What if the vessel stops being deployed?

Explanation: Gilda would stay idle without any active behaviour, since it's currently not performing any task and there's no need to avoid obstacles or other vessels.

State_permutation: deploy': 'False'

Do the same for the following representation:

"""

return_obs_avoid_instruction = """
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query. 

Decision-making: 
If deploy is False:
Outcome: The vessel is idle.
If station_keep is True:
Outcome: The vehicle will stay in place until further notice.
If deploy is True and next_loiter_point is not 'none':
Outcome: The vehicle is loitering.
If deploy is True, next_loiter_point is not 'none', and obstacle_proximity is 'nearby' or 'close' or 'very_close':
Outcome: The vehicle is loitering while avoiding an obstacle.
If deploy is True, next_loiter_point is not 'none', and contact_range is 'close' or 'very_close':
Outcome: The vehicle is loitering while avoiding another vessel.
If deploy is True and return is True:
Outcome: The vehicle is returning to its starting point.
If deploy is True, return is True, and obstacle_proximity is 'nearby' or 'close' or 'very_close':
Outcome: The vehicle returns to its starting point while avoiding an obstacle.

Here's one example:

Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'True', 'station_keep': 'False', 'next_loiter_point': 'none', 'obstacle_name': 'obstacle_0', 'obstacle_proximity': 'close', 'contact_range': 'far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'southeast', 'loiter_point_direction': 'none', 'new_loiter_area': 'False', 'obstacle_direction': 'northeast', 'name': 'gilda', 'active_behaviour': 'waypt_return,avd_obstacles_avd_obstacles_ob_0'}
	 	
User query: What if Gilda stops moving towards its starting point and instead moves towards loiter point 1?

Explanation: Gilda would switch from returning to base for pick up to loitering around a set of waypoints starting from point 1. It would also have to continue avoiding obstacle 0, since it’s in close proximity

State_permutation: 'return': 'False', 'next_loiter_point': point1' 

Do the same for the following representation:

"""


class GPT3Annotator:

    def __init__(self):
        self.data = pd.read_csv("persistance/moos_ivp_csv/m34_alpha/m34_alpha_dataset_counterfactual.csv")

    @staticmethod
    def formulate_prompt(instruction, representation):
        prompt = "{} Representation: {} ".format(instruction, representation)
        return prompt

    def generate_annotation(self):
        for i in tqdm(range(len(self.data)), desc="Annotating", unit="iteration"):
            if "none" in self.data.iloc[i, 16]:
                prompt = self.formulate_prompt(no_bhv_instruction, self.data.iloc[i, 17])
            elif "station-keep" in self.data.iloc[i, 16]:
                prompt = self.formulate_prompt(station_keep_instruction, self.data.iloc[i, 17])
            elif "waypt_return,avd_obstacles" in self.data.iloc[i, 16]:
                prompt = self.formulate_prompt(return_obs_avoid_instruction, self.data.iloc[i, 17])
            elif "waypt_return" in self.data.iloc[i, 16]:
                prompt = self.formulate_prompt(return_instruction, self.data.iloc[i, 17])
            elif "avdcol_henry" in self.data.iloc[i, 16]:
                prompt = self.formulate_prompt(loiter_avd_col_instruction, self.data.iloc[i, 17])
            elif "loiter,avd_obstacles" in self.data.iloc[i, 16]:
                prompt = self.formulate_prompt(loiter_obs_avd_instruction, self.data.iloc[i, 17])
            elif "loiter" in self.data.iloc[i, 16]:
                prompt = self.formulate_prompt(loiter_instruction, self.data.iloc[i, 17])
            # print(prompt)
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", engine=deployment_name, messages=[{"role": "user", "content": prompt}])
            # print(response.choices[0].message.content)
            # print("Done")
            explanation = response.choices[0].message.content
            self.data.at[i, "explanation"] = explanation
            time.sleep(10)
        self.save_dataset("persistance/moos_ivp_csv/m34_alpha/m34_alpha_dataset_counterfactual_2.csv")

    def save_dataset(self, path):
        self.data.to_csv(path, index=False)


gpt3_annotator = GPT3Annotator()
gpt3_annotator.generate_annotation()