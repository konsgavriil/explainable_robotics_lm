import json
import pandas as pd

# Specify the filename
jsonl_filename = "cf_test.jsonl"
data = []
df = pd.read_csv("persistance/moos_ivp_csv/complete_datasets/counterfactual/counterfactual_test_dataset.csv")

for index, row in df.iterrows():
        #Counterfactual
        data.append(f"### Instruction: Below is a what-if query that asks for an explanation and a state permutation based on the provided vehicle state representation. User query: {row['user_query']}, Representation: {row['representation']}, ### Response: Explanation: {row['explanation']}, State Permutation: {row['state_permutation']}")
        #Causal
        # data.append(f"### Instruction: Below is a query that asks for a causal explanation based on the provided vehicle state representation. User query: {row['user_query']}, Representation: {row['representation']}, ### Response: {row['explanation']}")

# # Write data to the JSONL file
with open(jsonl_filename, 'w') as file:
    for item in data:
        json_line = json.dumps({"text": item})
        file.write(json_line + '\n')

print(f"JSONL file '{jsonl_filename}' has been created.")