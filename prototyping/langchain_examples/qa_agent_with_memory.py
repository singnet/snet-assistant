import os
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationTokenBufferMemory, ConversationBufferMemory, ConversationSummaryMemory
from langchain.chains import ConversationalRetrievalChain
import logging
from get_retriever import get_retriever

logging.basicConfig(level=logging.DEBUG)

data_dir = os.path.dirname(os.path.realpath(__file__))
ret = get_retriever(data_dir)
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, model_kwargs = {"timeout":10} )

#memory = ConversationSummaryMemory(llm=llm,memory_key="chat_history",return_messages=True)
#memory = ConversationTokenBufferMemory(llm=llm, max_token_limit=1000, memory_key="chat_history",return_messages=True)
memory = ConversationBufferMemory(memory_key="chat_history",return_messages=True)

qa = ConversationalRetrievalChain.from_llm(llm, retriever=ret, memory=memory)
print(qa("How to write a client for SingularityNET serice?"))

print("\n\n\n\n\n\n")

print(qa("Which programs language are suported?"))
