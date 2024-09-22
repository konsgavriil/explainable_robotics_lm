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
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

Decision-making: 
If deploy = false, then the vessel is idle.
If deploy = true, then the vehicle is moving within a predefined depth range. 
If deploy = true and next_loiter_point, then the vehicle is loitering around a predefined set of waypoints.
If deploy = true and return = true, then the vessel is returning to its starting point
If deploy = true, return = false, next_waypoint != ‘none’ and next_waypoint != ‘starting_point’, then the vehicle is surveying an area designated by the user.
If deploy = true, next_loiter_point != ‘none’ and periodic_ascent = true, then the vessel is surfacing to provide new GPS coordinates to command and control.

Available Behaviors:
None
Maxdepth,bhv_const_depth,waypt_survey
Maxdepth,loiter,bhv_const_depth
Maxdepth,loiter,bhv_periodic_surface,bhv_const_depth
maxdepth,waypt_return,bhv_const_depth

Here’s one example:

Representation: 	 	 	 	 	 	
{'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then perform the survey and finally return back to starting point', 'deploy': 'False', 'return': 'False', 'next_waypoint': 'none', 'behaviour_stage': 'none', 'next_loiter_point': 'none', 'gps_update_received': 'False', 'depth': 'on surface', 'vehicle_at_surface': 'True', 'periodic_ascend': 'False', 'waypoint_direction': 'none', 'loiter_point_direction': 'none', 'speed': 'idle', 'heading': 'south', 'name': 'henry', 'active_behaviour': 'none'}

User query: Why not Maxdepth,loiter,bhv_const_depth instead of None?  

Explanation: Henry needs to be deployed and not perform any survey to loiter around its predefined area while maintaining its depth. 

behaviour_permutation: Original: ‘None’, Modified: Maxdepth,loiter,bhv_const_depth

Do the same for the following representation: 

"""

loiter_instruction = """
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

Decision-making: 
If deploy = false, then the vessel is idle.
If deploy = true, then the vehicle is moving within a predefined depth range. 
If deploy = true and next_loiter_point, then the vehicle is loitering around a predefined set of waypoints.
If deploy = true and return = true, then the vessel is returning to its starting point
If deploy = true, return = false, next_waypoint != ‘none’ and next_waypoint != ‘starting_point’, then the vehicle is surveying an area designated by the user.
If deploy = true, next_loiter_point != ‘none’ and periodic_ascent = true, then the vessel is surfacing to provide new GPS coordinates to command and control.

Available Behaviors:
None
Maxdepth,bhv_const_depth,waypt_survey
Maxdepth,loiter,bhv_const_depth
Maxdepth,loiter,bhv_periodic_surface,bhv_const_depth
maxdepth,waypt_return,bhv_const_depth

Here's one example:

Representation: 	 	 	 	 	 	
{'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then perform the survey and finally return back to starting point', 'deploy': 'True', 'return': 'False', 'next_waypoint': 'none', 'behaviour_stage': 'none', 'next_loiter_point': 'point3', 'gps_update_received': 'False', 'depth': 'very deep', 'vehicle_at_surface': 'False', 'periodic_ascend': 'False', 'waypoint_direction': 'none', 'loiter_point_direction': 'southwest', 'speed': 'fast', 'heading': 'southwest', 'name': 'henry', 'active_behaviour': 'maxdepth,loiter,bhv_const_depth'}


User query: Why not None instead of Maxdepth,loiter,bhv_const_depth?

Explanation: Henry needs to stop its deployment to stay idle without any activated behaviour. Instead, the vessel is loitering towards point 3 while waiting to perform a survey.

behaviour_permutation: Original: 'Maxdepth,loiter,bhv_const_depth', Modified: 'None'

Do the same for the following representation: 

"""

loiter_surface_instruction = """
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

Decision-making: 
If deploy = false, then the vessel is idle.
If deploy = true, then the vehicle is moving within a predefined depth range. 
If deploy = true and next_loiter_point, then the vehicle is loitering around a predefined set of waypoints.
If deploy = true and return = true, then the vessel is returning to its starting point
If deploy = true, return = false, next_waypoint != 'none' and next_waypoint != 'starting_point', then the vehicle is surveying an area designated by the user.
If deploy = true, next_loiter_point != 'none' and periodic_ascent = true, then the vessel is surfacing to provide new GPS coordinates to command and control.

Available Behaviors:
None
Maxdepth,bhv_const_depth,waypt_survey
Maxdepth,loiter,bhv_const_depth
Maxdepth,loiter,bhv_periodic_surface,bhv_const_depth
maxdepth,waypt_return,bhv_const_depth

Here's one example:

Representation: 	 	 	 	 	 	
{'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then perform the survey and finally return back to starting point', 'deploy': 'True', 'return': 'False', 'next_waypoint': 'none', 'behaviour_stage': 'none', 'next_loiter_point': 'point6', 'gps_update_received': 'False', 'depth': 'very deep', 'vehicle_at_surface': 'False', 'periodic_ascend': 'True', 'waypoint_direction': 'none', 'loiter_point_direction': 'northwest', 'speed': 'moderate', 'heading': 'northeast', 'name': 'henry', 'active_behaviour': 'maxdepth,loiter,bhv_periodic_surface,bhv_const_depth'}

User query: Why not Maxdepth,loiter,bhv_const_depth instead of Maxdepth,loiter,bhv_periodic_surface,bhv_const_depth?

