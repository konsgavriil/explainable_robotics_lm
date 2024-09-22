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
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

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

Available Behaviors:
None
Loiter
Station-keep
Return
Loiter,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_0
loiter,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_3
Loiter,avd_obstacles_avd_obstacles_ob_4
loiter,avd_obstacles_avd_obstacles_ob_0,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_2,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_0,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3
Loiter,avd_obstacles_avd_obstacles_ob_3,avd_obstacles_avd_obstacles_ob_0
Loiter,avd_obstacles_avd_obstacles_ob_4,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_3,avdcol_henry,avd_obstacles_avd_obstacles_ob_0
Waypt_return,avd_obstacles_avd_obstacles_ob_0
Waypt_return,avd_obstacles_avd_obstacles_ob_3

Here's one example:

Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'none', 'obstacle_name': 'none', 'obstacle_proximity': 'none', 'contact_range': 'far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'idle', 'heading': 'north', 'loiter_point_direction': 'none', 'new_loiter_area': 'True', 'obstacle_direction': 'none', 'name': 'gilda', 'active_behaviour': 'none'}

User query: Why not Station-keep instead of None?  

Explanation: To stay in place, Gilda would need to activate its station-keeping through a user request. Instead, is idle without any active behaviour and waiting to get deployed.   

behaviour_permutation: Original: 'None', Modified: 'Station-keep'

Do the same for the following representation:

"""

loiter_instruction = """
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

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

Available Behaviors:
None
Loiter
Station-keep
Return
Loiter,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_0
loiter,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_3
Loiter,avd_obstacles_avd_obstacles_ob_4
loiter,avd_obstacles_avd_obstacles_ob_0,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_2,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_0,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3
Loiter,avd_obstacles_avd_obstacles_ob_3,avd_obstacles_avd_obstacles_ob_0
Loiter,avd_obstacles_avd_obstacles_ob_4,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_3,avdcol_henry,avd_obstacles_avd_obstacles_ob_0
Waypt_return,avd_obstacles_avd_obstacles_ob_0
Waypt_return,avd_obstacles_avd_obstacles_ob_3

Here's one example:

Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'point5', 'obstacle_name': 'none', 'obstacle_proximity': 'none', 'contact_range': 'very far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'northeast', 'loiter_point_direction': 'northeast', 'new_loiter_area': 'False', 'obstacle_direction': 'none', 'name': 'gilda', 'active_behaviour': 'loiter'}

User query: Why not Waypt_return,avd_obstacles_avd_obstacles_ob_0 instead of Loiter?  

Explanation: Gilda is still loitering fast towards point 5 with a northwest heading, and has not been asked to return to its starting point yet. Additionally, there is no detected obstacle in the vessel's environment.

behaviour_permutation: Original: Loiter, Modified: 'Waypt_return,avd_obstacles_avd_obstacles_ob_0'

Do the same for the following representation:

"""

loiter_obs_avd_instruction = """
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

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

Available Behaviors:
None
Loiter
Station-keep
Return
Loiter,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_0
loiter,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_3
Loiter,avd_obstacles_avd_obstacles_ob_4
loiter,avd_obstacles_avd_obstacles_ob_0,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_2,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_0,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3
Loiter,avd_obstacles_avd_obstacles_ob_3,avd_obstacles_avd_obstacles_ob_0
Loiter,avd_obstacles_avd_obstacles_ob_4,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_3,avdcol_henry,avd_obstacles_avd_obstacles_ob_0
Waypt_return,avd_obstacles_avd_obstacles_ob_0
Waypt_return,avd_obstacles_avd_obstacles_ob_3

Here's one example:

Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'point4', 'obstacle_name': 'obstacle_0', 'obstacle_proximity': 'close', 'contact_range': 'far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'northeast', 'loiter_point_direction': 'southeast', 'new_loiter_area': 'False', 'obstacle_direction': 'northeast', 'name': 'gilda', 'active_behaviour': 'loiter,avd_obstacles_avd_obstacles_ob_0'}

