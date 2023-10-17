import json
import os
from prototyping.sveta.descriptions_getters.description_getter import ServiceDescriptionGetter
from prototyping.sveta.llm_tests.gpt_caller import OpenAIChatCaller, MessageType, Message
from copy import deepcopy

def get_descriptions():
    dir_path = "../../../json"
    descriptions  = []
    for file_path in os.listdir(dir_path):
        # check if current file_path is a file
        json_file = os.path.join(dir_path, file_path)
        if os.path.isfile(json_file):
            description = ServiceDescriptionGetter.get_description(json_file)
            if description is not None:
                descriptions.append(f"{description.display_name}: {description.short_description}" )
    return descriptions


class ServiceAdviser:
    def __init__(self, descriptions):
        self.descriptions = descriptions
        self.caller = OpenAIChatCaller()
        descriptions_str = "\n".join(descriptions)
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
    descriptions = get_descriptions()
    user_tasks = get_user_tasks("which_service_db.json")
    adviser = ServiceAdviser(descriptions)
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


    #
    #
    #print(result)