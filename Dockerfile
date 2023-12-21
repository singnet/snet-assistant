FROM ubuntu:20.04

COPY ./install_hyperon.sh  /app/install_hyperon.sh

#install hyperon
RUN sh /app/install_hyperon.sh "/app"
# after hyperon installation
RUN apt-get update
RUN apt-get install -y curl build-essential git

# clone metta-moto
WORKDIR /app
RUN git clone https://github.com/zarqa-ai/metta-motto.git
#RUN git clone https://github.com/besSveta/metta-motto.git --branch fix_retrieval_agent
ENV PYTHONPATH "${PYTHONPATH}:/app/metta-motto"
ENV METTAMOTOPATH "/app/metta-motto"

# Setup requirements
COPY ./prototyping/metta_llm /app/snet-assistant/prototyping/metta_llm
COPY ./prototyping/assistant_utils /app/snet-assistant/prototyping/assistant_utils

ENV PYTHONPATH "${PYTHONPATH}:/app/snet-assistant"
RUN pip install openai markdown tiktoken bs4 chromadb
ENV OPENAI_API_KEY "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"

WORKDIR /app/snet-assistant
CMD [ "python3", "prototyping/metta_llm/metta_guidance/runner.py"]
#CMD ["/bin/bash"]