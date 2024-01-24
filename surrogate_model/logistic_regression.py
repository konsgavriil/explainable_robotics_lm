from sklearn.linear_model import LogisticRegression
from classification_model import ClassificationModel
from joblib import dump, load


class LogisticClassifier(ClassificationModel):

    def __init__(self, features, labels):
        super().__init__(features, labels)
        self.classifier = LogisticRegression()
        self.hyperparams = {"solver": ["lbfgs", "liblinear", "newton-cg", "newton-cholesky", "sag", "saga"]}

    def train_model(self):
        self.classifier.fit(self.features, self.labels)
        self.save_model()

    def predict(self, new_entry):
        return self.classifier.predict(new_entry)

    def save_model(self):
        """
        Stores the parameters of the trained model locally.
        """
        dump(self.classifier, "lr_params.joblib")

    def load_model(self):
        """
        Loads an existing model using a saved parameter file.
        """
        try:
            self.classifier = load("lr_params.joblib")
        except FileNotFoundError:
            print("Model file not found. Training now to derive params")
            self.train_model()
