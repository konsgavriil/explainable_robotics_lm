import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

from surrogate_model.nearest_neighbours import KNNClassifier

from surrogate_model.decision_tree import DTreeClassifier
from sklearn import tree
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
import dtreeviz
import numpy as np

from surrogate_model.naive_bayes import NaiveBayes
from surrogate_model.neural_network import NeuralNetwork
from surrogate_model.support_vector_machine import SupportVectorMachine

if __name__ == '__main__':
    df = pd.read_csv("persistance/moos_ivp_csv/s4_delta_sm_training.csv")
    features = df.iloc[:, :4]
    labels = df.iloc[:, -1]
    enc = OrdinalEncoder()
    l_enc = LabelEncoder()
    enc.fit(features)
    X = enc.transform(features)
    l_enc.fit(labels)
    Y = l_enc.transform(labels)

    # X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
    # clf = KNNClassifier(X, Y)
    # clf = DTreeClassifier(X, Y)
    clf = NeuralNetwork(X, Y)
    # clf.load_model()
    # text_representation = tree.export_text(clf.classifier)
    # print(text_representation)
    # clf.retrieve_dt_info()
    # clf = clf.classifier.best_estimator_
    # viz_model = dtreeviz.model(clf.classifier, X_train=X, y_train=Y, feature_names=features.columns, target_name="behaviour", class_names=np.unique(labels.values))
    # v = viz_model.view()
    # v.show()
    # v.save("s4_delta_decision_boundaries.svg")
    metrics = clf.select_model()
    print(metrics)
    # y_pred = clf.predict(X_test)
    #
    # from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
    #
    # accuracy = accuracy_score(y_test, y_pred)
    # print(f'Accuracy: {accuracy:.4f}')
    # #
    # print('Classification Report:')
    # print(classification_report(y_test, y_pred))
    #
    # # print('Confusion Matrix:')
    # # print(confusion_matrix(y_test, y_pred))
    #
    # confusion_matrix = confusion_matrix(y_test, y_pred)
    # #
    # cm_display = ConfusionMatrixDisplay(confusion_matrix=confusion_matrix)
    #
    # import matplotlib.pyplot as plt
    # cm_display.plot()
    # plt.show()