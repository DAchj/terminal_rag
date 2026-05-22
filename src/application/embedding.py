"""
使用全局变量记录向量
"""

import ollama
import numpy as np

model = "bge-m3:latest"

texts = [ # 文档0：Python 排序相关
    "Python 中可以使用 sorted() 函数对列表进行排序，它会返回一个新的排序列表。"
    "同时，列表对象也提供了 sort() 方法，该方法会原地修改列表，不返回新对象。",

    # 文档1：快餐店菜单
    "麦当劳经典套餐：巨无霸汉堡配薯条，再加一杯冰可乐，是最受欢迎的搭配。",

    # 文档2：水果营养价值
    "苹果富含维生素C和膳食纤维，每天吃一个苹果对健康非常有益。俗话说'一天一苹果，医生远离我'。",

    # 文档3：编程语言对比
    "JavaScript 和 Python 都是非常流行的编程语言。JavaScript 主要用于前端开发，"
    "而 Python 在数据科学和人工智能领域更常见。",

    # 文档4：手机产品信息
    "iPhone 15 Pro 配备了 A17 Pro 芯片，采用钛金属边框，"
    "支持 USB-C 接口，摄像头系统有了重大升级。",

    # 文档5：算法教程（真正相关）
    "快速排序（Quicksort）是一种高效的排序算法，"
    "它采用分治策略，通过选择一个'基准'元素，将数组分为两部分，"
    "然后递归地对这两部分进行排序。平均时间复杂度为 O(n log n)。",

    # 文档6：咖啡知识
    "拿铁咖啡由浓缩咖啡和蒸奶组成，表面通常会有一层薄薄的奶泡。"
    "卡布奇诺的奶泡则更厚，口感更绵密。",

    # 文档7：Python 异常处理
    "Python 中使用 try-except 块来捕获和处理异常，"
    "这可以防止程序因为未处理的错误而意外崩溃。",

    # 文档8：篮球新闻
    "湖人队本赛季表现抢眼，詹姆斯场均得分排名联盟前列，"
    "球队有望进入季后赛。",

    # 文档9：排序算法比较（真正相关）
    "冒泡排序是一种简单的排序算法，它重复地遍历要排序的列表，"
    "比较相邻元素并交换顺序错误的元素。时间复杂度为 O(n²)，效率较低。"]

def embeddings():
    res = ollama.embeddings(model=model, prompt="今天天真不错，我要出去钓鱼")
    vector = res["embedding"]
    print(f"向量长度为{len(vector)}")
    print(f"向量的前十个值{vector[:10]}")


vectors = []
def batch_embeddings():
    for text in texts:
        res = ollama.embeddings(model=model, prompt=text)
        vectors.append(res["embedding"])
    print(f"生成了{len(vectors)}个向量")

def search_embeddings(query,top_k=2):
    print("开始检索--------------------------------------")
    print("向量初始化完成----------------------------------")
    queryEmbedding = ollama.embeddings(model=model, prompt=query)["embedding"]
    scores = np.dot(vectors, queryEmbedding) / (
            np.linalg.norm(vectors, axis=1) * np.linalg.norm(queryEmbedding)
    )
    indices = np.argsort(scores)[::-1][:top_k]
    return [texts[i] for i in indices],[scores[i] for i in indices]

