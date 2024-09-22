import os
import wandb
import torch
import pandas as pd
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

HF_LOGIN = ""
WANDB_KEY = ""
WANDB_PROJECT = ""
PEFT_MODEL_ID = ""

print("Logging in...")
login(HF_LOGIN)
wandb.login(key=WANDB_KEY)
os.environ["WANDB_PROJECT"] = WANDB_PROJECT  # name your W&B project

print("Loading model and tokenizer...")
model_name = "mistralai/Mistral-7B-Instruct-v0.3"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True)

inf_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    device_map="auto")

print("Model and tokenizer have been loaded!")

prompt = "As a data scientist, can you explain the concept of regularization in machine learning?"

sequences = inf_pipeline(
    prompt,
    do_sample=True,
    max_new_tokens=100, 
    temperature=0.7, 
    top_k=50, 
    top_p=0.95,
    num_return_sequences=1,
)
print(sequences[0]['generated_text'])

# df = pd.read_csv("/workspace/xarlm/causal_validation.csv")
# few_shot_df = df.head(2)
# df2 = df.tail(12)
# print("Test set has been loaded!")
# output_dict = {"query": [], "representation": [], "response": [], "label": []}
# print("Starting with loop...")
# i = 0
# for index, row in df2.iterrows(): 
#     print("Loop:", i)
#     text = f"Instruction: Using a vehicle state representation and a user query, generate an explanation that describes how the vehicle activated its current behaviour. \n Here are a few examples: \n Input: {few_shot_df.iloc[0][0]}, {few_shot_df.iloc[0][1]}, Output: {few_shot_df.iloc[0][2]} \n Input: {few_shot_df.iloc[1][0]}, {few_shot_df.iloc[1][1]}, Output: {few_shot_df.iloc[1][2]} \n Now do the same for the following input: \n Input: {row['representation']}, {row['user_query']}, Output:"
#     response = inf_pipeline(text, max_new_tokens=150, return_full_text=False, do_sample=True, top_k=10, num_return_sequences=1, eos_token_id=tokenizer.eos_token_id)
#     output_dict["query"].append(row['user_query'])
#     output_dict["representation"].append(row['representation'])
#     output_dict["response"].append(response)
#     output_dict["response"].append(response[-1]['generated_text'])
#     output_dict["label"].append(row['explanation'])
#     i += 1

# print("Saving inferenced dataframe...")
# inferenced_df = pd.DataFrame.from_dict(output_dict)
# print("Saving wandb log...")
# wandb.init(project="xarlm_mistral", name="mistral_causal_inference")
# wandb.log({"dataset": wandb.Table(dataframe=inferenced_df)})
# wandb.finish()