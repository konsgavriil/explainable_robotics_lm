import json
import pandas as pd

# Specify the filename
jsonl_filename = "contrastive_dataset.jsonl"
data = []
df = pd.read_csv("persistance/moos_ivp_csv/complete_datasets/contrastive/contrastive_dataset.csv")

for index, row in df.iterrows():
        #Counterfactual
        if row["user_query"].startswith("What"):
                data.append(f"### Instruction: Here's a representation that describes the current state of an autonomous maritime vehicle:\n{row['representation']}\nRespond to the following what-if query in a maximum of three sentences. Additionally, include a state difference that illustrates the alterations in the user query.\n{row['user_query']} \n### Response: {row['explanation']}\n{row['permutation']}")
        #Causal
        elif row["user_query"].startswith("Why has"):
                data.append(f"### Instruction: Here's a representation that describes the current state of an autonomous maritime vehicle:\n{row['representation']}\nGiven the provided representation, please respond to the following user query in no more than three sentences:\n{row['user_query']} \n### Response: {row['explanation']}")
        #Contrastive
        elif row["user_query"].startswith("Why"):
                data.append(f"### Instruction: Below is a representation depicting the current state of an autonomous maritime vehicle:\n{row['representation']}\nRespond to the following why-not query in a maximum of three sentences. Additionally, include a behaviour difference that illustrates the alterations in the user query.{row['user_query']} \n### Response: {row['explanation']}\n{row['permutation']}")

# # Write data to the JSONL file
with open(jsonl_filename, 'w') as file:
    for item in data:
        json_line = json.dumps({"text": item})
        file.write(json_line + '\n')

print(f"JSONL file '{jsonl_filename}' has been created.")