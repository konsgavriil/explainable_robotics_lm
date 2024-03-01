import os
import torch
import wandb
import evaluate
import numpy as np
from peft import LoraConfig
from datasets import load_dataset
from huggingface_hub import login
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM
from semantic_accuracy import SemanticAccuracy
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, AutoTokenizer, TrainingArguments

login("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")
wandb.login(key="e02f877bc61d440081963d6d9507c438fc3f32f1")
os.environ["WANDB_PROJECT"] = "xarlm"  # name your W&B project
os.environ["WANDB_LOG_MODEL"] = "checkpoint"  # log all model checkpoints

bleu_score = evaluate.load("bleu")
rouge_score = evaluate.load("rouge")
meteor_score = evaluate.load("meteor")
nist_mt_score = evaluate.load("nist_mt")
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
    n_score = nist_mt_score.compute(predictions=decoded_preds, references=decoded_labels)
    sa_score = semantic_acc_score.compute(input=input_texts, output=decoded_preds)

    b_score = {"bleu": b_value}
    result = {**r_score, **b_score, **m_score, **n_score, **sa_score}
    return result

dataset_name = "konsgavriil/xarlm_causal_p2"
dataset = load_dataset(dataset_name)
base_model_name = "meta-llama/Llama-2-7b-hf"

base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    device_map="auto",
    trust_remote_code=True,
    token=True
)

base_model.config.use_cache = False

# More info: https://github.com/huggingface/transformers/pull/24906
base_model.config.pretraining_tp = 1 

# Set the torch_dtype for the model
base_model = base_model.to(torch.bfloat16)

peft_config = LoraConfig(
    lora_alpha=16,
    lora_dropout=0.1,
    r=64,
    bias="none",
    task_type="CAUSAL_LM",
)

tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
# tokenizer.pad_token = tokenizer.eos_token
tokenizer.add_special_tokens({'pad_token': '[PAD]'})

instruction_template = "### Prompt:"
response_template = "### Response:"
collator = DataCollatorForCompletionOnlyLM(instruction_template=instruction_template, response_template=response_template, tokenizer=tokenizer, mlm=False)


output_dir = "/mnt/xarlm/results/causal_p2"

training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    logging_steps=10,
    eval_steps=10,
    max_steps=2000,
    report_to="wandb", 
    evaluation_strategy="steps",
    do_eval=True,
    warmup_steps=int(len(dataset["train"]) / 8),
    greater_is_better=True,
    # metric_for_best_model='eval_loss',
    load_best_model_at_end=True
)

max_seq_length = 512

trainer = SFTTrainer(
    model=base_model,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    peft_config=peft_config,
    dataset_text_field="text",
    data_collator=collator,
    max_seq_length=max_seq_length,
    tokenizer=tokenizer,
    args=training_args,
    compute_metrics=lambda p: compute_metrics(p, dataset["validation"]["text"]),
    # compute_metrics=compute_metrics,
    preprocess_logits_for_metrics = preprocess_logits_for_metrics,
    # callbacks=[EarlyStoppingCallback(early_stopping_patience=10)]
)

trainer.train()

# Evaluate on the validation set
results = trainer.evaluate()

# Print validation loss
print("Validation Loss:", results["eval_loss"])

output_dir = os.path.join(output_dir, "best_checkpoint_causal_p2")
trainer.model.save_pretrained(output_dir)