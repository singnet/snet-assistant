import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from utility import read_json, get_completion
from embed import embed_question
import openai
from openai.embeddings_utils import distances_from_embeddings


# Load environment variables
load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')

# Constants and Configurations
SUMMARY_PATH = "./prototyping/qna_Agent/data/summary.json"
DATASET_PATH = "./prototyping/qna_Agent/data/dataset_with_summary.csv"
EMBED_PATH = "./prototyping/qna_Agent/data/embed.npy"


def retrieve_answer_directory(question: str, path: str = SUMMARY_PATH) -> int:
    """
    Retrieve the relevant answer directory for a given question.

    Args:
        question (str): The question.
        path (str): Path to the summary file.

    Returns:
        int: The relevant directory ID.
    """
    summary_json = read_json(path)
    prompt = f"""Given the JSON data and question, identify the paragraph that provides the answer. Please ensure that you only provide the paragraph's ID.\n\nQuestion{question}\n\nJson:{summary_json}"""

    messages = [{'role': 'system', 'content': """You excel at following instructions and providing the correct answers."""},
                {'role': 'user', 'content': f"{prompt}"}]

    result = get_completion(messages=messages, model="gpt-3.5-turbo")
    if int(result) not in range(10):
        return -1
    else:
        return int(result)


def get_context(dataset, context_id: int, question: str):
    """
    Get context information for a given question.

    Args:
        dataset (pd.DataFrame): The dataset.
        context_id (int): The ID of the relevant context.
        question (str): The question.

    Returns:
        str: The context information.
    """
    context = eval(dataset['chuck_text'][context_id])
    flat_context = [item for sublist in context for item in sublist]

    result = pd.DataFrame({'text': flat_context})
    context_embed = np.load(EMBED_PATH, allow_pickle=True)[context_id]
    question_embed = embed_question(question)

    result['distances'] = distances_from_embeddings(
        question_embed, context_embed, distance_metric='cosine')

    temp = []

    for text in (result.sort_values('distances', ascending=True)[:5])["text"]:
        temp.append(text)

    return " ".join(temp)


def respond_to_context(question: str):
    """
    Respond to a given question with relevant context information.

    Args:
        question (str): The question.

    Returns:
        str: The response.
    """
    df = pd.read_csv(DATASET_PATH)
    relevant_id = retrieve_answer_directory(question) - 1

    if relevant_id == -1:
        return "Error: No relevant folder found to answer the given question."

    context = get_context(
        dataset=df, context_id=relevant_id, question=question)

    prompt_2 = f"""Context information is below.\n
    ---------------------\n
    {context}\n
    ---------------------\n
    Given the context information and not prior knowledge, 
    answer the query.\n
    Query: {question}\n
    Answer: """

    messages = [{'role': 'system', 'content': """You excel at following instructions and providing the correct answers."""},
                {'role': 'user', 'content': f"{prompt_2}"}]

    response = get_completion(messages=messages, model="gpt-3.5-turbo")

    return response
