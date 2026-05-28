
PROMPT_TEMPLATE = (
    "\n请根据以下资料回答用户的问题。回答要简洁自然，像正常对话一样。\n"
    "历史对话：\n"
    "{history}"
    "\n\n资料：\n"
    "{context}"
    "\n\n用户问题：{question}"
)

MAX_CACHED_SESSIONS = 200