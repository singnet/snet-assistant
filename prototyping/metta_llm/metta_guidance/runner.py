import os
import hyperon as hp
import pathlib
from motto.agents import DialogAgent

if __name__ == '__main__':
    '''
     use services short descriptions as prompt to get service which solves user's task
    '''
    metta_motto_path = os.environ["METTAMOTOPATH"]
    assistant_dir = str(pathlib.Path(__file__).parent.resolve().parent.parent.parent)

    agent = DialogAgent(path="prototyping/metta_llm/metta_guidance/chat_process.msa",
        include_paths=[metta_motto_path, assistant_dir])
    print("Hello! I am an AI assistant here to help you. How can I assist you today?")

    while True:
        question = input()
        result = agent(f'(user "{question}")').content
        if len(result) > 0:
            print(result[-1])
        else:
            print("Sorry, I'm having trouble answering")


