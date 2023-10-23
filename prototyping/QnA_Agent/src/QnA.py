from dotenv import load_dotenv, find_dotenv
from utility import read_json, get_completion
from embed import embed_question
from openai.embeddings_utils import distances_from_embeddings
import pandas as pd
import openai
import os
import numpy as np
import ast

_ = load_dotenv(find_dotenv())  # read local .env file

openai.api_key = os.getenv('OPENAI_API_KEY')

summary_path = (
    "/home/lewi/Documents/project/snet-assistant-test/prototyping/QnA_Agent/data/summary.json")
dataset_path = ("prototyping/QnA_Agent/data/dataset_with_summary.csv")
embed_path = (
    "/home/lewi/Documents/project/snet-assistant-test/prototyping/QnA_Agent/data/embed.npy")


def retrieveAnswerDirectory(question: str, path: str = summary_path) -> int:

    summary_json = (read_json(path))

    prompt = f"""Given the JSON data and question, identify the paragraph that provides the answer. Please ensure that you only provide the paragraph's ID.\n\nQuestion{question}\n\nJson:{summary_json}"""

    messages = [{'role': 'system', 'content': """You excel at following instructions and providing the correct answers."""},
                {'role': 'user', 'content': f"{prompt}"},
                ]

    result = get_completion(messages=messages, model="gpt-3.5-turbo")
    if int(result) not in range(10):
        return -1
    else:
        return int(result)


def get_context(dataset, id: int, question: str):
    context = eval(dataset['chuck_text'][id])
    flat_context = [item for sublist in context for item in sublist]

    result = pd.DataFrame({'text': flat_context})
    context_embed = np.load(
        '/home/lewi/Documents/project/snet-assistant-test/prototyping/QnA_Agent/data/embed.npy', allow_pickle=True)[id]
    question_embed = embed_question(question)
    # Get the distances from the embeddings

    result['distances'] = (distances_from_embeddings(
        question_embed, context_embed, distance_metric='cosine'))

    temp = []

    for text in (result.sort_values('distances', ascending=True)[:5])["text"]:
        temp.append(text)

    # # Return the context
    # return "\n\n###\n\n".join(temp)
    return (" ".join(temp))


def respondToContext(question: str):

    df = pd.read_csv(dataset_path)
    get_relevant_id = retrieveAnswerDirectory(question) - 1
    if get_relevant_id == -1:
        return (("error there is not relevant folder to answer the given questions"))

    context = get_context(
        dataset=df, id=get_relevant_id, question=question)

    print(context)

    prompt_2 = f"""Context information is below.\n
    ---------------------\n
    {context}\n
    ---------------------\n
    Given the context information and not prior knowledge, 
    answer the query.\n
    Query: {question}\n
    Answer: """

    messages = [{'role': 'system', 'content': """You excel at following instructions and providing the correct answers."""},
                {'role': 'user', 'content': f"{prompt_2}"},
                ]

    response = get_completion(messages=messages, model="gpt-3.5-turbo")

    return response


question = """how To get the metamask plugin install?"""
# id = (retrieveAnswerDirectory(question))
print(respondToContext(question))
