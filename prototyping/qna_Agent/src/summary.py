import ast
from prototyping.qna_Agent.src.utility import get_completion
import os
import pandas as pd
import tiktoken
import json
import openai
from dotenv import load_dotenv, find_dotenv

# Load environment variables
_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define paths
base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir_path = os.path.join(base_dir, "data")
path_dataset = os.path.join(data_dir_path, "dataset.csv")


def join_text(texts):
    """Concatenate a list of texts into a single string."""
    total_text = ""

    for text in texts:
        total_text += " ".join(text)

    return total_text


def summary(total_text, model="gpt-3.5-turbo"):
    """Generate a summary for the given text."""
    # prompt = f"""
    # Please provide a concise summary of the given text that contains enough information to determine whether a question can be answered by referring to the text or not.\n\ntext:{total_text}\n\nsummary:"""

    prompt = f"""Write a summary of the following. Try to use only the 
    information provided. 
    Try to include as many key details as possible.\n
    \n
    \n
    {total_text}\n
    \n
    \n
    SUMMARY:\n"""

    messages = [{'role': 'system', 'content': """You excel at extracting information from the given text and summary ."""},
                {'role': 'user', 'content': f"{prompt}"},
                ]

    result = get_completion(messages, model=model)

    return result


def clean_dataset(text):
    """Clean up a text."""
    return ' '.join(text.split())


def save_summary():
    """Load dataset, generate summaries, and save to a JSON file."""
    df = pd.read_csv(path_dataset)
    chuck_text = df['chuck_text']

    ENCODING = tiktoken.encoding_for_model("gpt-3.5-turbo")
    text_list = [join_text(ast.literal_eval(list_text))
                 for list_text in chuck_text]
    clean_test = [clean_dataset(text) for text in text_list]

    summary_sample = """The text provides an overview of the SingularityNET platform for decentralized AI services. It describes the key components like organizations, services, registry, channels, SDK, CLI, etc. It explains how services are defined using protocol buffers and metadata. It discusses how the daemon and multi-party escrow enable transactions. It describes concepts like on-chain/off-chain transactions, gas costs, wallets, DApp, and the AGIX token. It outlines how to create an organization, add members, publish services, make payments, etc. Overall, the text gives a high-level technical introduction to SingularityNET for publishers and consumers of AI services
"""
    summary_list = [summary(text, model='gpt-3.5-turbo-16k') if len(ENCODING.encode(text)) < 16400 else summary_sample
                    for text in clean_test]
    summary_dict = summary_dict = [{"id": index+1, "text": text}
                                   for index, text in enumerate(summary_list)]
    with open(os.path.join(data_dir_path, "summary.json"), 'w') as file:
        json.dump(summary_dict, file, indent=4)
