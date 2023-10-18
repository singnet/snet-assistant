import json
import os

import openai

from prototyping.service_find.descriptions_getters.description_getter import ServiceDescriptionGetter

class PromptGeneratorHelper:
    '''
    load descriptions from json files for all services. also on creates dictionaries with short description,
    full descriptions and documentation.
    '''
    def __init__(self, json_dir):
        self.json_dir = json_dir
        self.__load_descriptions_structures()
        self._short_descriptions = {}
        self._full_descriptions = {}
        self._services_documentation = {}

    def __load_descriptions_structures(self):
        self.services_descriptions = []
        for file_path in os.listdir(self.json_dir):
            # check if current file_path is a file
            json_file = os.path.join(self.json_dir, file_path)
            if os.path.isfile(json_file):
                description = ServiceDescriptionGetter.get_description(json_file)
                if description is not None:
                    self.services_descriptions.append(description)

    def get_short_descriptions(self):
        if len(self._short_descriptions) == 0:
            for description in self.services_descriptions:
                self._short_descriptions[description.display_name] = description.short_description
        return self._short_descriptions

    def get_full_descriptions(self):
        if len(self._full_descriptions) == 0:
            for description in self.services_descriptions:
                self._full_descriptions[description.display_name] = description.description
        return self._full_descriptions

    def get_services_documentation(self):
        if len(self._services_documentation) == 0:
            for description in self.services_descriptions:
                readme_content = ServiceDescriptionGetter.get_readme_text(description.url)
                if readme_content is not None:
                    self._services_documentation[description.display_name] = readme_content
                elif len(description.description) >= len(description.short_description):
                    self._services_documentation[description.display_name] = description.description
                else:
                    self._services_documentation[description.display_name] = description.short_description
        return self._services_documentation

    @staticmethod
    def get_embedding(text, model="text-embedding-ada-002"):
        text = text.replace("\n", " ")
        emd = openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']
        return emd



