import evaluate
import pandas as pd
from semantic_accuracy import SemanticAccuracy

bleu_score = evaluate.load("bleu")
rouge_score = evaluate.load("rouge")
meteor_score = evaluate.load("meteor")
semantic_acc_score = SemanticAccuracy()

df = pd.read_csv("xarlm_base_contrastive_inference.csv")

preds = df["response"]
labels = df["label"]
input_texts = df["representation"]

r_score = rouge_score.compute(predictions=preds, references=labels, use_stemmer=True)
b_value = bleu_score.compute(predictions=preds, references=labels)['bleu']
m_score = meteor_score.compute(predictions=preds, references=labels)
sa_score = semantic_acc_score.compute(input_texts, preds)
print(f"Rouge: {r_score}, Bleu: {b_value}, Meteor: {m_score}, Semantic Accuracy: {sa_score}")