import os
import wandb
import evaluate
import numpy as np
from peft import LoraConfig
from datasets import load_dataset
from huggingface_hub import login
from semantic_accuracy import SemanticAccuracy
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, EarlyStoppingCallback

login("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")
wandb.login(key="e02f877bc61d440081963d6d9507c438fc3f32f1")
base_model_name = "google/gemma-2b"
dataset_name = "konsgavriil/causal"
project_name = "{}/{}".format(base_model_name.split("/")[-1], dataset_name.split("/")[-1])
os.environ["WANDB_LOG_MODEL"] = "checkpoint"  # log all model checkpoints
wandb.init(project="xarlm", name=dataset_name)
bleu_score = evaluate.load("bleu")
rouge_score = evaluate.load("rouge")
meteor_score = evaluate.load("meteor")
semantic_acc_score = SemanticAccuracy()

def preprocess_logits_for_metrics(logits, labels):
    if isinstance(logits, tuple):
        logits = logits[0]
    return logits.argmax(dim=-1)

def compute_metrics(eval_preds, input_texts):
    preds, labels = eval_preds

    if isinstance(preds, tuple):
        preds = preds[0]

    # Replace -100 in the preds as we can't decode them
    preds = np.where(preds != -100, preds, tokenizer.pad_token_id)

    # Decode generated summaries into text
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)

    # Replace -100 in the labels as we can't decode them
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    
    # Decode reference summaries into text
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    
    # ROUGE expects a newline after each sentence
    decoded_preds = ["\n".join(pred.strip()) for pred in decoded_preds]

    decoded_labels = ["\n".join(label.strip()) for label in decoded_labels]
    # Compute scores
    r_score = rouge_score.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
    b_value = bleu_score.compute(predictions=decoded_preds, references=decoded_labels)['bleu']
    m_score = meteor_score.compute(predictions=decoded_preds, references=decoded_labels)
    sa_score = semantic_acc_score.compute(input_texts, decoded_preds)

    b_score = {"bleu": b_value}
    result = {**r_score, **b_score, **m_score, **sa_score}
    return result

def formatting_prompts_func(example):
    output_texts = []
    for i in range(len(example['representation'])):
        text = f"### Instruction: Here's a representation that describes the current state of an autonomous maritime vehicle:\n{example['representation'][i]}\nGiven the provided representation, please respond to the following user query in no more than three sentences:\n{example['user_query'][i]} \n### Response: {example['explanation'][i]}"
        # text = f"### Instruction: Here's a representation that describes the current state of an autonomous maritime vehicle:\n{example['representation'][i]}\nRespond to the following what-if query in a maximum of three sentences. Additionally, include a state difference that illustrates the alterations in the user query.\n{example['user_query'][i]} \n### Response: {example['explanation'][i]}\n{example['permutation'][i]}"
        # cnt_text = f"### Instruction: Below is a representation depicting the current state of an autonomous maritime vehicle:\n{example['representation'][i]}\nRespond to the following why-not query in a maximum of three sentences. Additionally, include a behaviour difference that illustrates the alterations in the user query.{example['user_query'][i]} \n### Response: {example['explanation'][i]}\n{example['permutation'][i]}"
        output_texts.append(text)
    return output_texts

dataset = load_dataset(dataset_name)

base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    device_map="auto",
    token=True,
)

peft_config = LoraConfig(
    lora_alpha=16,
    lora_dropout=0.1,
    r=64,
    bias="none",
    task_type="CAUSAL_LM",
)

tokenizer = AutoTokenizer.from_pretrained(base_model_name, Token=True)

response_template = "\n### Response:"
response_template_ids = tokenizer.encode(response_template, add_special_tokens=False)[2:]
collator = DataCollatorForCompletionOnlyLM(response_template=response_template_ids, tokenizer=tokenizer)

output_dir = "/mnt/xarlm/results/{}".format(dataset_name)

training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=5,
    per_device_train_batch_size=3,
    gradient_accumulation_steps=1,
    learning_rate=2e-4,
    logging_steps=20,
    eval_steps=100,
    max_steps=-1,
    report_to="wandb", 
    evaluation_strategy="steps",
    do_eval=True,
    greater_is_better=True,
    metric_for_best_model = 'eval_loss',
    load_best_model_at_end=True,
    fp16=True
)

max_seq_length = 256

trainer = SFTTrainer(
    model=base_model,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    peft_config=peft_config,
    formatting_func=formatting_prompts_func,
    data_collator=collator,
    max_seq_length=max_seq_length,
    tokenizer=tokenizer,
    args=training_args,
    compute_metrics=lambda p: compute_metrics(p, dataset["validation"]["representation"]),
    preprocess_logits_for_metrics = preprocess_logits_for_metrics,
    callbacks = [EarlyStoppingCallback(early_stopping_patience=10)]
)

trainer.train()
trainer.evaluate()
wandb.finish()