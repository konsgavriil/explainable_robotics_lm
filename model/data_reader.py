import pandas as pd

df = pd.read_csv("persistance/moos_ivp_csv/complete_datasets/mixed/mixed_test_dataset.csv")
output_dict = {"query": [], "representation": [], "response": []}
for index, row in df.iterrows():
    text = f"User query: {row['user_query']}, Representation: {row['representation']}"
    response = "lalato"
    output_dict["query"].append(row['user_query'])
    output_dict["representation"].append(row['representation'])
    output_dict["response"].append(response)

df_out = pd.DataFrame(output_dict)
print(df_out)