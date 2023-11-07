from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

import glob
import os
import logging

#logging.basicConfig(level=logging.DEBUG)

def download_md_files(data_dir):
    if not os.path.exists(data_dir):
        raise Exception("{data_dir} does not exists")
    d = os.path.join(data_dir, "original_docs")
    os.mkdir(d)
    os.system(f"cd {d}; git clone https://github.com/singnet/dev-portal.git")
    g1 = glob.glob(os.path.join(d, "dev-portal", "docs","*md"))
    g2 = glob.glob(os.path.join(d, "dev-portal", "docs", "*", "*md"))
    g3 = glob.glob(os.path.join(d, "dev-portal", "docs", "*", "*", "*md"))
    rez = list(g1) + list(g2) + list(g3)
    assert len(rez) > 0
    return rez

def load_split_docs(data_dir):
    docs = []
    for files in download_md_files(data_dir):
        loader = UnstructuredMarkdownLoader(files)
        docs += loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 2000, chunk_overlap = 200)
    splits = text_splitter.split_documents(docs)
    print(len(splits))
    return splits

def get_retriever(data_dir):
    db = os.path.join(data_dir, "chroma_db")
    if os.path.exists(db):
        vs = Chroma(persist_directory=db, embedding_function=OpenAIEmbeddings())
    else:
        splits = load_split_docs(data_dir)
        vs = Chroma.from_documents(documents=splits,embedding=OpenAIEmbeddings(),persist_directory=db )
    return vs.as_retriever(search_kwargs = {'k':4})
