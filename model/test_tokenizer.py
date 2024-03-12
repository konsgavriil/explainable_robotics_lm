from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

def print_tokens_with_ids(txt):
    tokens = tokenizer.tokenize(txt, add_special_tokens=False)
    token_ids = tokenizer.encode(txt, add_special_tokens=False)
    print(list(zip(tokens, token_ids)))
prompt = "### Instruction: Here's a representation that describes the current state of an autonomous maritime vehicle:\n{'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'point7', 'obstacle_name': 'obstacle_0', 'obstacle_proximity': 'very far', 'contact_range': 'very far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'northwest', 'loiter_point_direction': 'northwest', 'new_loiter_area': 'False', 'obstacle_direction': 'northeast', 'name': 'gilda', 'active_behaviour': 'loiter'}\nGiven the provided representation, please respond to the following user query in no more than three sentences:\nWhy has Gilda activated this specific behaviour? \n### Response: Gilda is currently in a fast loiter towards point 7 with a northwest heading. Since there are no obstacles or other vessels nearby, there is no need for collision avoidance or contact resolution."
print_tokens_with_ids(prompt) 

response_template = "\n### Response:"
print_tokens_with_ids(response_template) 