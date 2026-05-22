from sentence_transformers import CrossEncoder


reranker=None
def initModel():
    global reranker
    # 指定模型下载目录
    print("开始下载rerank模型")
    reranker = CrossEncoder(
        'BAAI/bge-reranker-v2-m3',
        cache_folder='D:\\rerankmodel',  # 自定义缓存目录
        model_kwargs={"torch_dtype": "float16"},
        device='cuda',
        local_files_only=True
    )
    print("rerank模型下载完成")

def rerank_search(chunks,question):
    pairs=[[question,chunk]for chunk in chunks]
    # 3. 计算 Rerank 分数
    rerank_scores = reranker.predict(pairs)

    # 4. 根据 Rerank 分数重新排序，并取最终结果
    #    zip 将文本和分数打包，然后按分数从高到低排序
    ranked_results = sorted(zip(chunks, rerank_scores), key=lambda x: x[1], reverse=True)
    return [chunk for chunk, score in ranked_results[:1]],[score for chunk, score in ranked_results[:5]]
