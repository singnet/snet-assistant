import os
import hyperon as hp
import pathlib


def run_script(path, metta):
    with open(path, "r") as f:
        script = f.read()
    print(metta.run(script))

if __name__ == '__main__':
    '''
     use services short descriptions as prompt to get service which solves user's task
    '''
    metta_motto_path = os.environ["METTAMOTOPATH"]
    assistant_dir = str(pathlib.Path(__file__).parent.resolve().parent.parent.parent)

    env_builder = hp.Environment.custom_env(include_paths=[metta_motto_path])
    metta = hp.MeTTa(env_builder=env_builder)
    run_script("prototyping/metta_llm/metta_guidance/test_chat_agent.metta", metta)
    result = (metta.run(f'''!(llm (Agent (chat-gpt "gpt-3.5-turbo-0613"))(Messages (system 
                                      "Introduce yourself if it is the beginning of the conversation, 
                                      and ask the user if he needs your help.")))''', True))
    if len(result) > 0:
        print(result[-1])
    while True:
        question = input()
        result = metta.run(f"!(llm (Agent &chat) (user \"{question}\"))", True)
        if len(result) > 0:
            print(result[-1])
        else:
            print("Sorry, I'm having trouble answering")


