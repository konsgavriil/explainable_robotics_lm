import json
import pandas as pd

# Specify the filename
jsonl_filename = "example.jsonl"
data = []
df = pd.read_csv("data/initial_llm_training_set.csv")

for index, row in df.iterrows():
        data.append(f"Below is a query that asks for a causal explanation based on the provided vehicle state representation... ### User query: {row['user_query']}, Input: {row['representation']}, Response: {row['explanation']}")

# Data to be written to the JSONL file
# data = [
#     {"name": "John", "age": 30, "city": "New York"},
#     {"name": "Alice", "age": 25, "city": "San Francisco"},
#     {"name": "Bob", "age": 35, "city": "Chicago"}
# ]



# # Write data to the JSONL file
with open(jsonl_filename, 'w') as file:
    for item in data:
        json_line = json.dumps({"text": item})
        file.write(json_line + '\n')

print(f"JSONL file '{jsonl_filename}' has been created.")