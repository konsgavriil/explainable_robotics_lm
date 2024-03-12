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
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, AutoTokenizer, TrainingArguments, EarlyStoppingCallback

login("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")
wandb.login(key="e02f877bc61d440081963d6d9507c438fc3f32f1")
dataset_name = "konsgavriil/xarlm_causal_p5"
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

dataset = load_dataset(dataset_name)
base_model_name = "meta-llama/Llama-2-7b-hf"

compute_dtype = getattr(torch, "float16")

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=compute_dtype,
    bnb_4bit_use_double_quant=False,
)

base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    quantization_config=quant_config,
    device_map="auto",
    trust_remote_code=True,
    token=True,
)

base_model.config.use_cache = False
base_model.config.pretraining_tp = 1 

# Set the torch_dtype for the model
#base_model = base_model.to(torch.bfloat16)

peft_config = LoraConfig(
    lora_alpha=16,
    lora_dropout=0.1,
    r=64,
    bias="none",
    task_type="CAUSAL_LM",
)

tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

response_template = "\n### Response:"
response_template_ids = tokenizer.encode(response_template, add_special_tokens=False)
collator = DataCollatorForCompletionOnlyLM(response_template=response_template_ids, tokenizer=tokenizer)

output_dir = "/mnt/xarlm/results/{}".format(dataset_name)

training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=2,
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
    metric_for_best_model = 'bleu',
    load_best_model_at_end=True
)

# max_seq_length = 512
max_seq_length = 256

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
    preprocess_logits_for_metrics = preprocess_logits_for_metrics,
    callbacks = [EarlyStoppingCallback(early_stopping_patience=10)]
)

trainer.train()

# Evaluate on the validation set
results = trainer.evaluate()

# Print validation loss
print("Validation Loss:", results["eval_loss"])

output_dir = os.path.join(output_dir, dataset_name)
trainer.model.save_pretrained(output_dir)
wandb.finish()