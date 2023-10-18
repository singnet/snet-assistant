import json
import os

from copy import deepcopy

from prototyping.service_find.llm_tests.prompt_generator_helper import PromptGeneratorHelper
from prototyping.service_find.llm_tests.gpt_caller import OpenAIChatCaller, Message, MessageType



class ServiceAdviser:
    def __init__(self, descriptions):
        self.descriptions = descriptions
        self.caller = OpenAIChatCaller()
        descriptions_str = str(descriptions)
        self.caller.history.add_history(
            Message(MessageType.SYSTEM, f'There are next services in snet platform: {descriptions_str}'))

    def get_services(self, sentence):
        result = self.caller.get_response(sentence)
        return result

def get_user_tasks(filename):
    json_file_path = os.path.join(filename)
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    return data


if __name__ == '__main__':
    dir_path = "../../../json"
    gen_helper = PromptGeneratorHelper(dir_path)
    descriptions = gen_helper.get_short_descriptions()
    user_tasks = get_user_tasks("which_service_db.json")
    adviser = ServiceAdviser(descriptions)
    # with open("descriptions_prompt.txt", "w") as f:
    #     f.writelines(str(descriptions))
    history = deepcopy(adviser.caller.history)
    for task in user_tasks:
        result = adviser.get_services(task['question'])
        task.update({'llm_answer': result})
        # will not work for all examples, the prompt is to long,  so I clear history
        adviser.caller.history = deepcopy(history)
    json_data = json.dumps(user_tasks, indent=2)
    with open("which_service_db_results.json", 'w') as f:
        f.write(json_data)
    print(user_tasks[:3])
 