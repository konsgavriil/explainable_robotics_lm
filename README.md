# Enhancing Situation Awareness through Model-Based Explanation Generation

This repository contains the **source code and dataset** used in the paper:

> **K. Gavriilidis, I. Konstas, H. Hastie, A. Munafo, and W. Pang**  
> *Enhancing Situation Awareness through Model-Based Explanation Generation*  
> In *Proceedings of the 2nd Workshop on Practical LLM-assisted Data-to-Text Generation (Practical D2T 2024)*, Tokyo, Japan, pp. 7–16.  
> [[ACL Anthology Link]](https://aclanthology.org/2024.practicald2t-1.2) [[XARLM Datasets]](https://drive.google.com/drive/folders/1F40oo4bp209e96jneQYuVta4wDww7zka?usp=sharing) 

---

## Overview

In Human-In-The-Loop applications, operators require a clear understanding of a robot’s **state, rationale, and projected behaviour** to maintain trust and effectively assist. This repository provides the implementation and resources for evaluating **explanation styles**—causal, counterfactual, and contrastive—using **large language models (LLMs)**.

We introduce **XARLM (eXplainable Autonomous Robot Language Model)**, which transforms vehicle states and user queries into **natural language explanations** to enhance situation awareness.

Key contributions:
- A **dataset** of 8,051 annotated instances from **maritime autonomous missions**.  
- Three **fine-tuning tasks** for causal, counterfactual, and contrastive explanations.  
- Code for **fine-tuning LLMs** (Mistral, LLaMA2, Falcon) on explanation generation.  
- Evaluation scripts for **automatic metrics** (BLEU, ROUGE, METEOR, Semantic Accuracy/Precision).  
- Results from **two user studies** on explanation effectiveness and user preferences.  

---

## Contents

```
├── annotation/                  # All modules for data annotation are included here
│   ├── auxiliary/             # Annotation of MOOS-IvP initial datasets
│   ├── llm_annotation/           # Annotation of datasets with OpenAI API
│
├── model/                 # All of the modules for fine-tuning, inference and evaluation are included here
│   ├── ablation/              # Modules used for ablation study
│   └── finetuning/           # Folder with finetuning modules of LLMs 
│   ├── inference/        # Folder with modules used for inference
│   └── metrics/           # Defined metrics to measure semantic accuracy
│
├── parser/             # Modules for extracting features from MOOS-IvP logs
├── user_study/             # Resources and webpage materials used in user study 
├── util_modules/             # Additional modules used across the whole project
├── README.md             # This file
└── environment.yml       # Conda environment file with dependencies 
```

---

## Dataset

The dataset is based on **MOOS-IvP** simulated maritime missions, featuring three scenarios with varying complexity (survey, loiter, multi-vehicle). Each instance contains:
- **Vehicle states** (objectives, behaviours, headings, obstacles, etc.)  
- **User queries** (causal, what-if, why-not)  
- **Explanations** in three styles:  
  - **Causal** (justification of behaviour)  
  - **Counterfactual** (what-if reasoning)  
  - **Contrastive** (why-not reasoning)  

**Statistics:**
- Total: **8051 instances**  
- Causal: 1151, Counterfactual: 3450, Contrastive: 3450  
- Includes **spatial tokens**, state updates, and behaviour permutations  

All data is released under a **Creative Commons Attribution (CC-BY)** license.

---

## Usage

### Requirements

Install requirements with:
```bash
conda env create -f environment.yml
```

## Results

- **Mistral-7B** achieved the best performance across explanation types.  
- **Causal explanations** yielded the highest accuracy for decision-making queries.  
- **Contrastive explanations** were most effective for spatial queries.  
- **User preference study**: 70% favoured **template-based explanations**, but LLM-generated explanations performed comparably in situational awareness tasks.  

See `results/` for detailed metrics and user study analysis.

---

## Citation

If you use this repository, please cite our paper:

```bibtex
@inproceedings{gavriilidis2024enhancing,
  title={Enhancing Situation Awareness through Model-Based Explanation Generation},
  author={Gavriilidis, Konstantinos and Konstas, Ioannis and Hastie, Helen and Munafo, Andrea and Pang, Wei},
  booktitle={Proceedings of the 2nd Workshop on Practical LLM-assisted Data-to-Text Generation},
  year={2024},
  pages={7--16},
  publisher={Association for Computational Linguistics}
}
```

---

## Acknowledgements

This work was funded and supported by:  
- **EPSRC CDT in Robotics and Autonomous Systems (EP/S023208/1)**  
- **SeeByte Ltd**  
- **Scottish Research Partnership in Engineering (SRPe)**
