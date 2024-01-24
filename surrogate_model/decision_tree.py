from dtreeviz import dtreeviz
from dtreeviz.trees import *
from joblib import dump, load
from sklearn.tree import DecisionTreeClassifier
from surrogate_model.classification_model import ClassificationModel


class DTreeClassifier(ClassificationModel):
    """
    Module for training and predicting with a decision tree.
    """

    def __init__(self, features, labels):
        """
        Initialises the model and the datasets if a data frame is provided.
        :param data: Dataframe with features and target values.
        """
        super().__init__(features, labels)
        self.classifier = DecisionTreeClassifier(random_state=0)
        self.hyperparams = {"criterion": ["gini", "entropy", "log_loss"], "splitter": ["best", "random"],
                            "max_depth": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                            "random_state": [0, 1, 2], "max_leaf_nodes": [5, 10, 15, 20, 25, 30],
                            "min_impurity_decrease": [0.0, 1.0, 2.0]}

    def train_model(self):
        """
        Trains a model with the provided dataset and stores its parameters.
        """
        self.classifier.fit(self.features, self.labels)
        self.save_model()

    def predict(self, new_entry):
        prediction = self.classifier.predict(new_entry)
        return prediction

    def save_model(self):
        """
        Stores the parameters of the trained model locally.
        """
        dump(self.classifier, "s4_delta_dt_params.joblib")

    def load_model(self):
        """
        Loads an existing model using a saved parameter file.
        """
        try:
            self.classifier = load("s1_alpha_dt_params.joblib")
            self.classifier = self.classifier.best_estimator_
        except FileNotFoundError:
            print("Model file not found. Training now to derive params")
            # self.train_model()

    # def generate_figure(self, vehicle_state: np.ndarray):
    #     """
    #     Generates a graph of the decision tree and a trail based on a specific vehicle state.
    #     param vehicle_state: Given state that describes the vehicle's situation
    #     """
    #     viz = dtreeviz(self.classifier,
    #                    self.features,
    #                    self.labels,
    #                    target_name='behaviour',
    #                    feature_names=["ready_plan", "current_obj", "progress_type", "same_objective", "obstacle_found"],
    #                    class_names={0: "hold_position", 1: "obstacle_avoidance", 2: "replanned_transit",
    #                                 3: "survey", 4: "transit", 5: "wait"},
    #                    X=vehicle_state)
    #     viz.display()

    def retrieve_dt_info(self):
        """
        Prints the condition and leaf nodes and describes the criteria for each split.
        """
        n_nodes = self.classifier.tree_.node_count
        children_left = self.classifier.tree_.children_left
        children_right = self.classifier.tree_.children_right
        feature = self.classifier.tree_.feature
        threshold = self.classifier.tree_.threshold

        node_depth = np.zeros(shape=n_nodes, dtype=np.int64)
        is_leaves = np.zeros(shape=n_nodes, dtype=bool)
        stack = [(0, 0)]  # start with the root node id (0) and its depth (0)
        while len(stack) > 0:
            # `pop` ensures each node is only visited once
            node_id, depth = stack.pop()
            node_depth[node_id] = depth

            # If the left and right child of a node is not the same we have a split
            # node
            is_split_node = children_left[node_id] != children_right[node_id]
            # If a split node, append left and right children and depth to `stack`
            # so we can loop through them
            if is_split_node:
                stack.append((children_left[node_id], depth + 1))
                stack.append((children_right[node_id], depth + 1))
            else:
                is_leaves[node_id] = True

        print(
            "The binary tree structure has {n} nodes and has "
            "the following tree structure:\n".format(n=n_nodes)
        )
        for i in range(n_nodes):
            if is_leaves[i]:
                print(
                    "{space}node={node} is a leaf node.".format(
                        space=node_depth[i] * "\t", node=i
                    )
                )
            else:
                print(
                    "{space}node={node} is a split node: "
                    "go to node {left} if X[:, {feature}] <= {threshold} "
                    "else to node {right}.".format(
                        space=node_depth[i] * "\t",
                        node=i,
                        left=children_left[i],
                        feature=feature[i],
                        threshold=threshold[i],
                        right=children_right[i],
                    )
                )

    def get_visited_nodes(self, vehicle_state):
        """
        Extracts the indices of the visited nodes.
        param vehicle_state: State which affects the tree traversal.
        :return: List of node indices.
        """
        return self.classifier.decision_path(vehicle_state).indices.tolist()
