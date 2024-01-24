from sklearn.svm import SVC
from surrogate_model.classification_model import ClassificationModel
from joblib import dump, load


class SupportVectorMachine(ClassificationModel):

    def __init__(self, features, labels):
        super().__init__(features, labels)
        self.classifier = SVC()
        self.hyperparams = [{"kernel": ["rbf"], "gamma": [1e-3, 1e-4], "C": [1, 10, 100, 1000]},
                            {"kernel": ["linear"], "C": [1, 10, 100, 1000]}]

    def train_model(self):
        self.classifier.fit(self.features, self.labels)
        self.save_model()

    def predict(self, new_entry):
        return self.classifier.predict(new_entry)

    def save_model(self):
        """
        Stores the parameters of the trained model locally.
        """
        dump(self.classifier, "svm_params.joblib")

    def load_model(self):
        """
        Loads an existing model using a saved parameter file.
        """
        try:
            self.classifier = load("svm_params.joblib")
        except FileNotFoundError:
            print("Model file not found. Training now to derive params")
            self.train_model()
