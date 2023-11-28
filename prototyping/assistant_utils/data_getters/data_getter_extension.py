import pathlib
from hyperon.ext import register_atoms
from hyperon import *
from prototyping.assistant_utils import ServicesInformationGetterCreator, OpenAIEmbeddings, ServicesDbController
from prototyping.assistant_utils import PlatformInformationGetter


class GetterHelper:
    def __init__(self, json_dir):
        self.getter = ServicesInformationGetterCreator.create("json", json_dir)
        defaulf_embeddings = OpenAIEmbeddings()
        self.platform_info_getter = PlatformInformationGetter(defaulf_embeddings)
        self.service_db_controller = ServicesDbController(defaulf_embeddings, self.getter)

    def get_service_descriptions(self):
        descriptions = self.getter.short_descriptions
        return [S(str(descriptions))]

    def get_service_names(self):
        names = self.getter.display_names
        return [S(str(names))]

    def get_service_prompt(self, text):
        services = ""
        text = repr(text).lower() if not isinstance(text, str) else text.lower()
        for name in self.getter.display_names:
            if (name.lower() in text) and (name not in services):
                services += f"{name};"
        services = services[:-1].split(";") if len(services) > 0 else []

        promt = ""
        for service in services:
            promt += str(self.getter.get_service_full_descriptions(service)) + " "
            promt += str(self.getter.get_service_group_data(service)) + " "
            doc = self.service_db_controller.get_closest_documentation(service, text)
            if doc is not None:
                promt += doc
        return [S(str(promt))]

    def concat_strings(self, str1, str2):
        str1 = repr(str1).replace("\"", "")
        str2 = repr(str2).replace("\"", "")
        return [S(f'"{str1} {str2}"')]

    def is_snet_service(self, service_name):
        name = repr(service_name) if not isinstance(service_name, str) else service_name
        if len(name) > 0 and "(" == name[0] and name[-1] == ")":
            name = name[1:-1]
        result = name.replace('"', '').lower() in [nm.lower() for nm in self.getter.display_names]
        return [ValueAtom(result)]

    def get_service_documentation(self, service_name,  prefix):
        documentation = self.getter.get_service_documentation(service_name)
        prefix = repr(prefix).replace('"', "") if not isinstance(prefix, str) else prefix
        return [S(prefix + " " + str(documentation))]

    def get_question_context(self, question):
        question = repr(question) if not isinstance(question, str) else question
        context = self.platform_info_getter.get_context(question)
        return [S(context)]



@register_atoms
def data_getters_atoms():
    parent_dir = pathlib.Path(__file__).parent.resolve().parent.parent.parent
    json_dir = f"{parent_dir}/json"
    getter_helper = GetterHelper(json_dir)

    return {
        'get_service_descriptions':
            G(OperationObject('get_service_descriptions', getter_helper.get_service_descriptions, unwrap=False)),

        'get_service_names':
            G(OperationObject('get_service_names', getter_helper.get_service_names, unwrap=False)),

        'concat_strings':
            G(OperationObject('concat_strings', lambda str1, str2: getter_helper.concat_strings(str1, str2),
                              unwrap=False)),
        'is_snet_service':
            G(OperationObject('is_snet_service', lambda service: getter_helper.is_snet_service(service),
                              unwrap=False)),
        'get_question_context':
            G(OperationObject('get_question_context', lambda question: getter_helper.get_question_context(question),
                              unwrap=False)),
        'get_service_prompt':
            G(OperationObject('get_service_prompt', lambda question: getter_helper.get_service_prompt(question),
                              unwrap=False)),
    }