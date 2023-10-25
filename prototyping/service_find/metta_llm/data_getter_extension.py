
import pathlib

from hyperon.ext import register_atoms
from hyperon import *
from  assistant_utils import ServicesInformationGetterCreator

class GetterHelper:
    def __init__(self, json_dir):
        self.getter = ServicesInformationGetterCreator.create("json", json_dir)


    def get_service_descriptions(self, prefix):
        descriptions = self.getter.short_descriptions
        return [S(repr(prefix) + " " + str(descriptions))]

    def get_service_names(self, prefix):
        names = self.getter.display_names
        return  [S(str(names))] if len(prefix) == 0 else [S(repr(prefix) + " " + str(names))]



@register_atoms
def data_getters_atoms():
    parent_dir = pathlib.Path(__file__).parent.resolve().parent.parent.parent
    json_dir = f"{parent_dir}/json"
    getter_helper = GetterHelper(json_dir)

    return {
        'get_service_descriptions':
            G(OperationObject('get_service_descriptions', lambda prefix: getter_helper.get_service_descriptions(prefix), unwrap=False)),

        'get_service_names':
            G(OperationObject('get_service_names', lambda prefix: getter_helper.get_service_names(prefix),
                              unwrap=False))
        }



