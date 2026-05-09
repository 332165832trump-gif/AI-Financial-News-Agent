"""
Demo 2：JSON 和 Python dict/list 的关系
适合 Python 初学者的最小可运行示例

运行：
    python examples/json_demo.py

这个脚本只讲一个核心概念：
  JSON（字符串格式） ←→ Python dict/list（内存对象）
"""

import json

print("=" * 60)
print("JSON 和 Python dict/list 到底是什么关系？")
print("=" * 60)

# ============================================================
# 第1步：一个 JSON 字符串长什么样
# ============================================================
# JSON 本质上就是一个"字符串"，长得像 Python 的 dict
# 但它只是一个文本文件/网络传输的格式，不能直接 .get() 取值

json_string = '''
{
  "name": "张三",
  "age": 25,
  "skills": ["Python", "JavaScript"],
  "address": {
    "city": "北京",
    "street": "长安街"
  }
}
'''

print(f"\n这是一个 JSON 字符串:")
print(json_string)

print(f"\n它的类型: {type(json_string)}")
print("← 是的，它只是一个 str（字符串），不是 dict！")

# 下面这行会报错！因为 json_string 是 str，不能用 []
# print(json_string["name"])  ← 这行会报 TypeError

# ============================================================
# 第2步：把 JSON 字符串 → Python dict（解析）
# ============================================================
print(f"\n{'─'*50}")
print("json.loads()：把字符串变成 Python 对象")
print(f"{'─'*50}")

data = json.loads(json_string)

print(f"\n解析后 data 的类型: {type(data)}")
print("← 现在是 dict 了！可以按 key 取值了！")

# 现在可以取值了：
print(f"\n可以取值了:")
print(f"  data['name']     = {data['name']}")
print(f"  data['age']      = {data['age']}")
print(f"  data['skills']   = {data['skills']}")
print(f"  data['skills'] 的类型: {type(data['skills'])}  ← 这是 list")
print(f"  data['skills'][0] = {data['skills'][0]}")

# 取值的安全方式：用 .get()
print(f"\n安全取值方法 .get():")
print(f"  data.get('name')        = {data.get('name')}")
print(f"  data.get('不存在的key')   = {data.get('不存在的key')}  ← 返回 None，不报错")
print(f"  data.get('不存在的key', '默认') = {data.get('不存在的key', '默认')}")

# ============================================================
# 第3步：Python dict → JSON 字符串（序列化）
# ============================================================
print(f"\n{'─'*50}")
print("json.dumps()：把 Python 对象变成 JSON 字符串")
print(f"{'─'*50}")

python_dict = {
    "股票": "NVDA",
    "价格": 120.5,
    "涨跌幅": 3.2,
    "标签": ["芯片", "AI", "GPU"]
}

# 变成 JSON 字符串（用于保存文件或发送到网络）
output = json.dumps(python_dict, ensure_ascii=False, indent=2)

print(f"\n变成 JSON 字符串后:")
print(output)
print(f"\n类型: {type(output)}  ← 又变回 str 了！")

# ============================================================
# 第4步：四个容易搞混的函数
# ============================================================
print(f"\n{'─'*50}")
print("四兄弟一图记住:")
print(f"{'─'*50}")

print("""
  json.loads(字符串)   →  Python 对象     记法：load  String
  json.dumps(对象)     →  JSON 字符串     记法：dump  String
  json.load(文件对象)  →  Python 对象     记法：load  File
  json.dump(对象, 文件) →  写入文件        记法：dump  to File

  带 s 的 = 操作字符串
  不带 s 的 = 操作文件
""")

# ============================================================
# 第5步：嵌套结构怎么取值
# ============================================================
# 这是实际项目中最常见的操作
# API 返回的数据通常是嵌套的 dict + list
print(f"\n{'─'*50}")
print("实战：嵌套结构取值")
print(f"{'─'*50}")

api_response = {
    "status": "ok",
    "articles": [
        {
            "title": "Nvidia股价创新高",
            "source": {"name": "Bloomberg", "id": "bloomberg"},
            "tags": ["芯片", "AI"]
        },
        {
            "title": "美联储暗示降息",
            "source": {"name": "Reuters", "id": "reuters"},
            "tags": ["利率", "宏观"]
        }
    ]
}

print(f"\nAPI 返回的数据结构:")
print(f"  api_response 是 {type(api_response).__name__}")
print(f"  api_response['articles'] 是 {type(api_response['articles']).__name__}")
print(f"  api_response['articles'][0] 是 {type(api_response['articles'][0]).__name__}")
print(f"  api_response['articles'][0]['source'] 是 {type(api_response['articles'][0]['source']).__name__}")

# 逐层取值
first_article = api_response["articles"][0]
print(f"\n第一篇文章标题: {first_article['title']}")
print(f"第一篇文章来源: {first_article['source']['name']}")
print(f"第一篇文章标签: {first_article['tags']}")

# 遍历所有文章
print(f"\n遍历所有文章:")
for i, article in enumerate(api_response["articles"], start=1):
    title = article.get("title", "无标题")
    source = article.get("source", {}).get("name", "未知")
    print(f"  [{i}] {title}")
    print(f"      来源: {source}")

print(f"\n{'─'*50}")
print("总结：")
print("  JSON = 一种字符串格式（用于传输和存储）")
print("  dict/list = Python 在内存里的数据结构（用于计算）")
print("  json.loads() / json.dumps() = 两者之间的翻译官")
print(f"{'─'*50}")
