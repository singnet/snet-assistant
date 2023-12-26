FROM ubuntu:22.04

COPY ./install_hyperon.sh  /app/install_hyperon.sh

#install hyperon
RUN sh /app/install_hyperon.sh "/app"
# after hyperon installation
RUN apt-get update
RUN apt-get install -y curl build-essential git

# clone metta-moto
WORKDIR /app
RUN git clone https://github.com/zarqa-ai/metta-motto.git
ENV PYTHONPATH "${PYTHONPATH}:/app/metta-motto"
ENV METTAMOTOPATH "/app/metta-motto"

# copy source code
COPY ./prototyping/metta_llm /app/snet-assistant/prototyping/metta_llm
COPY ./prototyping/assistant_utils /app/snet-assistant/prototyping/assistant_utils

ENV PYTHONPATH "${PYTHONPATH}:/app/snet-assistant"
RUN pip install openai markdown tiktoken bs4 chromadb  pysqlite3-binary
ENV OPENAI_API_KEY "<put your openai key>"

WORKDIR /app/snet-assistant
CMD [ "python3", "prototyping/metta_llm/metta_guidance/runner.py"]
#CMD ["/bin/bash"]
