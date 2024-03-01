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
        
        return {"semantic_accuracy": total_acc/len(inputs), "semantic_accuracy": total_prec/len(inputs)}

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
    
    def derive_dm_for_s1(self):
        #If deploy is false and return is false, then the vehicle is idle with no activated behaviour.
        #If deploy is true and return is false, then the vehicle is surveying an area. 
        #If deploy is true and return is true, then the vehicle is returning to its starting point. 
        #If deploy is true, return is false, obstacle name is not equal to none, obstacle resolved is false and obstacle proximity has value nearby, close or very close, then the vehicle is surveying the area while avoiding an obstacle.
        #If deploy is true, return is true, obstacle name is not equal to none, obstacle resolved is false and obstacle proximity has value nearby, close or very close, then the vehicle is returning to its starting point while avoiding an obstacle.
        pass

    def derive_dm_for_s4(self):
        """
            If deploy = false, then the vessel is idle.
            If deploy = true, then the vehicle is moving within a predefined depth range. 
            If deploy = true and next_loiter_point, then the vehicle is loitering around a predefined set of waypoints.
            If deploy = true and return = true, then the vessel is returning to its starting point
            If deploy = true, return = false, next_waypoint != ‘none’ and next_waypoint != ‘starting_point’, then the vehicle is surveying an area designated by the user.
            If deploy = true, next_loiter_point != ‘none’ and periodic_ascent = true, then the vessel is surfacing to provide new GPS coordinates to command and control.
        """
        pass

    def derive_dm_for_m34(self):
        """
            If deploy is False:
                Outcome: The vessel is idle.
            If station_keep is True:
                Outcome: The vehicle will stay in place until further notice.
            If deploy is True and next_loiter_point is not 'none':
                Outcome: The vehicle is loitering.
            If deploy is True, next_loiter_point is not 'none', and obstacle_proximity is 'nearby' or 'close' or 'very_close':
                Outcome: The vehicle is loitering while avoiding an obstacle.
            If deploy is True, next_loiter_point is not 'none', and contact_range is 'close' or 'very_close':
                Outcome: The vehicle is loitering while avoiding another vessel.
            If deploy is True and return is True:
                Outcome: The vehicle is returning to its starting point.
            If deploy is True, return is True, and obstacle_proximity is 'nearby' or 'close' or 'very_close':
                Outcome: The vehicle returns to its starting point while avoiding an obstacle.
        """
        pass