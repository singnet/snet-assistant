import glob
import os
import shutil

import numpy as np
from prototyping.assistant_utils.data_getters.constants import data_dir

from prototyping.assistant_utils.data_processors import DocProcessor
import chromadb

dev_portal_url = "https://github.com/singnet/dev-portal.git"


class PlatformInformationGetter:
    def __init__(self, embeddings):
        self.embeddings_getter = embeddings
        self.__original_docs_folder = os.path.join(data_dir, "original_docs")
        db = os.path.join(data_dir, "chroma_db_platform")
        self.collection_name = "doc_chunks_collection"
        need_load_docs = not os.path.exists(db)

        self.chroma_client = chromadb.PersistentClient(db)

        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name,
                                                                      metadata={"hnsw:space": "cosine"})

        if not need_load_docs:
            if self.collection.count() < 10:
                need_load_docs = True
                shutil.rmtree(db)

        if need_load_docs:
            self.load_docs()

    def _download_md_files(self):
        if not os.path.exists(data_dir):
            raise Exception(f"{data_dir} does not exists")
        dev_portal_path = os.path.join(self.__original_docs_folder, "dev-portal")
        if not os.path.exists(dev_portal_path):
            if not os.path.exists(self.__original_docs_folder):
                os.mkdir(self.__original_docs_folder)
            os.system(f"cd {self.__original_docs_folder}; git clone {dev_portal_url}")
        paths = ["docs", "tutorials"]
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
        i = 1
        for file in self._download_md_files():
            text = DocProcessor.clear_text(file)
            chunks = {}
            chunks['texts'] = DocProcessor.get_text_chunks(text)
            chunks['embeddings'] = self.embeddings_getter.get_chunk_embeddings(chunks['texts'])
            length = len(chunks['texts'])
            if length > 0:
                chunks['source'] = [{'source': file}] * length
                ids = [f"id{i + j}" for j in range(length)]
                i += length
                self.collection.add(embeddings=chunks['embeddings'], documents=chunks['texts'],
                                    metadatas=chunks['source'], ids=ids)
        # delete loaded original documents
        shutil.rmtree(self.__original_docs_folder)

    # def _combine_documents(self, docs, document_separator="\n\n"):
    #     doc_strings =  [format_document(doc, self.doc_prompt) for doc in docs]
    #     return document_separator.join(doc_strings)

    def get_context(self, question, docs_count=10):
        embeddings_values = self.embeddings_getter.get_embeddings(question)
        context = self.collection.query(query_embeddings=[embeddings_values], n_results=docs_count)
        # print(context['metadatas'])  # returns a list of the first 10 items in the collection
        # print(self.collection.count())
        docs = np.unique(context["documents"][0])
        res = "\n".join(docs)
        return res
