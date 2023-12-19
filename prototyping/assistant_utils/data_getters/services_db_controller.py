import os
import pathlib

from prototyping.assistant_utils.data_getters.constants import data_dir
from prototyping.assistant_utils.data_getters.services_information_getter import ServicesInformationGetter, \
    ServicesInformationGetterCreator


class ServicesDbController:
    '''
    Stores documentation about services in chroma database
    '''

    def __init__(self, services_information_getter: ServicesInformationGetter):
        self.services_information_getter = services_information_getter
        self.__docs_folder = os.path.join(data_dir, "services_docs")
        if os.path.exists(self.__docs_folder):
            files = os.listdir(self.__docs_folder)
            need_load_docs = len(files) == 0
        else:
            os.mkdir(self.__docs_folder)
            need_load_docs = True

        if need_load_docs:
            self.load_docs()

    def load_docs(self):
        '''
            loads all documents into database
        '''
        services_names = self.services_information_getter.display_names
        i = 1
        for name in services_names:
            documentation = self.services_information_getter.get_service_documentation(name)
            if documentation is not None:
                # !!! file name is the as service name but in lower case
                with open(os.path.join(self.__docs_folder, f"{name.lower()}.txt"), mode="w") as f:
                    f.write(documentation)

    @property
    def services_docs_folder(self):
        '''
              returns path to file contatining information about service.
        '''
        return self.__docs_folder


if __name__ == '__main__':
    parent_dir = pathlib.Path(__file__).parent.resolve().parent.parent.parent
    json_dir = f"{parent_dir}/json"
    getter = ServicesInformationGetterCreator.create(json_dir)
    controller = ServicesDbController(getter)
    text = controller.services_docs_folder
    print(text)
