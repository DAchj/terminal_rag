from collections import OrderedDict

from langchain_classic.memory import ConversationBufferWindowMemory


class MemoryManager:
    """短期窗口 + 长期 MySQL 存储"""

    def __init__(self, window_k=2):
        self.window_k = window_k
        self._windows = OrderedDict()  # session_id → ConversationBufferWindowMemory

    def get_window(self, session_id):
        if session_id in self._windows:
            self._windows.move_to_end(session_id)
            return self._windows[session_id]

        memory = ConversationBufferWindowMemory(
            k=self.window_k,
            return_messages=True,
            memory_key="history",
        )
        self._windows[session_id] = memory
        return memory

    def get_context(self, session_id):
        """只返回窗口内的最近消息（不查 MySQL）"""
        memory = self.get_window(session_id)
        return memory.load_memory_variables({})["history"]