User query: Why not Loiter instead of Loiter,avd_obstacles_avd_obstacles_ob_0?  

Explanation: To just loiter without any obstacle avoidance, Gilda would need to have more distance from obstacle 0 or no spotted obstacles at all.

behaviour_permutation: Original: 'Loiter,avd_obstacles_avd_obstacles_ob_0', Modified: 'Loiter'

Do the same for the following representation: 

"""

loiter_avd_col_instruction = """
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

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

Available Behaviors:
None
Loiter
Station-keep
Return
Loiter,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_0
loiter,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_3
Loiter,avd_obstacles_avd_obstacles_ob_4
loiter,avd_obstacles_avd_obstacles_ob_0,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_2,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_0,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3
Loiter,avd_obstacles_avd_obstacles_ob_3,avd_obstacles_avd_obstacles_ob_0
Loiter,avd_obstacles_avd_obstacles_ob_4,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_3,avdcol_henry,avd_obstacles_avd_obstacles_ob_0
Waypt_return,avd_obstacles_avd_obstacles_ob_0
Waypt_return,avd_obstacles_avd_obstacles_ob_3

Here's one example:

Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'point7', 'obstacle_name': 'obstacle_0', 'obstacle_proximity': 'nearby', 'contact_range': 'close', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'northwest', 'loiter_point_direction': 'southwest', 'new_loiter_area': 'False', 'obstacle_direction': 'northwest', 'name': 'gilda', 'active_behaviour': 'loiter,avd_obstacles_avd_obstacles_ob_0,avdcol_henry'}

User query: Why not Waypt_return,avd_obstacles_avd_obstacles_ob_0 instead of loiter,avd_obstacles_avd_obstacles_ob_0,avdcol_henry?  

Explanation: Gilda would need to retrieve a command to return to its starting point and interrupt its loitering. Moreover, it would need to have more distance from its contact.

behaviour_permutation: 
Original: 'loiter,avd_obstacles_avd_obstacles_ob_0,avdcol_henry', 
Modified: 'Waypt_return,avd_obstacles_avd_obstacles_ob_0'

Do the same for the following representation: 

"""

station_keep_instruction = """
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

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

Available Behaviors:
None
Loiter
Station-keep
Return
Loiter,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_0
loiter,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_3
Loiter,avd_obstacles_avd_obstacles_ob_4
loiter,avd_obstacles_avd_obstacles_ob_0,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_2,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_0,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3
Loiter,avd_obstacles_avd_obstacles_ob_3,avd_obstacles_avd_obstacles_ob_0
Loiter,avd_obstacles_avd_obstacles_ob_4,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_3,avdcol_henry,avd_obstacles_avd_obstacles_ob_0
Waypt_return,avd_obstacles_avd_obstacles_ob_0
Waypt_return,avd_obstacles_avd_obstacles_ob_3

Here's one example:

Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'True', 'next_loiter_point': 'none', 'obstacle_name': 'obstacle_2', 'obstacle_proximity': 'very far', 'contact_range': 'very far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'low', 'heading': 'southeast', 'loiter_point_direction': 'none', 'new_loiter_area': 'False', 'obstacle_direction': 'southwest', 'name': 'gilda', 'active_behaviour': 'station-keep'}

User query: Why not Return instead of station-keep?  

Explanation: Gilda would have to retrieve a request to move back to its starting point. Because there are no obstacles or other vessels nearby, it would also take a direct route without modifying its trajectory. However, Gilda currently stays in place waiting for further instructions.

behaviour_permutation: 
Original: 'Station-keep', 
Modified: 'Return'

Do the same for the following representation: 

"""

return_instruction = """
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

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