Explanation: The vehicle currently has an activated periodic ascent, that indicates a required GPS coordinate fix. If it was deactivated, then the vehicle would normally loiter while maintaining its depth and waiting for a survey request.

behaviour_permutation: Original: 'Maxdepth,loiter,bhv_periodic_surface,bhv_const_depth', Modified: 'Maxdepth,loiter,bhv_const_depth'

Do the same for the following representation:

"""

survey_instruction = """
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

Decision-making: 
If deploy = false, then the vessel is idle.
If deploy = true, then the vehicle is moving within a predefined depth range. 
If deploy = true and next_loiter_point, then the vehicle is loitering around a predefined set of waypoints.
If deploy = true and return = true, then the vessel is returning to its starting point
If deploy = true, return = false, next_waypoint != 'none' and next_waypoint != 'starting_point', then the vehicle is surveying an area designated by the user.
If deploy = true, next_loiter_point != 'none' and periodic_ascent = true, then the vessel is surfacing to provide new GPS coordinates to command and control.

Available Behaviors:
None
Maxdepth,bhv_const_depth,waypt_survey
Maxdepth,loiter,bhv_const_depth
Maxdepth,loiter,bhv_periodic_surface,bhv_const_depth
maxdepth,waypt_return,bhv_const_depth

Here's one example:

Representation: {'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then perform the survey and finally return back to starting point', 'deploy': 'True', 'return': 'False', 'next_waypoint': 'point2', 'behaviour_stage': 'advanced', 'next_loiter_point': 'none', 'gps_update_received': 'False', 'depth': 'very deep', 'vehicle_at_surface': 'False', 'periodic_ascend': 'True', 'waypoint_direction': 'northwest', 'loiter_point_direction': 'none', 'speed': 'max speed', 'heading': 'southeast', 'name': 'henry', 'active_behaviour': 'maxdepth,bhv_const_depth,waypt_survey'} 	 	

User query: Why not Maxdepth,loiter,bhv_const_depth instead of Maxdepth,bhv_const_depth,waypt_survey?

Explanation: Henry should have an assigned loiter point to loiter around. Currently, the user has selected a survey area and the vessel is moving towards survey point 2. Moreover, periodic ascend should be deactivated during loitering, otherwise, the vehicle will need to surface to make a coordinate correction.   

behaviour_permutation: Original: 'Maxdepth,bhv_const_depth,waypt_survey', Modified: 'Maxdepth,loiter,bhv_const_depth'
Do the same for the following representation: 

"""

return_instruction = """
Instruction: Generate a why-not query based on the provided decision-making description of an autonomous vehicle and a given vehicle state representation. The query should inquire about an alternative behaviour the agent could exhibit, considering the active behaviour specified in the provided representation. Provide a corresponding explanation and a behaviour permutation reflecting the potential behaviour change described in the user query.

Decision-making: 
If deploy = false, then the vessel is idle.
If deploy = true, then the vehicle is moving within a predefined depth range. 
If deploy = true and next_loiter_point, then the vehicle is loitering around a predefined set of waypoints.
If deploy = true and return = true, then the vessel is returning to its starting point
If deploy = true, return = false, next_waypoint != 'none' and next_waypoint != 'starting_point', then the vehicle is surveying an area designated by the user.
If deploy = true, next_loiter_point != 'none' and periodic_ascent = true, then the vessel is surfacing to provide new GPS coordinates to command and control.

Available Behaviors:
None
Maxdepth,bhv_const_depth,waypt_survey
Maxdepth,loiter,bhv_const_depth
Maxdepth,loiter,bhv_periodic_surface,bhv_const_depth
maxdepth,waypt_return,bhv_const_depth

Here's one example:

Representation: 	 	 	 	 	 	
{'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then perform the survey and finally return back to starting point', 'deploy': 'True', 'return': 'True', 'next_waypoint': 'starting_point', 'behaviour_stage': 'in-transit', 'next_loiter_point': 'none', 'gps_update_received': 'False', 'depth': 'very deep', 'vehicle_at_surface': 'False', 'periodic_ascend': 'True', 'waypoint_direction': 'northwest', 'loiter_point_direction': 'none', 'speed': 'very fast', 'heading': 'southwest', 'name': 'henry', 'active_behaviour': 'maxdepth,waypt_return,bhv_const_depth'}
	
User query: Why not Maxdepth,loiter,bhv_periodic_surface,bhv_const_depth instead of Maxdepth,waypt_return,bhv_const_depth?

Explanation: Henry is currently moving towards its starting point as part of its return step. To go to the surface during loitering, it would need to deactivate its return sequence and plan its next loiter point.   

behaviour_permutation: Original: 'Maxdepth,waypt_return,bhv_const_depth', Modified: ‘Maxdepth,loiter,bhv_periodic_surface,bhv_const_depth’

Do the same for the following representation: 

"""


class GPT3Annotator:

    def __init__(self):
        self.data = pd.read_csv("persistance/moos_ivp_csv/s4_delta/s4_delta_dataset_contrastive.csv")

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
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", engine=deployment_name, messages=[{"role": "user", "content": prompt}])
            explanation = response.choices[0].message.content
            self.data.at[i, "explanation"] = explanation
            time.sleep(10)
        self.save_dataset("persistance/moos_ivp_csv/s4_delta/s4_delta_dataset_contrastive_2.csv")

    def save_dataset(self, path):
        self.data.to_csv(path, index=False)

gpt3_annotator = GPT3Annotator()
gpt3_annotator.generate_annotation()