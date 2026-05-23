from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate



class LangchainChat:
    def __init__(self, retriever):
        load_dotenv()
        self.llm = ChatOllama(model=os.environ.get("llm_model"))
        self.prompt = ChatPromptTemplate.from_template("""
                         请根据以下资料回答用户的问题。回答要简洁自然，像正常对话一样。
                         历史对话：
                         {history}

                         资料：
                         {context}

                         用户问题：{input}
                         """)
        self.chater = create_retrieval_chain(
            retriever,
            create_stuff_documents_chain(self.llm, self.prompt)
        )

    # 一次性返回方法
    def invoke(self, input_data):
        return self.chater.invoke(input_data)

    # 流式返回方法
    def streamInvoke(self, input_data,user: dict):
        from application.service.chat_message import create_chat_message, get_chat_messagestr
        messagestr=get_chat_messagestr(input_data.session_id)
        # 保存用户消息
        create_chat_message(input_data.session_id,"user",input_data.question)
        chunkStrs=''
        for chunk in self.chater.stream({"input": input_data.question,
                                         "history":messagestr}):
            chunkStr=chunk.get("answer", "")
            chunkStrs+=chunkStr
            yield chunkStr
        # 保存模型回答
        create_chat_message(input_data.session_id,"assistant",chunkStrs)

