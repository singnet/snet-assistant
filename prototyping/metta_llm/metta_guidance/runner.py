import os
import sys

import hyperon as hp

def run_script(path, metta):
    with open(path, "r") as f:
        script = f.read()
    print(metta.run(script))

if __name__ == '__main__':
    '''
     use services short descriptions as prompt to get service which solves user's task
    '''
    metta_motto_path = os.environ["METTAMOTOPATH"]


    env_builder = hp.Environment.custom_env(include_paths=[metta_motto_path])
    metta = hp.MeTTa(env_builder=env_builder)
    run_script("prototyping/metta_llm/metta_dialogue_agent/test_llm_agent.metta", metta)


