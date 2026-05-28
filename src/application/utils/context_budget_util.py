from application.common import constant
from application.exception.business_exception import BusinessException


class ContextBudget:

    def __init__(self, llm, max_context=32768, max_output=2048, safety_buffer=500):
        self.llm = llm
        self.req_context = max_context - max_output - safety_buffer

    def check_and_truncate(self, historystr, docs, question):
       #  没有超直接返回
       if  self.get_total_tokens(historystr=historystr, docs=docs, question=question) >= self.req_context:
        return  historystr, docs

       historys= self.get_lines(historystr= historystr)
       #  优先删除历史
       while  historys and self.get_total_tokens(historystr=self.get_join(historys=historys),docs=docs,question=question) > self.req_context:
           if(len(historys)>=2):
               historys= historys[2:]
           else:
               historys=[]

       historystr = self.get_join(historys=historys)
       if self.get_total_tokens(historystr=historystr, docs=docs, question=question) <= self.req_context:
           return historystr, docs

       docs=list(docs)
       #  仍然超，删除最开始的文档
       while not docs  and self.get_total_tokens(historystr=historystr, docs=docs, question=question) > self.req_context:
           docs.pop()

       if self.get_total_tokens(historystr=historystr, docs=docs, question=question) <= self.req_context:
           return historystr, docs

       # 问题过长，抛出异常
       raise BusinessException(code=1000,message="问题过长，请精简问题后重试",data=None)



    # 获取总token数
    def get_total_tokens(self, historystr, docs, question):
        context_str = "\n".join(d.page_content for d in docs)
        allcontext = constant.PROMPT_TEMPLATE.format(
            history=historystr,
            context=context_str,
            question=question)
        return self.llm.get_num_tokens(allcontext)


    def get_lines(self,historystr):
        if not historystr or not historystr.strip():
            return []
        return historystr.split("\n")


    def get_join(self,historys):
        return  "\n".join(historys)


