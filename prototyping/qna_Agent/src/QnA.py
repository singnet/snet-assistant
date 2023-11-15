import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from prototyping.qna_Agent.src.utility import read_json, get_completion, function_call
from prototyping.qna_Agent.src.embed import embed_question
import openai
from openai.embeddings_utils import distances_from_embeddings


# Load environment variables
load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')

# Constants and Configurations
SUMMARY_PATH = "./prototyping/qna_Agent/data/summary.json"
DATASET_PATH = "./prototyping/qna_Agent/data/dataset.csv"
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
    # prompt = f"""Given the provided JSON data and a question, your task is to identify the paragraph that contains the answer. When providing your answer, include only the ID of the paragraph. Do not include any additional information, only the number corresponding to the paragraph.\n\nQuestion{question}\n\nJson:{summary_json}\n\nparagraph ID: """
    prompt = f"""Some choices are given below. It is provided in a numbered list 
    (1 to 9), 
    where each item in the list corresponds to a summary.\n
    ---------------------\n
    {summary_json}
    \n---------------------\n
    Using only the choices above and not prior knowledge, return 
    the choice that is most relevant to the question: '{question}'\n
    Provide choice in the following format: 'ANSWER: <number>' and explain why 
    this summary was selected in relation to the question.\n"""

    messages = [{'role': 'system', 'content': """You excel at following instructions and providing the correct answers."""},
                {'role': 'user', 'content': f"{prompt}"}]

    # result = get_completion(messages=messages, model="gpt-3.5-turbo")

    result = function_call(messages=messages, model="gpt-3.5-turbo")
    if int(result) not in range(10):
        return -1
    else:
        return int(result-1)


def get_context(dataset,  question: str):
    """
    Get context information for a given question.

    Args:
        dataset (pd.DataFrame): The dataset.
        question (str): The question.

    Returns:
        str: The context information.
    """
    result_frame = pd.DataFrame()
    size = dataset.shape[0]
    for context_id in range(size):
        #context_id = 7
        path = dataset['path'][context_id]
        context = eval(dataset['chuck_text'][context_id])
        flat_context = [item for sublist in context for item in sublist]

        result = pd.DataFrame({'text': flat_context})
        context_embed = np.load(EMBED_PATH, allow_pickle=True)[context_id]
        question_embed = embed_question(question)
        result['distances'] = distances_from_embeddings(
            question_embed, context_embed, distance_metric='cosine') if question_embed is not None else 100
        result_frame = result_frame.append(result, ignore_index=True)
        #break
    temp = []
    result_frame.drop_duplicates(['text'], inplace=True)
    result_frame.sort_values('distances', ascending=True, inplace=True)
    for text in (result_frame[:7])["text"]:
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
    # relevant_id = retrieve_answer_directory(question) - 1
    #
    # if relevant_id == -1:
    #     return "Error: No relevant folder found to answer the given question."

    context = get_context(dataset=df,  question=question)

    prompt = f"""Context information is below.\n
    ---------------------\n
    {context}\n
    ---------------------\n
    Given only the context information and not prior knowledge, 
    answer the query.\n
    Query: {question}\n
    Answer: """

    messages = [{'role': 'system', 'content': """You excel at following instructions and providing the correct answers."""},
                {'role': 'user', 'content': f"{prompt}"}]

    response = get_completion(messages=messages, model="gpt-3.5-turbo", temperature=0)

    return response
