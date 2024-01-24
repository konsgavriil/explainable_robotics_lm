from joblib import dump, load
from surrogate_model.classification_model import ClassificationModel
from sklearn.neighbors import KNeighborsClassifier


class KNNClassifier(ClassificationModel):

    def __init__(self, features, labels):
        super().__init__(features, labels)
        self.classifier = KNeighborsClassifier()
        self.hyperparams = {'leaf_size': [5, 10, 15, 20, 25, 30], 'metric': ['minkowski', 'canberra', 'chebyshev']}

    def train_model(self):
        self.classifier.fit(self.features, self.labels)
        self.save_model()

    def predict(self, new_entry):
        return self.classifier.predict(new_entry)

    def save_model(self):
        """
        Stores the parameters of the trained model locally.
        """
        dump(self.classifier, "s1_alpha_knn_params.joblib")

    def load_model(self):
        """
        Loads an existing model using a saved parameter file.
        """
        try:
            self.classifier = load("s1_alpha_knn_params.joblib")
        except FileNotFoundError:
            print("Model file not found. Training now to derive params")
            self.train_model()
