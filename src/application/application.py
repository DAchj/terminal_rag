from application.chromadb import initDB, initData,del_collection
from application.ollama_chat import chat
from application.rerank import initModel


def main():
   initModel()
   initDB()
   del_collection()
   initData()
   chat()


