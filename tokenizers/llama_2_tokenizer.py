from transformers import LlamaTokenizer

# class VehicleStateTokenizer:
from huggingface_hub import login
login("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")
#     def __init__(self) -> None:
tokenizer = LlamaTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
# tokenizer.from_pretrained()
tokens = tokenizer.tokenize(text="{'objectives': 'Loiter between points 0 to 7 until a survey objective is provided, then perform the survey and finally return back to starting point', 'deploy': 'False', 'return': 'False', 'next_waypoint': 'none', 'behaviour_stage': 'none', 'next_loiter_point': 'none', 'gps_update_received': 'False', 'depth': 'on surface', 'vehicle_at_surface': 'True', 'periodic_ascend': 'False', 'waypoint_direction': 'none', 'loiter_point_direction': 'none', 'speed': 'idle', 'heading': 'south', 'name': 'henry', 'active_behaviour': 'none', 'what_if': 'none', 'predicted_behaviour': 'none', 'why_not': 'none', 'feature_justification': 'none'}")
print(tokens)

    