Available Behaviors:
None
Loiter
Station-keep
Return
Loiter,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_0
loiter,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_3
Loiter,avd_obstacles_avd_obstacles_ob_4
loiter,avd_obstacles_avd_obstacles_ob_0,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_2,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_0,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3
Loiter,avd_obstacles_avd_obstacles_ob_3,avd_obstacles_avd_obstacles_ob_0
Loiter,avd_obstacles_avd_obstacles_ob_4,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_3,avdcol_henry,avd_obstacles_avd_obstacles_ob_0
Waypt_return,avd_obstacles_avd_obstacles_ob_0
Waypt_return,avd_obstacles_avd_obstacles_ob_3

Here's one example:

Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'True', 'station_keep': 'False', 'next_loiter_point': 'none', 'obstacle_name': 'obstacle_2', 'obstacle_proximity': 'very far', 'contact_range': 'far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'idle', 'heading': 'southeast', 'loiter_point_direction': 'none', 'new_loiter_area': 'False', 'obstacle_direction': 'southwest', 'name': 'gilda', 'active_behaviour': 'waypt_return'}

User query: Why not Waypt_return,avd_obstacles_avd_obstacles_ob_2 instead of waypt_return?  

Explanation: Gilda would need to modify its trajectory if it was closer to obstacle 2. At the moment, the vessel is moving directly towards its starting point without any risk of collision.

behaviour_permutation: 
Original: 'waypt_return', 
Modified: 'Waypt_return,avd_obstacles_avd_obstacles_ob_2'

Do the same for the following representation: 

"""

return_obs_avoid_instruction = """
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

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

Available Behaviors:
None
Loiter
Station-keep
Return
Loiter,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_0
loiter,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_3
Loiter,avd_obstacles_avd_obstacles_ob_4
loiter,avd_obstacles_avd_obstacles_ob_0,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_2,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_0,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3
Loiter,avd_obstacles_avd_obstacles_ob_3,avd_obstacles_avd_obstacles_ob_0
Loiter,avd_obstacles_avd_obstacles_ob_4,avd_obstacles_avd_obstacles_ob_2
loiter,avd_obstacles_avd_obstacles_ob_2,avd_obstacles_avd_obstacles_ob_3,avdcol_henry
loiter,avd_obstacles_avd_obstacles_ob_3,avdcol_henry,avd_obstacles_avd_obstacles_ob_0
Waypt_return,avd_obstacles_avd_obstacles_ob_0
Waypt_return,avd_obstacles_avd_obstacles_ob_3

Here's one example:

Representation: {'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'True', 'station_keep': 'False', 'next_loiter_point': 'none', 'obstacle_name': 'obstacle_0', 'obstacle_proximity': 'nearby', 'contact_range': 'far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'southeast', 'loiter_point_direction': 'none', 'new_loiter_area': 'False', 'obstacle_direction': 'northeast', 'name': 'gilda', 'active_behaviour': 'waypt_return,avd_obstacles_avd_obstacles_ob_0'}

User query: Why not Loiter, avd_obstacles_avd_obstacles_ob_0 instead of waypt_return,avd_obstacles_avd_obstacles_ob_0?  

Explanation: Gilda would have to cancel its return due to an operator command, move towards a new waypoint while avoiding obstacle 0 and loiter around until further notice. Instead, the vessel is moving directly towards its starting point for pick up.

behaviour_permutation: 
Original: 'Waypt_return,avd_obstacles_avd_obstacles_ob_0', 
Modified: 'Loiter, avd_obstacles_avd_obstacles_ob_0'

Do the same for the following representation: 

"""


class GPT3Annotator:

    def __init__(self):
        self.data = pd.read_csv("persistance/moos_ivp_csv/m34_alpha/m34_alpha_dataset_contrastive.csv")

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
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", engine=deployment_name, messages=[{"role": "user", "content": prompt}])
            explanation = response.choices[0].message.content
            self.data.at[i, "explanation"] = explanation
            time.sleep(10)
        self.save_dataset("persistance/moos_ivp_csv/m34_alpha/m34_alpha_dataset_contrastive_2.csv")

    def save_dataset(self, path):
        self.data.to_csv(path, index=False)


gpt3_annotator = GPT3Annotator()
gpt3_annotator.generate_annotation()