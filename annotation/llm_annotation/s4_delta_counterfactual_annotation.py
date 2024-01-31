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

no_bhv_instruction = """
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query. 

Decision-making: 
If deploy = false, then the vessel is idle.
If deploy = true, then the vehicle is moving within a predefined depth range. 
If deploy = true and next_loiter_point, then the vehicle is loitering around a predefined set of waypoints.
If deploy = true and return = true, then the vessel is returning to its starting point
If deploy = true, return = false, next_waypoint != ‘none’ and next_waypoint != ‘starting_point’, then the vehicle is surveying an area designated by the user.
If deploy = true, next_loiter_point != ‘none’ and periodic_ascent = true, then the vessel is surfacing to provide new GPS coordinates to command and control.

Here’s one example:

Representation: 	 	 	 	 	 	
{'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then perform the survey and finally return back to starting point', 'deploy': 'False', 'return': 'False', 'next_waypoint': 'none', 'behaviour_stage': 'none', 'next_loiter_point': 'none', 'gps_update_received': 'False', 'depth': 'on surface', 'vehicle_at_surface': 'True', 'periodic_ascend': 'False', 'waypoint_direction': 'none', 'loiter_point_direction': 'none', 'speed': 'idle', 'heading': 'south', 'name': 'henry', 'active_behaviour': 'none'}


User query: What if Henry is deployed and next_loiter_point = point0  

Explanation: If Henry starts moving towards point 0, then the vessel is going to circle the predefined loiter waypoints while maintaining its depth within a predefined range. 

State_permutation: ‘deploy’ = ‘True’, 'next_loiter_point': point0'

Do the same for the following representation:

"""

loiter_instruction = """
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query. 

Decision-making: 
If deploy = false, then the vessel is idle.
If deploy = true, then the vehicle is moving within a predefined depth range. 
If deploy = true and next_loiter_point, then the vehicle is loitering around a predefined set of waypoints.
If deploy = true and return = true, then the vessel is returning to its starting point
If deploy = true, return = false, next_waypoint != ‘none’ and next_waypoint != ‘starting_point’, then the vehicle is surveying an area designated by the user.
If deploy = true, next_loiter_point != ‘none’ and periodic_ascent = true, then the vessel is surfacing to provide new GPS coordinates to command and control.

Here’s one example:

Representation: 	 	 	 	 	 	
{'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then perform the survey and finally return back to starting point', 'deploy': 'True', 'return': 'False', 'next_waypoint': 'none', 'behaviour_stage': 'none', 'next_loiter_point': 'point3', 'gps_update_received': 'False', 'depth': 'very deep', 'vehicle_at_surface': 'False', 'periodic_ascend': 'False', 'waypoint_direction': 'none', 'loiter_point_direction': 'southwest', 'speed': 'fast', 'heading': 'southwest', 'name': 'henry', 'active_behaviour': 'maxdepth,loiter,bhv_const_depth'}


User query: What if Henry stops being deployed?  

Explanation: If Henry stops being deployed, then the vessel would reduce its speed and eventually stay idle.

State_permutation: 'deploy': False'

Do the same for the following representation:

"""

loiter_surface_instruction = """
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query. 

Decision-making: 
If deploy = false, then the vessel is idle.
If deploy = true, then the vehicle is moving within a predefined depth range. 
If deploy = true and next_loiter_point, then the vehicle is loitering around a predefined set of waypoints.
If deploy = true and return = true, then the vessel is returning to its starting point
If deploy = true, return = false, next_waypoint != ‘none’ and next_waypoint != ‘starting_point’, then the vehicle is surveying an area designated by the user.
If deploy = true, next_loiter_point != ‘none’ and periodic_ascent = true, then the vessel is surfacing to provide new GPS coordinates to command and control.

Here’s one example:

Representation: 	 	 	 	 	 	
{'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then perform the survey and finally return back to starting point', 'deploy': 'True', 'return': 'False', 'next_waypoint': 'none', 'behaviour_stage': 'none', 'next_loiter_point': 'point6', 'gps_update_received': 'False', 'depth': 'very deep', 'vehicle_at_surface': 'False', 'periodic_ascend': 'True', 'waypoint_direction': 'none', 'loiter_point_direction': 'northwest', 'speed': 'moderate', 'heading': 'northeast', 'name': 'henry', 'active_behaviour': 'maxdepth,loiter,bhv_periodic_surface,bhv_const_depth'}

	 	

User query: What if periodic ascend is deactivated?

Explanation: The vehicle would stop surfacing and continue to maintain its depth to desirable levels while loitering.

State_permutation: 'periodic_ascend': ‘False'

Do the same for the following representation:

"""

