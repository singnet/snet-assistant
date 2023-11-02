from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
import logging
import os
import sys

# TEMPORAL IMPORT FOR PROTOTYPE
import_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if import_dir not in sys.path:
    sys.path.append(import_dir)

from assistant_utils import JSONServicesInformationGetter


sf_prompt_template = """You are the SingularityNet AI platform and marketplace assistant.
There is a complete list of services on snet platform with descriptions.
{short_descriptions}

Answer the following user question. Your reply should be very short and have a format [a, b,...], where 'a', 'b' are relevant services.
You can use only services on snet platform. If task cannot be performed by services on snet platform then answer [].
"""


def make_service_find_chain(llm, services_json_path):
    if not os.path.isdir(services_json_path):
        raise Exception(f"Directory {services_json_path} does not exists")

    gen_helper = JSONServicesInformationGetter(services_json_path)
    sf_prompt = ChatPromptTemplate.from_messages([
    ("system", sf_prompt_template),
    ("human", "{question}"),
    ])

    chain = ({"question": RunnablePassthrough(), "short_descriptions": lambda x: str(gen_helper.short_descriptions)}
    | sf_prompt | llm | StrOutputParser())

    return chain

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, model_kwargs = {"timeout":10} )
    chain = make_service_find_chain(llm, "../../json")
    print(chain.invoke("I need to translate my handwritten russian text to english"))
