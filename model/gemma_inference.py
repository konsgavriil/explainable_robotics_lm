import os
import wandb
import torch
import pandas as pd
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

print("Logging in...")
login("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")
wandb.login(key="e02f877bc61d440081963d6d9507c438fc3f32f1")
os.environ["WANDB_PROJECT"] = "xarlm"  # name your W&B project
print("Loading model and tokenizer...")

tokenizer = AutoTokenizer.from_pretrained("google/gemma-1.1-7b-it")
model = AutoModelForCausalLM.from_pretrained(
    "google/gemma-1.1-7b-it",
    device_map="auto",
    torch_dtype=torch.bfloat16
)

inf_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device_map="auto",
    trust_remote_code=True
)

print("Model and tokenizer have been loaded!")

# df = pd.read_csv("/workspace/xarlm/causal_validation.csv")
df = pd.read_csv("/workspace/xarlm/counterfactual_validation.csv")
few_shot_df = df.head(2)
df2 = df.tail(12)
print("Test set has been loaded!")
# output_dict = {"query": [], "representation": [], "response": [], "label": []}
output_dict = {"query": [], "representation": [], "response": [], "label_exp": [], "label_perm": []}

print("Starting with loop...")
i = 0
for index, row in df2.iterrows(): 
    print("Loop:", i)
    # text = f"Instruction: Using a vehicle state representation and a user query, generate an explanation that describes how the vehicle activated its current behaviour. \n Here are a few examples: \n Input: {few_shot_df.iloc[0][0]}, {few_shot_df.iloc[0][1]}, Output: {few_shot_df.iloc[0][2]} \n Input: {few_shot_df.iloc[1][0]}, {few_shot_df.iloc[1][1]}, Output: {few_shot_df.iloc[1][2]} \n Now do the same for the following input: \n Input: {row['representation']}, {row['user_query']}, Output:"
    text = f"Instruction: Using a vehicle state representation and a user query, generate an explanation that describes how the vehicle activated its current behaviour and a permutation that describes the condition in the user query. \n Here are a few examples: \n Input: {few_shot_df.iloc[0][0]}, {few_shot_df.iloc[0][1]}, Output: {few_shot_df.iloc[0][2]}, {few_shot_df.iloc[0][3]} \n Input: {few_shot_df.iloc[1][0]}, {few_shot_df.iloc[1][1]}, Output: {few_shot_df.iloc[1][2]}, {few_shot_df.iloc[1][3]} \n Now do the same for the following input: \n Input: {row['representation']}, {row['user_query']}, Output:"
    response = inf_pipeline(text, do_sample=True, num_return_sequences=1, return_full_text=False, eos_token_id=tokenizer.eos_token_id, max_new_tokens=150, top_k=10, temperature=0.6)
    output_dict["query"].append(row['user_query'])
    output_dict["representation"].append(row['representation'])
    output_dict["response"].append(response[-1]['generated_text'])
    # output_dict["label"].append(row['explanation'])
    output_dict["label_exp"].append(row['explanation'])
    output_dict["label_perm"].append(row['permutation'])
    i += 1

print("Saving inferenced dataframe...")
inferenced_df = pd.DataFrame.from_dict(output_dict)
print("Saving wandb log...")
# wandb.init(project="xarlm_gemma", name="gemma_causal_inference")
wandb.init(project="xarlm_gemma", name="gemma_cf_inference")
wandb.log({"dataset": wandb.Table(dataframe=inferenced_df)})
wandb.finish()
