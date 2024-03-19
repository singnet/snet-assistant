# run with --env OPENAI_API_KEY=$OPENAI_API_KEY --env GIT_TOKEN=$GIT_TOKEN

FROM trueagi/hyperon:latest
USER root
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
RUN pip install openai markdown tiktoken bs4 chromadb  pysqlite3-binary anthropic

WORKDIR /app/snet-assistant
CMD [ "python3", "prototyping/metta_llm/metta_guidance/runner.py"]
#CMD ["/bin/bash"]
