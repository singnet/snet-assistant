import pathlib
from hyperon.ext import register_atoms
from hyperon import *
from prototyping.assistant_utils.data_getters.services_information_getter import ServicesInformationGetterCreator
from prototyping.assistant_utils.data_getters.platform_information_getter import PlatformInformationGetter
from prototyping.assistant_utils.data_getters.constants import data_dir
from prototyping.assistant_utils.data_getters.services_db_controller import ServicesDbController


class GetterHelper:
    def __init__(self, json_dir):
        self.getter = ServicesInformationGetterCreator.create(json_dir)
        self.platform_info_getter = PlatformInformationGetter()
        self.service_db_controller = ServicesDbController(self.getter)
        self.history_length_for_service_name = 5

    def get_service_descriptions(self):
        descriptions = self.getter.short_descriptions
        return [ValueAtom(str(descriptions))]

    def get_service_names(self):
        names = self.getter.display_names
        return [S(str(names))]

    def cut_history_to_str(self, history):
        if isinstance(history, str):
            return history
        if hasattr(history, 'get_children'):
            history =  history.get_children()
            if len(history) > self.history_length_for_service_name:
                history = history[:self.history_length_for_service_name]
            return " ".join(repr(value) for value in history)

    def extract_service_file_name(self, text):
        text = self.cut_history_to_str(text)
        text = repr(text).lower() if not isinstance(text, str) else text.lower()
        found_service = ""
        for name in self.getter.display_names:
            nm = name.lower()
            if (nm in text) and len(nm) > len(found_service):
                found_service = nm
        return [ValueAtom(f"{found_service}.txt")] if len(found_service) > 0 else [ValueAtom(None)]

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

    def get_service_docs_folder(self):
        folder = self.service_db_controller.services_docs_folder
        return [ValueAtom(folder)]

    def get_platform_docs_folder(self):
        folder = self.platform_info_getter.docs_folder
        return [ValueAtom(folder)]

    def get_data_dir(self):
        return [ValueAtom(data_dir)]


@register_atoms
def data_getters_atoms():
    parent_dir = pathlib.Path(__file__).parent.resolve().parent.parent.parent
    json_dir = f"{parent_dir}/json"
    getter_helper = GetterHelper(json_dir)

    return {
        'get-service-descriptions':
            G(OperationObject('get-service-descriptions', getter_helper.get_service_descriptions, unwrap=False)),

        'get-service-names':
            G(OperationObject('get-service-names', getter_helper.get_service_names, unwrap=False)),

        'concat-strings':
            G(OperationObject('concat-strings', lambda str1, str2: getter_helper.concat_strings(str1, str2),
                              unwrap=False)),
        'is-snet-service':
            G(OperationObject('is-snet-service', lambda service: getter_helper.is_snet_service(service),
                              unwrap=False)),
        'get-platform-docs-folder':
            G(OperationObject('get-platform-docs-folder',  getter_helper.get_platform_docs_folder, unwrap=False)),

        'get-service-docs-folder':
            G(OperationObject('get-service-docs-folder', getter_helper.get_service_docs_folder, unwrap=False)),
        'get-data-dir':
            G(OperationObject('get-data-dir', getter_helper.get_data_dir, unwrap=False)),

        'extract-service-file-name':
            G(OperationObject('extract-service-file-name', lambda question: getter_helper.extract_service_file_name(
                question),
                              unwrap=False)),
    }
