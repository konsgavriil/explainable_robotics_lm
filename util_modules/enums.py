from enum import Enum


class MOOSIvPBehaviour(Enum):
    waypt_survey = 1
    waypt_return = 2
    obstacle_avd = 3
    max_depth = 4
    bhv_const_depth = 5


class MOOSIvPScenario(Enum):
    s1_alpha = 1
    s4_delta = 2
    m34_alpha_bo = 3


class ExplanationType(Enum):
    # all = 4
    contrastive = 3
    counterfactual = 2
    causal_explanation = 1


class SurrogateModel(Enum):
    SVM = 3
    NeuralNet = 2
    NaiveBayes = 5
    DecisionTree = 1
    NearestNeighbors = 4
