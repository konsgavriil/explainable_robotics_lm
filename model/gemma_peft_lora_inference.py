import os
import wandb
import torch
import pandas as pd
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

print("Logging in...")
login("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")
wandb.login(key="e02f877bc61d440081963d6d9507c438fc3f32f1")

print("Loading model and tokenizer...")
model_id = "google/gemma-7b"
peft_model_id = "konsgavriil/gemma-7b-causal"
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", token=True)
model.load_adapter(peft_model_id)
tokenizer = AutoTokenizer.from_pretrained(model_id, token=True)
tokenizer.pad_token = '[PAD]'
print("Adapter and tokenizer have been loaded!")
df = pd.read_csv("/workspace/xarlm/causal_validation.csv")
random_entries = df.sample(n=10)
new_df = pd.DataFrame(random_entries)
print("Test set has been loaded!")
output_dict = {"query": [], "representation": [], "response": []}
inf_pipeline = pipeline(task="text-generation", model= model, tokenizer= tokenizer, device_map="auto")
print("Starting with loop...")
i = 0
for index, row in new_df.iterrows(): 
    print("Loop:", i)
    text = f"Representation: {row['representation']}, User query: {row['user_query']}"
    response = inf_pipeline(text, return_full_text=False, eos_token_id=tokenizer.eos_token_id)
    output_dict["query"].append(row['user_query'])
    output_dict["representation"].append(row['representation'])
    output_dict["response"].append(response)
    i += 1

print("Saving inferenced dataframe...")
inferenced_df = pd.DataFrame.from_dict(output_dict)
print("Saving wandb log...")
wandb.init(project="xarlm_gemma", name="xarlm_all_types_inference")
wandb.log({"dataset": wandb.Table(dataframe=inferenced_df)})
wandb.finish()