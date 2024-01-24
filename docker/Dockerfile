FROM nvcr.io/nvidia/pytorch:23.12-py3
 
WORKDIR /workspace

COPY llama2_peft_lora.py /workspace/xarlm/llama2_peft_lora.py

SHELL ["/bin/bash", "-c"]

# Install Conda
RUN apt-get update && apt-get install -y \
    wget \
    bzip2

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh

# Set the Conda environment path
ENV PATH /opt/conda/bin:$PATH

RUN conda init

# Create Conda Environment
RUN conda create -n xarlm python=3.11

RUN echo "source activate xarlm" > ~/.bashrc
ENV PATH /opt/conda/envs/xarlm/bin:$PATH

# RUN conda activate xarlm

RUN pip install transformers\
&& pip install datasets \
&& pip install peft \
&& pip install trl \
&& pip install wandb \
&& pip install bitsandbytes \
