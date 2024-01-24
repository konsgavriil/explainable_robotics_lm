from abc import ABC, abstractmethod
from sklearn.model_selection import KFold, GridSearchCV, cross_validate


class ClassificationModel(ABC):

    def __init__(self, features, labels):
        super().__init__()
        self.classifier = None
        self.hyperparams = None
        self.features = features
        self.labels = labels
        self.predict_fn = lambda x: self.classifier.predict_proba(x).astype(float)

    @abstractmethod
    def train_model(self):
        pass

    @abstractmethod
    def predict(self, new_entry):
        pass

    @abstractmethod
    def save_model(self):
        pass

    def select_model(self):
        trials = 20
        best_score = 0
        metrics = None
        best_clf = None

        for i in range(trials):
            print("Trial:", i)
            inner_cv = KFold(n_splits=5, shuffle=True, random_state=i)
            outer_cv = KFold(n_splits=5, shuffle=True, random_state=i)

            clf = GridSearchCV(estimator=self.classifier, param_grid=self.hyperparams, cv=inner_cv)
            # nested_score = cross_val_score(clf, X=self.features, y=self.labels, cv=outer_cv)
            nested_score = cross_validate(clf, X=self.features, y=self.labels, cv=outer_cv, scoring=("accuracy",
                                          "precision_macro", "recall_macro", "f1_macro"))
            print(nested_score["test_accuracy"].mean())
            if nested_score["test_accuracy"].mean() > best_score:
                best_score = nested_score["test_accuracy"].mean()
                metrics = nested_score
                best_clf = clf

        self.classifier = best_clf.fit(self.features, self.labels)
        self.save_model()

        return metrics

    def score_model(self, columns):
        trials = 20
        best_score = 0
        result = None

        for i in range(trials):
            print("Trial:", i)
            outer_cv = KFold(n_splits=5, shuffle=True, random_state=i)

            nested_score = cross_validate(self.classifier, X=self.features.iloc[:, columns], y=self.labels, cv=outer_cv, scoring=("accuracy",
                                          "precision_macro", "recall_macro", "f1_macro"))
            print(nested_score["test_accuracy"].mean())
            if nested_score["test_accuracy"].mean() > best_score:
                best_score = nested_score["test_accuracy"].mean()
                result = nested_score

        return result

    # def score_model(self, X_train, X_test, y_train, y_test):
    #     self.classifier.fit(X_train, y_train)
    #     y_pred = self.classifier.predict(X_test)
    #     accuracy = metrics.accuracy_score(y_test, y_pred)
    #     precision = metrics.precision_score(y_test, y_pred, average="macro")
    #     recall = metrics.recall_score(y_test, y_pred, average="macro")
    #     f1 = metrics.f1_score(y_test, y_pred, average="macro")
    #     return accuracy, precision, recall, f1

    # def print_confusion_matrix(self):
    #     labels = ["wait", "transit", "survey", "hold_position"]
    #     test_pred_decision_tree = self.classifier.predict(self.x_test)
    #     metrics.ConfusionMatrixDisplay.from_predictions(self.y_test, test_pred_decision_tree, display_labels=labels, cmap="magma")
    #     plt.show()




