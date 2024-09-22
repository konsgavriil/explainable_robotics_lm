import os
import wandb
# import torch
import pandas as pd
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

HF_LOGIN = ""
WANDB_KEY = ""
WANDB_PROJECT = ""

print("Logging in...")
login(HF_LOGIN)
wandb.login(key=WANDB_KEY)
os.environ["WANDB_PROJECT"] = WANDB_PROJECT  # name your W&B project
print("Loading model and tokenizer...")

# Loading it model
model_id = "mistralai/Mistral-7B-Instruct-v0.3"
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", trust_remote_code=True, token=True) 

# Loading tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id, add_bos_token=True, add_eos_token=True, trust_remote_code=True)

inf_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device_map="auto",
    trust_remote_code=True
)

print("Model and tokenizer have been loaded!")

df = pd.read_csv("/workspace/xarlm/causal_validation.csv")
# df = pd.read_csv("/workspace/xarlm/counterfactual_validation.csv")
# df = pd.read_csv("/workspace/xarlm/contrastive_validation.csv")
few_shot_df = df.head(2)
df2 = df.tail(100)
print("Test set has been loaded!")
output_dict = {"query": [], "representation": [], "response": [], "label": []}
# output_dict = {"query": [], "representation": [], "response": [], "label_exp": [], "label_perm": []}
print("Starting with loop...")
i = 0
for index, row in df2.iterrows(): 
    print("Loop:", i)  
    text = f"Instruction: Using a vehicle state representation and a user query, generate an explanation that describes how the vehicle activated its current behaviour. \n Here are a few examples: \n Input: {few_shot_df.iloc[0][0]}, {few_shot_df.iloc[0][1]}, Output: {few_shot_df.iloc[0][2]} \n Input: {few_shot_df.iloc[1][0]}, {few_shot_df.iloc[1][1]}, Output: {few_shot_df.iloc[1][2]} \n Now do the same for the following input: \n Input: {row['representation']}, {row['user_query']}, Output:"
    # text = f"Instruction: Using a vehicle state representation and a user query, generate an explanation that describes how the vehicle would change its current behaviour if its state was modified and a permutation that describes the condition in the user query. \n Here are a few examples: \n Input: {few_shot_df.iloc[0][0]}, {few_shot_df.iloc[0][1]}, Output: {few_shot_df.iloc[0][2]}, {few_shot_df.iloc[0][3]} \n Input: {few_shot_df.iloc[1][0]}, {few_shot_df.iloc[1][1]}, Output: {few_shot_df.iloc[1][2]}, {few_shot_df.iloc[1][3]} \n Now do the same for the following input: \n Input: {row['representation']}, {row['user_query']}, Output:"
    # text = f"Instruction: Using a vehicle state representation and a user query, generate an explanation that describes why the vehicle does not activate an alternative behaviour and a permutation that mentions the alternative behaviour in the user query. \n Here are a few examples: \n Input: {few_shot_df.iloc[0][0]}, {few_shot_df.iloc[0][1]}, Output: {few_shot_df.iloc[0][2]}, {few_shot_df.iloc[0][3]} \n Input: {few_shot_df.iloc[1][0]}, {few_shot_df.iloc[1][1]}, Output: {few_shot_df.iloc[1][2]}, {few_shot_df.iloc[1][3]} \n Now do the same for the following input: \n Input: {row['representation']}, {row['user_query']}, Output:"
    response = inf_pipeline(text, max_new_tokens=1000, return_full_text=False)
    output_dict["query"].append(row['user_query'])
    output_dict["representation"].append(row['representation'])
    output_dict["response"].append(response[-1]['generated_text'])
    output_dict["label"].append(row['explanation'])
    # output_dict["label_exp"].append(row['explanation'])
    # output_dict["label_perm"].append(row['permutation'])
    i += 1

print("Saving inferenced dataframe...")
inferenced_df = pd.DataFrame.from_dict(output_dict)
print("Saving wandb log...")
wandb.init(project=WANDB_PROJECT, name="mistral_it_causal_inference")
# wandb.init(project="xarlm_mistral", name="mistral_it_cf_inference")
# wandb.init(project="xarlm_mistral", name="mistral_it_contrastive_inference")
wandb.log({"dataset": wandb.Table(dataframe=inferenced_df)})
wandb.finish()