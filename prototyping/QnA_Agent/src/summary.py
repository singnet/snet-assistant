import ast
from utility import get_completion
import os
import pandas as pd
import tiktoken

import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())  # read local .env file

openai.api_key = os.getenv('OPENAI_API_KEY')
base_dir = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))
data_dir_path = os.path.join(base_dir, "data")


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


def clean_dataset(text):
    return ' '.join(text.split())


summary_sample = """
The text provides an overview of the SingularityNET platform for decentralized AI services. It describes the key components like organizations, services, registry, channels, SDK, CLI, etc. It explains how services are defined using protocol buffers and metadata. It discusses how the daemon and multi-party escrow enable transactions. It describes concepts like on-chain/off-chain transactions, gas costs, wallets, DApp, and the AGIX token. It outlines how to create an organization, add members, publish services, make payments, etc. Overall, the text gives a high-level technical introduction to SingularityNET for publishers and consumers of AI services
"""


def save_summary():

    df = pd.read_csv(path_dataset)
    chuck_text = df['chuck_text']

    ENCODING = tiktoken.encoding_for_model("gpt-3.5-turbo")
    text_list = [join_text(ast.literal_eval(list_text))
                 for list_text in chuck_text]
    clean_test = [clean_dataset(text) for text in text_list]

    summary_list = [summary(text, model='gpt-3.5-turbo-16k') if len(ENCODING.encode(text)) < 16400 else summary_sample
                    for text in clean_test]
    # for index, text in enumerate(text_list):
    #     print(len(ENCODING.encode(text)), len(
    #         ENCODING.encode(clean_test[index])))
    df['summary'] = summary_list
    df.to_csv(os.path.join(data_dir_path, "dataset_with_summary.csv"))
    print(df.head())
    # # print(text_list[6])


save_summary()
