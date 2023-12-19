import glob
import os
import shutil
from pathlib import Path
from prototyping.assistant_utils.data_getters.constants import data_dir

dev_portal_url = "https://github.com/singnet/dev-portal.git"

folders_to_load = ["docs", "tutorials"]
class PlatformInformationGetter:
    '''
    stores all md documents from https://github.com/singnet/dev-portal in chroma database
    '''
    def __init__(self):
        self.__original_docs_folder = os.path.join(data_dir, "original_docs")
        self.__md_docs_folder = os.path.join(data_dir, "dev_portal_md_docs")
        if os.path.exists(self.__md_docs_folder):
            files = os.listdir(self.__md_docs_folder)
            need_load_docs = len(files) == 0
        else:
            Path(self.__md_docs_folder).mkdir(parents=True, exist_ok=True)
            need_load_docs = True

        if need_load_docs:
            self.load_docs()

    def _download_md_files(self):
        '''
        load all md files content from https://github.com/singnet/dev-portal
        :return:
        '''
        if not os.path.exists(data_dir):
            raise Exception(f"{data_dir} does not exists")
        dev_portal_path = os.path.join(self.__original_docs_folder, "dev-portal")
        if not os.path.exists(dev_portal_path):
            if not os.path.exists(self.__original_docs_folder):
                os.mkdir(self.__original_docs_folder)
            os.system(f"cd {self.__original_docs_folder}; git clone {dev_portal_url}")
        paths = folders_to_load
        files = []
        for ph in paths:
            g1 = glob.glob(os.path.join(dev_portal_path, ph, "*md"))
            files.extend(list(g1))
            g2 = glob.glob(os.path.join(dev_portal_path, ph, "*", "*md"))
            files.extend(list(g2))
            g3 = glob.glob(os.path.join(dev_portal_path, ph, "*", "*", "*md"))
            files.extend(list(g3))
        assert len(files) > 0
        return files

    def load_docs(self):
        for file in self._download_md_files():
            shutil.move(file, os.path.join(self.__md_docs_folder, Path(file).name))
        shutil.rmtree(self.__original_docs_folder)

    # def _combine_documents(self, docs, document_separator="\n\n"):
    #     doc_strings =  [format_document(doc, self.doc_prompt) for doc in docs]
    #     return document_separator.join(doc_strings)

    @property
    def docs_folder(self):
        return self.__md_docs_folder


if __name__ == '__main__':
    getter = PlatformInformationGetter()
    print(getter.docs_folder)
