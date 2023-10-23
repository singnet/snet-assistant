from dotenv import load_dotenv, find_dotenv
from utility import read_json, get_completion
from embed import embed_question
import pandas as pd
import openai
import os

_ = load_dotenv(find_dotenv())  # read local .env file

openai.api_key = os.getenv('OPENAI_API_KEY')

path = ("/home/lewi/Documents/project/snet-assistant-test/prototyping/QnA_Agent/data/summary.json")


def retrieveAnswerDirectory(question: str, path: str = path) -> int:

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


question = """how To get the metamask plugin install?"""
print(retrieveAnswerDirectory(question))
