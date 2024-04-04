from transformers import AutoTokenizer, LlamaTokenizer
from huggingface_hub import login
from trl import DataCollatorForCompletionOnlyLM
from transformers import AutoTokenizer
login("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")


prompt1 = "### Instruction: Here's a representation that describes the current state of an autonomous maritime vehicle:\n{'objective': 'Loiter around in different areas which are selected randomly, while avoiding obstacles and collision with other vessels. Finally, once the command is provided by the operator, return to starting point.', 'deploy': 'True', 'return': 'False', 'station_keep': 'False', 'next_loiter_point': 'point7', 'obstacle_name': 'obstacle_0', 'obstacle_proximity': 'very far', 'contact_range': 'very far', 'contact_resolved': 'FALSE', 'collision_avoidance_mode': 'none', 'speed': 'fast', 'heading': 'northwest', 'loiter_point_direction': 'northwest', 'new_loiter_area': 'False', 'obstacle_direction': 'northeast', 'name': 'gilda', 'active_behaviour': 'loiter'}\nGiven the provided representation, please respond to the following user query in no more than three sentences:\nWhy has Gilda activated this specific behaviour? \n### Response: Gilda is currently in a fast loiter towards point 7 with a northwest heading. Since there are no obstacles or other vessels nearby, there is no need for collision avoidance or contact resolution."
prompt2 = "### Instruction: Here's a representation that describes the current state of an autonomous maritime vehicle:\n{'objective': 'Go to points 0, 1, 2 and then return to starting position.', 'deploy': 'False', 'return': 'False', 'obstacle_name': 'none', 'obstacle_proximity': 'none', 'obstacle_resolved': 'False', 'behaviour_stage': 'none', 'next_point': 'none', 'speed': 'none', 'heading': 'none', 'next_point_direction': 'none', 'obstacle_direction': 'none', 'name': 'alpha', 'active_behaviour': 'none'}\nRespond to the following what-if query in a maximum of three sentences. Additionally, include a state difference that illustrates the alterations in the user query.\nWhat if Alpha is deployed and return is true? \n### Response: If Alpha gets deployed and return is true, it would activate its return behaviour that configures the vehicle to return to its starting position after completing its surveying task.\ndeploy = 'True', return = 'True'" 

input_list = [prompt1, prompt2]

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf", pad_token = '<pad>', add_eos_token= True, padding=True, truncation=True, trust_remote_code=True, max_length=512, return_tensors="pt", use_fast=True)
# tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf", trust_remote_code=True, use_fast=True)
# tokenizer = LlamaTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf", trust_remote_code=True, add_eos_token=True, pad_token='<pad>')
# tokenizer.add_special_tokens = True
# tokenizer.pad_token = '<pad>'
# response_template = "\n### Response:"
# response_template_ids = tokenizer.encode(response_template, add_special_tokens=False)
# collator = DataCollatorForCompletionOnlyLM(response_template=response_template_ids, tokenizer=tokenizer)

# tokenized_data = tokenizer(input_list, return_tensors="pt", padding=True, truncation=True)
# batch = collator(tokenized_data)
# print(batch)
# tokens = tokenizer.tokenize(prompt1, add_special_tokens=True, max_length=512, return_tensors="pt")
tokens = tokenizer.tokenize(prompt1, add_special_tokens=True)
# tokens = tokenizer.encode(prompt1, add_special_tokens=True)
# tokens = tokenizer.encode(prompt1)

print(tokens)
