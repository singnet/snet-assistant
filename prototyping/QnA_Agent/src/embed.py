import os
import openai
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import time
import numpy as np

load_dotenv(find_dotenv())

# Load your API key from an environment variable or secret management service
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# OpenAI's best embeddings model as of Oct 2023
EMBEDDING_MODEL = "text-embedding-ada-002"


def embed_context(context_list):
    embeddings = []
    for batch in context_list:
        flattened = [item for sublist in batch for item in sublist if sublist]

        response = openai.Embedding.create(
            model=EMBEDDING_MODEL,
            input=flattened
        )

        batch_embeddings = [data["embedding"] for data in response["data"]]
        embeddings.append(batch_embeddings)

        time.sleep(10)

    return np.array(embeddings)


def embed_question(question):
    response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=question
    )

    return np.array(response.data[0].embedding)
