"""
Demo 1：requests.get() 到底干了什么
适合 Python 初学者的最小可运行示例

运行：
    python examples/simple_requests_demo.py

这个脚本只用 20 行代码，让你理解：
  1. requests.get() 是什么
  2. 状态码是什么
  3. response.json() 把什么变成了什么
"""

import requests

# ============================================================
# 第1步：发一个请求
# ============================================================
# requests.get("网址") 相当于你在浏览器里输入网址然后回车
# 浏览器拿到的是"网页"，代码拿到的是"数据"
url = "https://httpbin.org/json"

print("=" * 50)
print("正在请求:", url)
print("=" * 50)

# 这行代码做了：
#   1. 你的电脑向 httpbin.org 的服务器说"请给我 /json 这个页面"
#   2. 服务器收到请求，返回一段数据
#   3. Python 把返回的数据装进 response 这个变量里
response = requests.get(url)

# ============================================================
# 第2步：看状态码
# ============================================================
# 状态码是服务器告诉你的第一句话
# 200 = 一切正常
# 404 = 你要的东西不存在
# 500 = 服务器自己出错了
print(f"\n状态码: {response.status_code}")
print(f"状态码的类型: {type(response.status_code)}  ← 这是一个整数 (int)")

# ============================================================
# 第3步：拿到原始文本
# ============================================================
# response.text 是服务器返回的"原封不动"的字符串
# 浏览器拿到这个字符串后会渲染成网页，但代码不会
raw_text = response.text
print(f"\nresponse.text 的类型: {type(raw_text)}  ← 这是字符串 (str)")
print(f"response.text 的内容 (前100字符):")
print(raw_text[:100])
print("...")

# ============================================================
# 第4步：把 JSON 字符串变成 Python 对象
# ============================================================
# response.json() 是最重要的一行！
# 它把上面那个"字符串"解析成 Python 能直接用的数据结构
data = response.json()

print(f"\nresponse.json() 的类型: {type(data)}  ← 这是字典 (dict) 或列表 (list)")

# 打印 data 里有什么
print(f"\ndata 的内容:")
print(f"  data = {data}")

# 现在可以按 key 取值了！
# 如果 data 是字符串，你不能这样取值
# 但 response.json() 把它变成了 dict，所以可以
print(f"\n按 key 取值示范:")
for key in data:
    value = data[key]
    print(f"  data['{key}'] = {value}")
    print(f"    类型: {type(value).__name__}")

print("\n" + "=" * 50)
print("总结一句话：")
print("  requests.get() 是'去拿数据'")
print("  response.json() 是'把数据变成本 Python 能用的格式'")
print("=" * 50)
