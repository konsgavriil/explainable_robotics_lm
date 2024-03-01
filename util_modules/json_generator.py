import json
import pandas as pd

# Specify the filename
jsonl_filename = "counterfactual_validation_dataset.jsonl"
data = []
df = pd.read_csv("persistance/moos_ivp_csv/complete_datasets/counterfactual/counterfactual_validation_dataset.csv")

for index, row in df.iterrows():
        #Counterfactual
        if row["user_query"].startswith("What"):
                #data.append(f"### Instruction: User Query: {row['user_query']} Representation: {row['representation']} ### Response: Explanation: {row['explanation']} State Permutation: {row['permutation']}") 
                #data.append(f"### Instruction: Below is a what-if query that asks for an explanation and a state permutation based on the provided vehicle state representation. User query: {row['user_query']}, Representation: {row['representation']}, ### Response: Explanation: {row['explanation']}, State Permutation: {row['permutation']}")
                data.append(f"### Instruction: Generate a single counterfactual explanation and state permutation using the following user query and vehicle state representation: User Query: {row['user_query']} Representation: {row['representation']} ### Response: Explanation: {row['explanation']} State Permutation: {row['permutation']}") 
                # data.append(f"### Instruction: Generate a single counterfactual explanation that answers the following user query using the autonomous vehicle's state representation. Also, generate a single state permutation that indicates the permutations implied by the user query: User Query: {row['user_query']} Representation: {row['representation']} ### Response: Explanation: {row['explanation']} State Permutation: {row['permutation']}") 

        #Causal
        elif row["user_query"].startswith("Generate"):
                # data.append(f"### Instruction: User Query: {row['user_query']} Representation: {row['representation']} ### Response: Explanation: {row['explanation']}")
                # data.append(f"### Instruction: Below is a query that asks for a causal explanation based on the provided vehicle state representation. User query: {row['user_query']}, Representation: {row['representation']}, ### Response: Explanation: {row['explanation']}")
                data.append(f"### Instruction: Generate a single causal explanation using the following user query and vehicle state representation: User Query: {row['user_query']} Representation: {row['representation']} ### Response: Explanation: {row['explanation']}") 
                # data.append(f"### Instruction: Generate a single causal explanation that justifies the vehicle's current behaviour using the following user query and vehicle state representation: User Query: {row['user_query']} Representation: {row['representation']} ### Response: Explanation: {row['explanation']}") 

        #Contrastive
        elif row["user_query"].startswith("Why"):
                # data.append(f"### Instruction: User query: {row['user_query']} Representation: {row['representation']} ### Response: Explanation: {row['explanation']}, Behaviour Permutation: {row['permutation']}")
                # data.append(f"### Instruction: Below is a why-not query that asks for an explanation and a behaviour permutation based on the provided vehicle state representation. User query: {row['user_query']}, Representation: {row['representation']}, ### Response: Explanation: {row['explanation']}, Behaviour Permutation: {row['permutation']}")
                data.append(f"### Instruction: Generate a single contrastive explanation and behaviour permutation using the following user query and vehicle state representation: User Query: {row['user_query']} Representation: {row['representation']} ### Response: Explanation: {row['explanation']} Behaviour Permutation: {row['permutation']}") 
                # data.append(f"### Instruction: Generate a single contrastive explanation that answers the following user query using the autonomous vehicle's state representation. Also, generate a single behaviour permutation that indicates the permutations implied by the user query: User Query: {row['user_query']} Representation: {row['representation']} ### Response: Explanation: {row['explanation']} Behaviour Permutation: {row['permutation']}") 

# # Write data to the JSONL file
with open(jsonl_filename, 'w') as file:
    for item in data:
        json_line = json.dumps({"text": item})
        file.write(json_line + '\n')

print(f"JSONL file '{jsonl_filename}' has been created.")