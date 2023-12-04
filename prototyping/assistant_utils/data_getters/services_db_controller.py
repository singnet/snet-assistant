import os
import shutil

import chromadb
import numpy as np
import pathlib

from prototyping.assistant_utils.data_processors import OpenAIEmbeddings
from prototyping.assistant_utils.data_getters.constants import data_dir
from prototyping.assistant_utils.data_getters.services_information_getter import ServicesInformationGetter, \
    ServicesInformationGetterCreator
from prototyping.assistant_utils.data_processors import DocProcessor
from prototyping.assistant_utils.data_processors import AbstractEmbeddings

class ServicesDbController:
    '''
    Stores documentation about services in chroma database
    '''

    def __init__(self, embeddings: AbstractEmbeddings, services_information_getter: ServicesInformationGetter):
        self.embeddings_getter = embeddings
        self.services_information_getter = services_information_getter
        db = os.path.join(data_dir, "chroma_db_services")
        self.collection_name = "services_doc_chunks_collection"
        need_load_docs = not os.path.exists(db)

        self.chroma_client = chromadb.PersistentClient(db)

        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name,
                                                                      metadata={"hnsw:space": "cosine"})

        if not need_load_docs:
            if self.collection.count() < 10:
                need_load_docs = True
                shutil.rmtree(db)

        if need_load_docs:
            self._load_docs()

    def _load_docs(self):
        '''
            loads all documents into database
        '''
        services_names = self.services_information_getter.display_names
        i = 1
        for name in services_names:
            documentation = self.services_information_getter.get_service_documentation(name)
            if documentation is not None:
                chunks = DocProcessor.get_text_chunks(documentation)
                if len(chunks) > 0:
                    embeddings = self.embeddings_getter.get_chunks_embeddings(chunks)
                    length = len(embeddings)
                    ids = [f"id{i+j}" for j in range(length)]
                    i += length
                    self.collection.add(embeddings=embeddings, documents=chunks,  metadatas=[{'source': name.lower()}]*length, ids=ids)

    def get_closest_documentation(self, service_name, question, docs_count=5):
        '''
        returns closest (according to embeddings) document for given question about given service.
        '''
        embeddings_values = self.embeddings_getter.get_embeddings(question)
        context = self.collection.query(query_embeddings=[embeddings_values], n_results=docs_count, where={"source": service_name.lower()})
        docs = np.unique(context["documents"][0])
        res = "\n".join(docs)
        return res


if __name__ == '__main__':
    parent_dir = pathlib.Path(__file__).parent.resolve().parent.parent.parent
    json_dir = f"{parent_dir}/json"
    getter = ServicesInformationGetterCreator.create("json", json_dir)
    defaulf_embeddings = OpenAIEmbeddings()
    controller = ServicesDbController(defaulf_embeddings ,getter)
    text = controller.get_closest_documentation("Image Segmentation", "How to setup Semantic Segmentation service")
    print(text)



