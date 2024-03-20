import os
import wandb
import pandas as pd
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

print("Logging in...")
login("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")
wandb.login(key="e02f877bc61d440081963d6d9507c438fc3f32f1")
os.environ["WANDB_PROJECT"] = "xarlm"  # name your W&B project

print("Loading model and tokenizer...")
# model_id = "meta-llama/Llama-2-7b-hf"
model_id = "meta-llama/Llama-2-7b-chat-hf"
# peft_model_id = "konsgavriil/xarlm_adapter_all_types"
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", trust_remote_code=True, use_auth_token=True)
# model.load_adapter(peft_model_id)
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
print("Adapter and tokenizer have been loaded!")

print("Loading test sample set...")
df = pd.read_csv("persistance/moos_ivp_csv/complete_datasets/causal/causal_test_sample.csv")
print("Test sample set has been loaded!")

output_dict = {"query": [], "representation": [], "response": []}
inf_pipeline = pipeline(model= model, torch_dtype=torch.float16, tokenizer=tokenizer, device_map="auto", trust_remote_code=True)

print("Starting with loop...")
i = 0
for index, row in df.iterrows(): 
    print("Loop:", i)
    text = f"### Instruction: Here's a representation that describes the current state of an autonomous maritime vehicle:\n{row['representation']}\nGiven the provided representation, please respond to the following user query in no more than three sentences:\n{row['user_query']} \n### Response:"
    response = inf_pipeline(text, do_sample=True, num_return_sequences=1, return_full_text=False,
                            eos_token_id=tokenizer.eos_token_id, max_new_tokens=90, top_k=10, temperature=0.6)
    output_dict["query"].append(row['user_query'])
    output_dict["representation"].append(row['representation'])
    output_dict["response"].append(response)
    i += 1

print("Saving inferenced dataframe...")
inferenced_df = pd.DataFrame.from_dict(output_dict)
print("Saving wandb log...")
wandb.init(project="xarlm", name="xarlm_chat_causal_inference")
wandb.log({"dataset": wandb.Table(dataframe=inferenced_df)})
wandb.finish()