import os
import torch
import wandb
import evaluate
import numpy as np
import pandas as pd
from peft import LoraConfig
from datasets import load_dataset
from huggingface_hub import login
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, AutoTokenizer, TrainingArguments

login("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")
wandb.login(key="e02f877bc61d440081963d6d9507c438fc3f32f1")
os.environ["WANDB_PROJECT"] = "xarlm"  # name your W&B project

base_model_name = "meta-llama/Llama-2-7b-hf"
adapter_id = "konsgavriil/xarlm_adapter_all_types"
model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    device_map="auto",
    trust_remote_code=True,
    load_in_8bit=True,
    use_auth_token=True
)

tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

model.load_adapter(adapter_id)
model.enable_adapters()

df = pd.read_csv("mixed_test_dataset.csv")
output_dict = {"query": [], "representation": [], "response": []}
for index, row in df.iterrows():
    text = f"User query: {row['user_query']}, Representation: {row['representation']}"
    inputs = tokenizer(text, return_tensors="pt")
    inputs.to("cuda")
    output = model.generate(**inputs)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    output_dict["query"].append(row['user_query'])
    output_dict["representation"].append(row['representation'])
    output_dict["response"].append(response)


# Convert the DataFrame into a W&B Table
all_types_inference_table = wandb.Table(dataframe=df)
iris_table_artifact = wandb.Artifact("all_types_inference_artifact", type="dataset")
iris_table_artifact.add(all_types_inference_table, "all_types_inference_table")
df.to_csv('mixed_test_with_responses.csv', index=False)
# Log the raw csv file within an artifact to preserve our data
iris_table_artifact.add_file("mixed_test_with_responses.csv")