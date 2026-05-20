import ollama

from application.chromadb import search_by_chromadb

def chat():
    model='qwen2.5:7b'
    print(f"模型{model}加载完毕，可以开始使用了")

    messages=[]
    while (True):
      userinput= input("你： ")

      if userinput == "quit":
          break
      if not userinput:
          continue
      embeddingres=search_by_chromadb(userinput)
      prompt=f"""
      请你基于以下信息回答下边的问题，如果不知道就回答不知道，信息：{chr(10).join(f'- {c}' for c in embeddingres)}，
      问题：{userinput}
      """
      messages.append({"role":"user","content":prompt})
      try:
        print(f"{model}: ",end="",flush=True)
        res= ollama.chat(model=model, messages=messages,stream=True)
        resStr=''
        for re in res:
           content= re["message"]["content"]
           print(content,end="",flush=True)
           resStr+=content
        print("\n")
        messages.append({"role":"assistant","content":resStr})
      except Exception as e:
          print(f"发生异常{e}")
