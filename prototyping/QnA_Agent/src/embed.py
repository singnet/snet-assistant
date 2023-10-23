import os
import openai
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import time
import numpy as np

# Load your API key from an environment variable or secret management service
load_dotenv(find_dotenv())
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# OpenAI's best embeddings model as of Oct 2023
EMBEDDING_MODEL = "text-embedding-ada-002"


def embed_context(context_list: list):
    """
    Embed a list of contexts using OpenAI's embedding model.

    Args:
        context_list (list): List of contexts.

    Returns:
        np.array: Array of embeddings.
    """
    embeddings = []
    for batch in context_list:
        flattened = [item for sublist in batch for item in sublist if sublist]

        try:
            response = openai.Embedding.create(
                model=EMBEDDING_MODEL,
                input=flattened
            )
            batch_embeddings = [data["embedding"] for data in response["data"]]
            embeddings.append(batch_embeddings)
        except Exception as e:
            print(f"An error occurred: {e}")

        time.sleep(10)  # Add comment explaining the sleep time

    return np.array(embeddings)


def embed_question(question: str):
    """
    Embed a question using OpenAI's embedding model.

    Args:
        question (str): The question.

    Returns:
        np.array: Embedding of the question.
    """
    try:
        response = openai.Embedding.create(
            model=EMBEDDING_MODEL,
            input=question
        )
        return np.array(response.data[0].embedding)
    except Exception as e:
        print(f"An error occurred: {e}")
