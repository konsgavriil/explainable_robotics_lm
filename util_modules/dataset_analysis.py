import re
import nltk
import json
import pandas as pd
from nltk.stem import PorterStemmer

class DatasetAnalysis:

    def __init__(self, file_path) -> None:
        self.inputs = []
        self.outputs = []
        self.stemmer = PorterStemmer()        
        with open(file_path, 'r') as file:
            for line in file:
                entry = json.loads(line)
                instruction_text = entry["text"].split("### Prompt:")[1].split("### Response:")[0].strip()
                self.inputs.append(instruction_text)
                response_text = entry["text"].split("### Response:")[1].strip()
                self.outputs.append(response_text)
        self.all_text = self.inputs + self.outputs
        # Tokenization and preprocessing
        self.input_tokens = [self.extract_tokens(doc.lower()) for doc in self.inputs]
        self.output_tokens = [self.extract_tokens(doc.lower()) for doc in self.outputs]
        self.all_text_tokens = [self.extract_tokens(doc.lower()) for doc in self.all_text]
        # Basic statistics
        self.vocab = set(token for doc in self.all_text_tokens for token in doc)
    
    def calc_number_of_spatial_tokens(self, tokens):
        # spatial_refs = ["point", "obstacle", "close", "far", "nearby", "very close", "very far", "east", "west", "north", "south", "northeast",
        #                 "northwest", "southeast", "southwest", "medium", "medium_distance", "cpa", "giveway", "stern", "head on", "stand on", "bow", "inextremis",
        #                 "unsure_bow", "direction", "new loiter area", "pointstart", "starting point", "starting_point", "deep", "on surface", "moderate depth",
        #                 "shallow", "very deep", "ascent", "ascending"]
        
        spatial_refs = ["obstacle", "a", "b", "c", "e", "proximity", "close", "far", "medium", "distance", "nearby", "point", "0", 
                                 "1", "2", "3", "4", "5", "6", "7", "8", "9", "direction", "north", "east", "south", "west", "northeast", "northwest",
                                 "southeast", "southwest", "waypoint", "starting", "contact","range"]
        occurances = 0
        for doc in tokens:
            for token in doc:
                if token in spatial_refs:
                    occurances += 1
                    break
        return occurances, len(tokens)
    
    def calc_spatial_tokens_per_entry(self, tokens):
        spatial_refs = ["obstacle", "a", "b", "c", "e", "proximity", "close", "far", "medium", "distance", "nearby", "point", "0", 
                                 "1", "2", "3", "4", "5", "6", "7", "8", "9", "direction", "north", "east", "south", "west", "northeast", "northwest",
                                 "southeast", "southwest", "waypoint", "starting", "contact","range"]
        occurances = 0
        for doc in tokens:
            for token in doc:
                if token in spatial_refs:
                    occurances += 1
        return occurances / len(tokens)
    
    def calc_vocabulary_size(self):
        return len(self.vocab)

    def calc_token_frequency_distribution(self, tokens):
        token_freq = nltk.FreqDist(token for doc in tokens for token in doc)
        return token_freq
        # Visualization
        # token_freq.plot(20, cumulative=False)

    def calc_document_stats(self, tokens):
        # Number of documents
        doc_lengths = [len(doc) for doc in tokens]
        # Average Document length
        avg_doc_length = sum(len(doc) for doc in tokens) / len(tokens)
        # Longest and shortest documents
        longest_doc = max(doc_lengths)
        shortest_doc = min(doc_lengths)
        return avg_doc_length, shortest_doc, longest_doc
    
    def extract_tokens(self, sentence):
        sentence = sentence.replace("_", " ")
        words = re.findall(r'\b\w+\b', sentence)
        unique_words = set(word.lower() for word in words)
        unique_words = {self.stemmer.stem(word) for word in unique_words}
        return unique_words


da = DatasetAnalysis("persistance/moos_ivp_jsonl/prompt2/causal/causal_dataset.jsonl")
vocab_size = da.calc_vocabulary_size()
input_avg_length, input_shortest_len, input_longest_len = da.calc_document_stats(da.input_tokens)
output_avg_length, output_shortest_len, output_longest_len = da.calc_document_stats(da.output_tokens)
spatial_occ_input, input_doc_num = da.calc_number_of_spatial_tokens(da.input_tokens)
avg_spatial_input = da.calc_spatial_tokens_per_entry(da.input_tokens)
spatial_occ_output, output_doc_num = da.calc_number_of_spatial_tokens(da.output_tokens)
avg_spatial_output = da.calc_spatial_tokens_per_entry(da.output_tokens)
spatial_percentage_input = spatial_occ_input / input_doc_num
spatial_percentage_output = spatial_occ_output / output_doc_num
spatial_percentage_input = "{:.2f}%".format(spatial_percentage_input * 100)
spatial_percentage_output = "{:.2f}%".format(spatial_percentage_output * 100)

# Display statistics
stats_df = pd.DataFrame({
    "Dataset Size": [len(da.inputs)],
    "Vocabulary Size": [vocab_size],
    "Average Input Length": [input_avg_length],
    "Longest Input Length": [input_longest_len],
    "Shortest Input Length": [input_shortest_len],
    "Average Output Length": [output_avg_length],
    "Longest Output Length": [output_longest_len],
    "Shortest Output Length": [output_shortest_len],
    "Inputs with spatial tokens": f"{spatial_occ_input}/{input_doc_num} ({spatial_percentage_input})",
    "Average number of spatial tokens per input": f"{avg_spatial_input}",
    "Outputs with spatial tokens": f"{spatial_occ_output}/{output_doc_num} ({spatial_percentage_output})",
    "Average number of spatial tokens per output": f"{avg_spatial_output}",
})
print(stats_df)