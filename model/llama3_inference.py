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
model_id = "meta-llama/Meta-Llama-3-8B-Instruct"

inf_pipeline = pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)

terminators = [
    inf_pipeline.tokenizer.eos_token_id,
    inf_pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

print("Model and tokenizer have been loaded!")

df = pd.read_csv("/workspace/xarlm/causal_validation.csv")
few_shot_df = df.head(2)
df2 = df.tail(12)
print("Test set has been loaded!")
output_dict = {"query": [], "representation": [], "response": []}
print("Starting with loop...")
i = 0
for index, row in df2.iterrows(): 
    print("Loop:", i)
    text = f"Input: {few_shot_df.iloc[0][0]}, {few_shot_df.iloc[0][1]}, Output: {few_shot_df.iloc[0][2]} \n Input: {few_shot_df.iloc[1][0]}, {few_shot_df.iloc[1][1]}, Output: {few_shot_df.iloc[1][2]} \n Input: {row['representation']}, {row['user_query']}, Output:"
    response = inf_pipeline(text, max_new_tokens=150, return_full_text=False, do_sample=True, top_k=10, num_return_sequences=1, temperature=0.6, eos_token_id=terminators)
    output_dict["query"].append(row['user_query'])
    output_dict["representation"].append(row['representation'])
    output_dict["response"].append(response)
    i += 1

print("Saving inferenced dataframe...")
inferenced_df = pd.DataFrame.from_dict(output_dict)
print("Saving wandb log...")
wandb.init(project="xarlm_llama3", name="llama3_causal_inference")
wandb.log({"dataset": wandb.Table(dataframe=inferenced_df)})
wandb.finish()