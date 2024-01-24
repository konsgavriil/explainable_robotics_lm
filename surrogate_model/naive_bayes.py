from sklearn.naive_bayes import CategoricalNB
from surrogate_model.classification_model import ClassificationModel
from joblib import dump, load


class NaiveBayes(ClassificationModel):

    def __init__(self, features, labels):
        super().__init__(features, labels)
        self.classifier = CategoricalNB()
        # self.classifier = GaussianNB()
        # self.hyperparams = {"var_smoothing": [1e-9]}
        self.hyperparams = {"alpha": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0], "fit_prior": [True, False]}

    def train_model(self):
        self.classifier.fit(self.features, self.labels)
        self.save_model()

    def predict(self, new_entry):
        return self.classifier.predict(new_entry)

    def save_model(self):
        """
        Stores the parameters of the trained model locally.
        """
        dump(self.classifier, "nb_params.joblib")

    def load_model(self):
        """
        Loads an existing model using a saved parameter file.
        """
        try:
            self.classifier = load("nb_params.joblib")
        except FileNotFoundError:
            print("Model file not found. Training now to derive params")
            self.train_model()
