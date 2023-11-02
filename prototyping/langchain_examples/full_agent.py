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


system_message = SystemMessage(
content="""You are a helpful agent which helps users with the SingularityNet platform.
By yourself you don't know much information about SingularityNET platform and services which are hosted on the platform but you have two powerful tools:
service_find (to find relevant AI services on the platform) and general_qa (to ask general questions about the platform).
If a user asks you some questions which involve services on the platform please use service_find tool.
If a user asks some general question about the platform or blockchain please use the general_qa tool."""
)


llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, request_timeout = 20  )

qa_chain = make_qa_chain(llm)

service_find_chain = make_service_find_chain(llm, "../../json")

tools = [
    Tool(
        name="general_qa",
        func=qa_chain.invoke,
        description="Useful for when you need to answer general questions about SingularityNET platform",
        return_direct=True,
    ),
    Tool(
        name="service_find",
        func=service_find_chain.invoke,
        description="Useful for when you need to find services on the platform to perform some specific task",
    ),
]


agent_kwargs = {
    "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    "system_message": system_message
}
memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    agent_kwargs=agent_kwargs,
    memory=memory,
)


#logging.basicConfig(level=logging.DEBUG)
agent.run("What is the puropose of SingularityNET platform?")
agent.run("I need to translate my handwritten russian text to english")
