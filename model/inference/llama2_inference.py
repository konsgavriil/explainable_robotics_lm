import os
import wandb
import torch
import pandas as pd
from huggingface_hub import login
from peft import PeftModel, PeftConfig
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

# Loading base model
model_id = "meta-llama/Llama-2-7b-hf"
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", trust_remote_code=True, token=True)
model.config.use_cache = False
model.config.pretraining_tp = 1 

# Loading tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
tokenizer.add_special_tokens({'pad_token': '<pad>'})
model.resize_token_embeddings(len(tokenizer))
model.config.pad_token_id = tokenizer.pad_token_id
tokenizer.padding_side = "right"

# Specify the model and the PEFT model paths
peft_model_id = PEFT_MODEL_ID

# Load adapter to base model
model.load_adapter(peft_model_id)


inf_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    # model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
    trust_remote_code=True
)

print("Model and tokenizer have been loaded!")

df = pd.read_csv("/workspace/xarlm/causal_validation.csv")
# df = pd.read_csv("/workspace/xarlm/counterfactual_validation.csv")
# df = pd.read_csv("/workspace/xarlm/contrastive_validation.csv")
# few_shot_df = df.head(2)
# df2 = df.tail(12)
print("Test set has been loaded!")
output_dict = {"query": [], "representation": [], "response": [], "label": []}
# output_dict = {"query": [], "representation": [], "response": [], "label_exp": [], "label_perm": []}
print("Starting with loop...")
i = 0
for index, row in df.iterrows(): 
    print("Loop:", i)
    text = f"### Instruction: Here's a representation that describes the current state of an autonomous maritime vehicle:\n{df['representation'][i]}\nGiven the provided representation, please respond to the following user query in no more than three sentences:\n{df['user_query'][i]} \n### Response: {df['explanation'][i]}"
    # text = f"### Instruction: Here's a representation that describes the current state of an autonomous maritime vehicle:\n{df['representation'][i]}\nRespond to the following what-if query in a maximum of three sentences. Additionally, include a state difference that illustrates the alterations in the user query.\n{df['user_query'][i]} \n### Response: {df['explanation'][i]}\n{df['permutation'][i]}"
    # text = f"### Instruction: Below is a representation depicting the current state of an autonomous maritime vehicle:\n{df['representation'][i]}\nRespond to the following why-not query in a maximum of three sentences. Additionally, include a behaviour difference that illustrates the alterations in the user query.{df['user_query'][i]} \n### Response: {df['explanation'][i]}\n{df['permutation'][i]}"
        
    # text = f"Instruction: Using a vehicle state representation and a user query, generate an explanation that describes how the vehicle activated its current behaviour. \n Here are a few examples: \n Input: {few_shot_df.iloc[0][0]}, {few_shot_df.iloc[0][1]}, Output: {few_shot_df.iloc[0][2]} \n Input: {few_shot_df.iloc[1][0]}, {few_shot_df.iloc[1][1]}, Output: {few_shot_df.iloc[1][2]} \n Now do the same for the following input: \n Input: {row['representation']}, {row['user_query']}, Output:"
    # text = f"Instruction: Using a vehicle state representation and a user query, generate an explanation that describes how the vehicle activated its current behaviour. \n Here are a few examples: \n Input: {few_shot_df.iloc[0][0]}, {few_shot_df.iloc[0][1]}, Output: {few_shot_df.iloc[0][2]} \n Input: {few_shot_df.iloc[1][0]}, {few_shot_df.iloc[1][1]}, Output: {few_shot_df.iloc[1][2]} \n Now do the same for the following input: \n Input: {row['representation']}, {row['user_query']}, Output:"
    # text = f"Instruction: Using a vehicle state representation and a user query, generate an explanation that describes how the vehicle would change its current behaviour if its state was modified and a permutation that describes the condition in the user query. \n Here are a few examples: \n Input: {few_shot_df.iloc[0][0]}, {few_shot_df.iloc[0][1]}, Output: {few_shot_df.iloc[0][2]}, {few_shot_df.iloc[0][3]} \n Input: {few_shot_df.iloc[1][0]}, {few_shot_df.iloc[1][1]}, Output: {few_shot_df.iloc[1][2]}, {few_shot_df.iloc[1][3]} \n Now do the same for the following input: \n Input: {row['representation']}, {row['user_query']}, Output:"
    # text = f"Instruction: Using a vehicle state representation and a user query, generate an explanation that describes why the vehicle does not activate an alternative behaviour and a permutation that mentions the alternative behaviour in the user query. \n Here are a few examples: \n Input: {few_shot_df.iloc[0][0]}, {few_shot_df.iloc[0][1]}, Output: {few_shot_df.iloc[0][2]}, {few_shot_df.iloc[0][3]} \n Input: {few_shot_df.iloc[1][0]}, {few_shot_df.iloc[1][1]}, Output: {few_shot_df.iloc[1][2]}, {few_shot_df.iloc[1][3]} \n Now do the same for the following input: \n Input: {row['representation']}, {row['user_query']}, Output:"
    response = inf_pipeline(text, do_sample=True, num_return_sequences=1, return_full_text=False, eos_token_id=tokenizer.pad_token_id, max_new_tokens=150, top_k=10, temperature=0.6)
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
wandb.init(project="xarlm_llama2", name="llama2_causal_inference")
# wandb.init(project="xarlm_llama2", name="llama2_cf_inference")
# wandb.init(project="xarlm_llama2", name="llama2_it_contrastive_inference")
wandb.log({"dataset": wandb.Table(dataframe=inferenced_df)})
wandb.finish()