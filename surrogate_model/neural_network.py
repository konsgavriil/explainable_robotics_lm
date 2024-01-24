from sklearn.neural_network import MLPClassifier
from joblib import dump, load
from surrogate_model.classification_model import ClassificationModel


class NeuralNetwork(ClassificationModel):

    def __init__(self, features, labels):
        super().__init__(features, labels)
        self.classifier = MLPClassifier()
        # self.hyperparams = {"hidden_layer_sizes": [(5, 50), (10, 100), (15, 100), (10, 150)], "max_iter": [1000]}
        self.hyperparams = {"hidden_layer_sizes": [(5, 50), (10, 100), (15, 150), (20, 200), (25, 200)], "max_iter": [2000]}

    def train_model(self):
        self.classifier.fit(self.features, self.labels)
        self.save_model()

    def predict(self, new_entry):
        return self.classifier.predict(new_entry)

    def save_model(self):
        """
        Stores the parameters of the trained model locally.
        """
        dump(self.classifier, "s1_alpha_nn_params.joblib")

    def load_model(self):
        """
        Loads an existing model using a saved parameter file.
        """
        try:
            self.classifier = load("s1_alpha_nn_params.joblib")
            self.classifier = self.classifier.best_estimator_

        except FileNotFoundError:
            print("Model file not found. Training now to derive params")
            # self.train_model()