survey_instruction = """
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query. 

Decision-making: 
If deploy = false, then the vessel is idle.
If deploy = true, then the vehicle is moving within a predefined depth range. 
If deploy = true and next_loiter_point, then the vehicle is loitering around a predefined set of waypoints.
If deploy = true and return = true, then the vessel is returning to its starting point
If deploy = true, return = false, next_waypoint != ‘none’ and next_waypoint != ‘starting_point’, then the vehicle is surveying an area designated by the user.
If deploy = true, next_loiter_point != ‘none’ and periodic_ascent = true, then the vessel is surfacing to provide new GPS coordinates to command and control.

Here’s one example:

Representation: {'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then perform the survey and finally return back to starting point', 'deploy': 'True', 'return': 'False', 'next_waypoint': 'point2', 'behaviour_stage': 'advanced', 'next_loiter_point': 'none', 'gps_update_received': 'False', 'depth': 'very deep', 'vehicle_at_surface': 'False', 'periodic_ascend': 'True', 'waypoint_direction': 'northwest', 'loiter_point_direction': 'none', 'speed': 'max speed', 'heading': 'southeast', 'name': 'henry', 'active_behaviour': 'maxdepth,bhv_const_depth,waypt_survey'} 	 	

User query: What if next waypoint is equal to none and next loiter point is point 0? 

Explanation: Henry would have to move towards point0 to loiter while waiting for the next designated survey area. However, because periodic ascend is also active while loitering, the vessel will have to go to the surface for a GPS coordinate correction.

State_permutation: 'next_waypoint': none, 'next_loiter_point': point0'

Do the same for the following representation:

"""

return_instruction = """
Instruction: For the following decision-making description of an autonomous vehicle and a provided vehicle state representation, generate a what-if query that would change the current behaviour of the agent, a corresponding explanation and a state permutation that indicates the representation permutation described in the user query. 

Decision-making: 
If deploy = false, then the vessel is idle.
If deploy = true, then the vehicle is moving within a predefined depth range. 
If deploy = true and next_loiter_point, then the vehicle is loitering around a predefined set of waypoints.
If deploy = true and return = true, then the vessel is returning to its starting point
If deploy = true, return = false, next_waypoint != ‘none’ and next_waypoint != ‘starting_point’, then the vehicle is surveying an area designated by the user.
If deploy = true, next_loiter_point != ‘none’ and periodic_ascent = true, then the vessel is surfacing to provide new GPS coordinates to command and control.

Here’s one example:

Representation: 	 	 	 	 	 	
{'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then perform the survey and finally return back to starting point', 'deploy': 'True', 'return': 'True', 'next_waypoint': 'starting_point', 'behaviour_stage': 'in-transit', 'next_loiter_point': 'none', 'gps_update_received': 'False', 'depth': 'very deep', 'vehicle_at_surface': 'False', 'periodic_ascend': 'True', 'waypoint_direction': 'northwest', 'loiter_point_direction': 'none', 'speed': 'very fast', 'heading': 'southwest', 'name': 'henry', 'active_behaviour': 'maxdepth,waypt_return,bhv_const_depth'}

	 	
User query: What if the vehicle is re-deployed without a designated survey area?

Explanation: If Henry is redeployed but not assigned to a survey area, then it would move towards point 0 to loiter while waiting for further instructions from C2.

State_permutation: 'return': ‘False’, 'next_waypoint': 'none',  'next_loiter_point': ‘point0'

Do the same for the following representation:

"""


class GPT3Annotator:

    def __init__(self):
        self.data = pd.read_csv("persistance/moos_ivp_csv/s4_delta/s4_delta_dataset_counterfactual.csv")

    @staticmethod
    def formulate_prompt(instruction, representation):
        prompt = "{} Representation: {} ".format(instruction, representation)
        return prompt

    def generate_annotation(self):
        for i in tqdm(range(len(self.data)), desc="Annotating", unit="iteration"): 
            if "none" in self.data.iloc[i, 15]:
                prompt = self.formulate_prompt(no_bhv_instruction, self.data.iloc[i, 16])
            elif "maxdepth,loiter,bhv_const_depth" in self.data.iloc[i, 15]:
                prompt = self.formulate_prompt(loiter_instruction, self.data.iloc[i, 16])
            elif "maxdepth,loiter,bhv_periodic_surface,bhv_const_depth" in self.data.iloc[i, 15]:
                prompt = self.formulate_prompt(loiter_surface_instruction, self.data.iloc[i, 16])
            elif "maxdepth,bhv_const_depth,waypt_survey" in self.data.iloc[i, 15]:
                prompt = self.formulate_prompt(survey_instruction, self.data.iloc[i, 16])
            elif "maxdepth,waypt_return,bhv_const_depth" in self.data.iloc[i, 15]:
                prompt = self.formulate_prompt(return_instruction, self.data.iloc[i, 16])
            # print(prompt)
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", engine=deployment_name, messages=[{"role": "user", "content": prompt}])
            # print(response.choices[0].message.content)
            # print("Done")
            explanation = response.choices[0].message.content
            self.data.at[i, "explanation"] = explanation
            time.sleep(10)
        self.save_dataset("persistance/moos_ivp_csv/s4_delta/s4_delta_dataset_counterfactual_2.csv")

    def save_dataset(self, path):
        self.data.to_csv(path, index=False)

gpt3_annotator = GPT3Annotator()
gpt3_annotator.generate_annotation()