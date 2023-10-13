import os
from sveta.descriptions_getters.description_getter import ServiceDescriptionGetter
from sveta.llm_tests.gpt_caller import OpenAIChatCaller, MessageType, Message


def get_descriptions():
    dir_path = "../../json"
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



if __name__ == '__main__':
    key = "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"
    descriptions = get_descriptions()
    sentence = "I have mp3 audio file, which contains some speech in russian language. I would like to get translation of this speech. Do you have service which can help me this this issue?"
    adviser = ServiceAdviser(descriptions)
    result = adviser.get_services(sentence)
    print(result)