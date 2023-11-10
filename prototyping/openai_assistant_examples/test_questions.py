import pickle
from openai import OpenAI
import time

client = OpenAI()

all_ids = pickle.load( open( "all_ids.p", "rb" ) )

def _get_result(assistant, question):
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=question)
    run = client.beta.threads.runs.create(thread_id=thread.id,assistant_id=assistant.id)

    status = ""
    while status != "completed":
        time.sleep(1)
        status = client.beta.threads.runs.retrieve(thread_id=thread.id,run_id=run.id).status
        if status != "in_progress" and status != "completed":
            print("ERROR:", status)
            return None

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

def get_result(assistant, question):
    rez = None
    while rez == None:
        rez = _get_result(assistant, question)
    return rez

assistant = client.beta.assistants.create(
  instructions="You are a SingularityNet platform support chatbot. Use your knowledge base to best respond to customer queries.",
  model="gpt-3.5-turbo-1106",
  tools=[{"type": "retrieval"}],
  file_ids=all_ids
)

questions = open("questions.txt").readlines()

for q in questions:
    q = q.strip()
    print("---")
    print(q)
    print("\n")
    print("answer:")
    print(get_result(assistant, q))
    print("----\n")

client.beta.assistants.delete(assistant.id)
