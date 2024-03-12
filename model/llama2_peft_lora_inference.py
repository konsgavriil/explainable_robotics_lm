import os
import wandb
import pandas as pd
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer

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
df = pd.read_csv("/workspace/xarlm/test_dataset.csv")
random_entries = df.sample(n=10)
new_df = pd.DataFrame(random_entries)
print("Test set has been loaded!")
output_dict = {"query": [], "representation": [], "response": []}

print("Starting with loop...")
i = 0
for index, row in new_df.iterrows(): 
    print("Loop:", i)
    text = f"Representation: {row['representation']}, User query: {row['user_query']}"
    inputs = tokenizer(text, return_tensors="pt")
    inputs.to("cuda")
    output = model.generate(**inputs, max_new_tokens=40)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    output_dict["query"].append(row['user_query'])
    output_dict["representation"].append(row['representation'])
    output_dict["response"].append(response)
    i += 1

print("Saving inferenced dataframe...")
inferenced_df = pd.DataFrame.from_dict(output_dict)
print("Saving wandb log...")
wandb.init(project="xarlm", name="xarlm_all_types_inference")
wandb.log({"dataset": wandb.Table(dataframe=inferenced_df)})
wandb.finish()