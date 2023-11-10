from langchain.chains import LLMMathChain
from langchain.llms import OpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
import logging
from make_qa_chain import make_qa_chain
from make_service_find_chain import make_service_find_chain



llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, request_timeout = 20  )

qa_chain = make_qa_chain(llm)

questions = open("questions.txt").readlines()

for q in questions:
    q = q.strip()
    print("---")
    print(q)
    print("\n")
    print("answer:")
    print(qa_chain.invoke(q))
    print("----\n")
    
