import time

from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage, get_buffer_string
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from rich import prompt

from application.config.llm_model import load_model
from application.config.memory_manager import MemoryManager


class FinishReasonHandler(BaseCallbackHandler):
    """捕获 LLM 的 finish_reason"""

    def __init__(self):
        self.finish_reason = "stop"

    def on_llm_end(self, response, **kwargs):
        """LLM 完成时触发"""
        try:
            # response.generations[0][0] 是第一条生成结果
            print("----------------------进入回答回调------------------------")
            gen = response.generations[0][0]
            if gen.generation_info:
                self.finish_reason = gen.generation_info.get("finish_reason", "stop")
        except Exception:
            pass


class LangchainChat:
    def __init__(self, retriever):
        load_dotenv()
        # self.llm = ChatOllama(model=os.environ.get("llm_model"))
        self.llm = load_model()
        # self.prompt = ChatPromptTemplate.from_template("""
        #                  请根据以下资料回答用户的问题。回答要简洁自然，像正常对话一样。
        #                  历史对话：
        #                  {history}
        #
        #                  资料：
        #                  {context}
        #
        #                  用户问题：{input}
        #                  """)
        self.retriever = retriever
        self.memoryger = MemoryManager()
        # self.chater = create_retrieval_chain(
        #     retriever,
        #     create_stuff_documents_chain(self.llm, self.prompt)
        # )

    # 一次性返回方法
    def invoke(self, input_data):
        if "history" not in input_data:
            input_data["history"] = ""
        return self.chater.invoke(input_data)

    # 流式返回方法
    def streamInvoke(self, input_data, user: dict):
        from application.service.chat_message import create_chat_message
        history_messages = self.memoryger.get_context(session_id=input_data.session_id)
        print(f"----------消息数量{len(history_messages)}---------")
        if input_data.question == "继续":
            yield from self.keepChat(input_data, history_messages)
            return
        # 获取文档
        docs = self.retriever.invoke({"input": input_data.question})

        # 获取之前对话摘要
        from application.bean_context import chromadb
        longMemoryter = chromadb.get_long_memory_retrieve(10, filter={"session_id": input_data.session_id})
        # # ====== ChromaDB 日志包装 ======
        # _chroma_invoke = longMemoryter.invoke
        #
        # def _log_chroma(query):
        #     q = query["input"] if isinstance(query, dict) else query
        #     docs = _chroma_invoke(q)
        #     print(f"\n===== ChromaDB 长期记忆 原始检索（{len(docs)} 条）=====")
        #     for i, d in enumerate(docs):
        #         print(f"  [{i + 1}] {d.page_content[:120]}")
        #     return docs
        #
        # baseRetriever = RunnableLambda(_log_chroma)

        longMemorys=longMemoryter.invoke(input_data.question)

        # 保存用户消息
        create_chat_message(input_data.session_id, "user", input_data.question)
        self.memoryger.get_window(session_id=input_data.session_id).chat_memory.add_user_message(input_data.question)
        handler = FinishReasonHandler()
        chunkStrs = ''
        prompt=f"""
                         请根据以下资料回答用户的问题。回答要简洁自然，像正常对话一样。
                         历史对话摘要：
                         {longMemorys}
                         
                         最近通话记录：
                         {get_buffer_string(history_messages)}
                         
                         资料：
                         {docs}

                         用户问题：{input_data.question}
                         """
        start = time.perf_counter()

        for chunk in self.llm.stream([HumanMessage(content=prompt)],
                                        config={"callbacks": [handler]}, ):
            chunkStr = chunk.content
            print(chunkStr + "----------------------")
            chunkStrs += chunkStr
            yield chunkStr
        end = time.perf_counter()
        print(f"执行耗时: {end - start:.4f} 秒")
        if handler.finish_reason == "length":
            print("==== 截断了 =====")  # 加一行
            yield "\n__TRUNCATED__"
        else:
            print(f"==== finish_reason = {handler.finish_reason} =====")  # 加一行

        # 保存模型回答
        create_chat_message(input_data.session_id, "assistant", chunkStrs)
        self.memoryger.get_window(session_id=input_data.session_id).chat_memory.add_ai_message(chunkStrs)
        import threading
        threading.Thread(
            target=self.generateSummary,
            args=(input_data.question, chunkStrs, input_data.session_id),
            daemon=True,
        ).start()

    def keepChat(self, input_data=None, messagess=None):
        from application.service.chat_message import create_chat_message
        messagestr = get_buffer_string(messagess)

        prompt = f"以下是未完成的内容，请直接从断点处继续往下写，不要重复已有内容：\n{messagestr}"
        print(f"prompt为{prompt}")
        create_chat_message(input_data.session_id, "user", "继续")
        self.memoryger.get_window(session_id=input_data.session_id).chat_memory.add_user_message(input_data.question)
        handler = FinishReasonHandler()
        chunkStrs = ''
        for chunk in self.llm.stream([HumanMessage(content=prompt)],
                                     config={"callbacks": [handler]}):
            chunkStr = chunk.content
            chunkStrs += chunkStr
            yield chunkStr
        if handler.finish_reason == "length":
            yield "\n__TRUNCATED__"
        create_chat_message(input_data.session_id, "assistant", chunkStrs)
        self.memoryger.get_window(session_id=input_data.session_id).chat_memory.add_ai_message(chunkStrs)
        return



    def generateSummary(self, user_msg, ai_msg, session_id):
        prompt = f"""请总结以下对话的核心语义。

对话内容：
用户：{user_msg}
AI：{ai_msg}

总结规则：
1. 保留：任务目标、问题描述、解决方案、重要约束
2. 忽略：礼貌用语、重复内容、确认性回复
3. 如果没有任何实质性内容，返回：NONE

示例1：
用户：你好，我想查询一下订单123456的物流信息
AI：好的，您的订单已发货，目前在上海中转站，预计明天送达
总结：查询订单123456物流，已发货在上海中转站，预计明天送达

示例2：
用户：谢谢
AI：不客气，还有其他问题吗？
总结：NONE

现在请总结：
总结：""""""请总结以下对话的核心语义。

对话内容：
用户：{user_msg}
AI：{ai_msg}

总结规则：
1. 保留：任务目标、问题描述、解决方案、重要约束
2. 忽略：礼貌用语、重复内容、确认性回复
3. 如果没有任何实质性内容，返回：NONE

示例1：
用户：你好，我想查询一下订单123456的物流信息
AI：好的，您的订单已发货，目前在上海中转站，预计明天送达
总结：查询订单123456物流，已发货在上海中转站，预计明天送达

示例2：
用户：谢谢
AI：不客气，还有其他问题吗？
总结：NONE

现在请总结：
总结："""
        print(prompt)
        response = self.llm.invoke([HumanMessage(content=prompt)])
        print(response)
        from application.bean_context import chromadb
        memory = response.content.strip()
        print(memory)
        print("摘要生成内容为---------------------" + memory)
        if "NONE" not in  memory:
            chromadb.write_long_memory(texts=[memory], metadata_list=[{"session_id": session_id}])


