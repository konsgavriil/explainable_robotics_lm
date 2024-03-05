import torch
import wandb
import evaluate
import numpy as np
from peft import LoraConfig, get_peft_model
from datasets import load_dataset
from huggingface_hub import login
from semantic_accuracy import SemanticAccuracy
from transformers.trainer_utils import SchedulerType
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments

login("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")
wandb.login(key="e02f877bc61d440081963d6d9507c438fc3f32f1")
dataset_name = "konsgavriil/xarlm_all_types"
wandb.init(project="xarlm")
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
    sa_score = semantic_acc_score.compute(input_texts, decoded_preds)

    b_score = {"bleu": b_value}
    result = {**r_score, **b_score, **m_score, **n_score, **sa_score}
    return result

dataset = load_dataset(dataset_name)
base_model_name = "meta-llama/Llama-2-7b-hf"

peft_config = LoraConfig(
    lora_alpha=16,
    lora_dropout=0.1,
    r=64,
    bias="none",
    task_type="CAUSAL_LM",
)

tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

instruction_template = "### Instruction:"
response_template = "### Response:"
collator = DataCollatorForCompletionOnlyLM(instruction_template=instruction_template, response_template=response_template, tokenizer=tokenizer, mlm=False)


output_dir = "/mnt/xarlm/results/{}".format(dataset_name)

def wandb_hp_space(trial):
    return {
        "name": "all_types_exp_sweep",
        "method": "grid",
        "metric": {"name": "semantic_precision", "goal": "maximize"},
        "parameters": {
            "lr": {'values': [0.00005, 0.0001, 0.0002, 0.0004, 0.0007, 0.001]},
            "lr_scheduler_type": {'values': [SchedulerType.LINEAR, SchedulerType.COSINE, SchedulerType.COSINE_WITH_RESTARTS,
                                             SchedulerType.POLYNOMIAL, SchedulerType.CONSTANT, SchedulerType.CONSTANT_WITH_WARMUP,
                                             SchedulerType.INVERSE_SQRT, SchedulerType.REDUCE_ON_PLATEAU]},
            "warmup_steps": {'values': [100, 200, 300, 400, 500]},
            "max_steps": {'values': [500, 1000, 1500, 2000]},
            "per_device_train_batch_size": {'values': [3, 6, 9, 12]},
        },
    }

def model_init(trial):
    base_model = AutoModelForCausalLM.from_pretrained(base_model_name, device_map="auto", trust_remote_code=True, token=True)
    base_model.config.use_cache = False
    base_model.config.pretraining_tp = 1 
    base_model = base_model.to(torch.bfloat16)
    model = get_peft_model(base_model, peft_config)
    return model

training_args = TrainingArguments(
    output_dir=output_dir,
    gradient_accumulation_steps=3,
    logging_steps=10,
    eval_steps=100,
    report_to="wandb", 
    evaluation_strategy="steps",
    do_eval=True,
)

max_seq_length = 512

trainer = SFTTrainer(
    model=None,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    dataset_text_field="text",
    data_collator=collator,
    max_seq_length=max_seq_length,
    tokenizer=tokenizer,
    args=training_args,
    model_init=model_init,
    compute_metrics=lambda p: compute_metrics(p, dataset["validation"]["text"]),
    preprocess_logits_for_metrics = preprocess_logits_for_metrics,
)

best_trial = trainer.hyperparameter_search(
    backend="wandb",
    hp_space=wandb_hp_space,
)