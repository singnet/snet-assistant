import ast
from utility import get_completion
import os
import pandas as pd

import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())  # read local .env file

openai.api_key = os.getenv('OPENAI_API_KEY')


path_dataset = os.path.join(
    os.getcwd(), "prototyping/QnA_Agent/data/dataset.csv")


def join_text(texts):
    total_text = ""

    for text in texts:
        total_text += " ".join(text)

    return total_text


def summary(total_text, model="gpt-3.5-turbo"):
    prompt = f"""
    Please provide a concise summary of the given text that contains enough information to determine whether a question can be answered by referring to the text or not.\n\ntext:{total_text}\n\nsummary:"""

    messages = [{'role': 'system', 'content': """You excel at extracting information from the given text and summary ."""},
                {'role': 'user', 'content': f"{prompt}"},
                ]

    result = get_completion(messages, model=model)

    return result


def save_summary():
    df = pd.read_csv(path_dataset)
    chuck_text = df['chuck_text']

    text_list = [join_text(ast.literal_eval(list_text))
                 for list_text in chuck_text]
    summary_list = [summary(text, model='gpt-3.5-turbo-16k')
                    for text in text_list]
    df['summary'] = summary_list

    print(df.head())


save_summary()
