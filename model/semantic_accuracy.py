import re
from nltk.stem import PorterStemmer

class SemanticAccuracy:

    def __init__(self) -> None:
        self.stemmer = PorterStemmer()
        self.spatial_ref_list = ["obstacle", "a", "b", "c", "e", "proximity", "close", "far", "medium", "distance", "nearby", "point", "0", 
                                 "1", "2", "3", "4", "5", "6", "7", "8", "9", "direction", "north", "east", "south", "west", "northeast", "northwest",
                                 "southeast", "southwest", "waypoint", "starting", "contact","range"]
        self.state_ref_list = ["objective", "deploy", "return", "resolved", "behaviour", "stage", "advanced", "completed", "transit", "speed", "fast", "idle", "low",
                               "max", "moderate", "very", "heading", "alpha", "cycled", "gps", "update", "received", "depth", "deep", "moderate", "surface", "shallow",
                               "henry", "station", "keep", "collision", "avoidance", "mode", "cpa", "giveway", "stern", "headon", "standon", "inextremis", "unsure bow",
                               "gilda"]
        self.decision_ref_list = ["return", "survey", "avoid", "obstacle", "loiter", "maintain", "depth", "maxdepth", "constant", "periodic", "surface", 
                                  "collision", "station-keep", "station", "keep"]
        
        self.token_dict = {}  

        self.spatial_ref_list = list(set(self.stemmer.stem(word) for word in self.spatial_ref_list))
        self.state_ref_list = list(set(self.stemmer.stem(word) for word in self.state_ref_list))
        self.decision_ref_list = list(set(self.stemmer.stem(word) for word in self.decision_ref_list))

    def compute(self, inputs, outputs) -> float:
        overall_acc, overall_prec = 0.0, 0.0

        if len(inputs) != len(outputs):
            raise ValueError("Model input and output length is not the same.")

        for input, output in zip(inputs, outputs):        

            input_tokens = self.extract_tokens(input)
            output_tokens = self.extract_tokens(output)

            spatial_ref = self.count_spatial_references(output_tokens)
            state_ref = self.count_state_references(output_tokens)
            decision_ref = self.count_decision_references(output_tokens)

            spatial_acc, spatial_prec, state_acc, state_prec , decision_acc, decision_prec = None, None, None, None, None, None

            refs = 0
            if spatial_ref > 0:
                spatial_acc, spatial_prec = self.calc_spatial_score(input_tokens, output_tokens, spatial_ref)
                refs += 1
            if state_ref > 0:
                state_acc, state_prec = self.calc_state_score(input_tokens, output_tokens, state_ref)
                refs += 1
            if decision_ref > 0:
                decision_acc, decision_prec = self.calc_decision_score(input_tokens, output_tokens, decision_ref)
                refs += 1

            total_acc = 0
            total_prec = 0
            if spatial_acc and spatial_prec:
                total_acc += spatial_acc
                total_prec += spatial_prec
            if state_acc and state_prec:
                total_acc += state_acc
                total_prec += state_prec
            if decision_acc and decision_prec:
                total_acc += decision_acc
                total_prec += decision_prec

            if refs > 0: 
                total_acc = total_acc / refs
                total_prec = total_prec / refs

            if 0.0 <= total_acc <= 1.0 and 0.0 <= total_prec <= 1.0:
                overall_acc += total_acc
                overall_prec += total_prec
            else:
                raise ValueError(f"Output value is out of the specified range: [0.0, 1.0]")
        
        return {"semantic_accuracy": overall_acc/len(inputs), "semantic_precision": overall_prec/len(inputs)}

    def calc_spatial_score(self, input_tokens, output_tokens, total_references) -> float:
        input_spatial_tokens = input_tokens.intersection(self.spatial_ref_list)
        correct_references = input_spatial_tokens.intersection(output_tokens)
        print("Spatial correct references:", correct_references)
        tp = len(correct_references)
        tn = len(output_tokens) - total_references
        fp = total_references - len(correct_references)
        acc = (tp + tn) / len(output_tokens)
        prec = tp / (tp+fp) 
        return acc, prec

    def calc_state_score(self, input_tokens, output_tokens, total_references) -> float:
        input_state_tokens = input_tokens.intersection(self.state_ref_list)
        correct_references = input_state_tokens.intersection(output_tokens)
        print("State correct references:", correct_references)
        tp = len(correct_references)
        tn = len(output_tokens) - total_references
        fp = total_references - len(correct_references)
        acc = (tp + tn) / len(output_tokens)
        prec = tp / (tp+fp) 
        return acc, prec
    
    def calc_decision_score(self, input_tokens, output_tokens, total_references) -> float:
        input_decision_tokens = input_tokens.intersection(self.decision_ref_list)
        correct_references = input_decision_tokens.intersection(output_tokens)
        print("Decision correct references:", correct_references)
        tp = len(correct_references)
        tn = len(output_tokens) - total_references
        fp = total_references - len(correct_references)
        acc = (tp + tn) / len(output_tokens)
        prec = tp / (tp+fp) 
        return acc, prec
            
    def count_spatial_references(self, output_tokens) -> int:
        references = 0
        print("Spatial Utterances")
        for utterance in output_tokens:
            if utterance in self.spatial_ref_list:
                references += 1
                print(utterance)
        return references
    
    def count_state_references(self, output_tokens) -> int:
        references = 0
        print("State Utterances")
        for utterance in output_tokens:
            if utterance in self.state_ref_list:
                references += 1
                print(utterance)
        return references

    def count_decision_references(self, output_tokens) -> int:
        references = 0
        print("Decision Utterances")
        for utterance in output_tokens:
            if utterance in self.decision_ref_list:
                references += 1
                print(utterance)
        return references

    def extract_tokens(self, sentence):
        sentence = sentence.replace("_", " ")
        words = re.findall(r'\b\w+\b', sentence)
        unique_words = set(word.lower() for word in words)
        unique_words = {self.stemmer.stem(word) for word in unique_words}
        return unique_words