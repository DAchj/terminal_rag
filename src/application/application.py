from application.chromadb import initDB, initData
from application.ollama_chat import chat


def main():
   initDB()
   initData()
   chat()


