import os
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationTokenBufferMemory, ConversationBufferMemory, ConversationSummaryMemory
from langchain.chains import ConversationalRetrievalChain
import logging
from get_retriever import get_retriever
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import format_document



qa_prompt_template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
doc_prompt = PromptTemplate.from_template("{page_content}")

def _combine_documents(docs, document_prompt=doc_prompt, document_separator="\n\n"):
        doc_strings = [format_document(doc, document_prompt) for doc in docs]
        return document_separator.join(doc_strings)

def make_qa_chain(llm):
    data_dir = os.path.dirname(os.path.realpath(__file__))
    retriever = get_retriever(data_dir)

    qa_prompt = ChatPromptTemplate.from_template(qa_prompt_template)

    chain = (
    {"context": retriever | _combine_documents  , "question": RunnablePassthrough()}
    | qa_prompt
    | llm
    | StrOutputParser()
    )
    return chain

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, model_kwargs = {"timeout":10} )
    chain = make_qa_chain(llm)
    print(chain.invoke("Which languages SingularityNET platform has SDK for?"))
