import json
import pandas as pd

# Specify the filename
jsonl_filename = "train.jsonl"
data = []
df = pd.read_csv("persistance/moos_ivp_csv/complete_datasets/causal/causal_train_dataset.csv")

for index, row in df.iterrows():
        #Counterfactual
        if row["user_query"].startswith("What"):
                data.append(f"### Instruction: Generate a single counterfactual explanation and state permutation using the following user query and vehicle state representation: User Query: {row['user_query']} Representation: {row['representation']} ### Response: Explanation: {row['explanation']} State Permutation: {row['permutation']}") 

        #Causal
        elif row["user_query"].startswith("Why has"):
                data.append(f"### Instruction: Here's a representation that describes the current state of an autonomous maritime vehicle:\n{row['representation']}\nGiven the provided representation, please respond to the following user query in no more than three sentences:\n{row['user_query']} \n### Response: {row['explanation']}")

        #Contrastive
        elif row["user_query"].startswith("Blah"):
                data.append(f"### Instruction: Generate a single contrastive explanation and behaviour permutation using the following user query and vehicle state representation: User Query: {row['user_query']} Representation: {row['representation']} ### Response: Explanation: {row['explanation']} Behaviour Permutation: {row['permutation']}") 

# # Write data to the JSONL file
with open(jsonl_filename, 'w') as file:
    for item in data:
        json_line = json.dumps({"text": item})
        file.write(json_line + '\n')

print(f"JSONL file '{jsonl_filename}' has been created.")