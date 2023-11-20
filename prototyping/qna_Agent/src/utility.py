import openai
from openai import OpenAI

client = OpenAI()
import json


def get_completion(messages,
                   model,
                   temperature=0,
                   max_tokens=410):
    """Generates a completion for the given messages and model.

    Args:
      messages: A list of messages, where each message is a dictionary with the
        following keys:
          * role: The role of the sender of the message, e.g. "user" or "system".
          * content: The text of the message.
      model: The model to use to generate the completion.
      temperature: The temperature of the model. Higher temperatures result in
        more creative and unpredictable completions.
      max_tokens: The maximum number of tokens to generate.

    Returns:
      A string containing the generated completion.
    """
    response = None
    while response is None:
        try:
            response = client.chat.completions.create(model=model,
            messages=messages,
            temperature=temperature,  # this is the degree of randomness of the model's output
            max_tokens=max_tokens)
        except Exception as e:
            return None
    return response.choices[0].message.content


def function_call(messages, model):
    response = client.chat.completions.create(model=model,
    messages=messages,
    functions=[
        {
            "name": "get_index",
            "description": "Get the paragraph index",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "the index of the paragraph in the json ",
                    },
                },
                "required": ["index"],
            },
        }
    ],
    function_call="auto",
    temperature=0)

    reply_content = response.choices[0].message

    funcs = reply_content.function_call.arguments
    funcs = json.loads(funcs)

    return funcs['index']


def read_json(path: str) -> dict:

    try:
        # Opening JSON file
        with open(path) as f:

            # returns JSON object as
            # a dictionary
            data = json.load(f)
    except Exception as e:
        print(f"error: {e}")
        return {}
    else:
        return data
