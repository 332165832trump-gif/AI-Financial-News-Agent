# 06 - Debug 的思维和方法

## 最重要的原则

> **出 bug 不是你的问题，是正常的。不会 debug 才是问题。**

你今天写的每 100 行代码，平均会遇到 2-3 个 bug。这不是因为你不够好——Google 的工程师也一样。区别在于：他们知道怎么快速找到 bug。

## Debug 三步法

### 第一步：定位——"死在哪一行？"

看 Python 的 Traceback（报错信息）：

```
Traceback (most recent call last):
  File "C:\...\main.py", line 8, in <module>        ← 3. 调用链：从 main.py 第8行开始
    from src import news_fetcher                     
  File "C:\...\src\__init__.py", line 1, in <module> ← 2. 然后调用了 __init__.py 第1行
    __init__.py                                      ← 1. 在这里报错
NameError: name '__init__' is not defined           ← 0. 错误类型和原因
```

**从下往上读：**
1. **最后一行** → 错误类型 + 原因：`NameError: name '__init__' is not defined`
2. **倒数第二行** → 具体哪一行代码出错：`File "__init__.py", line 1`
3. **继续往上** → 谁调用了出错的那行：`main.py line 8 → __init__.py line 1`

### 第二步：假设——"变量里到底是什么？"

最常见的问题是"我以为变量是这样的，实际上它是那样的"。

```python
# 不要猜，直接 print 出来看
print(f"变量 articles 的类型: {type(articles)}")
print(f"变量 articles 的长度: {len(articles)}")
print(f"变量 articles[0] 的内容: {articles[0]}")
print(f"变量 articles[0] 的键: {list(articles[0].keys())}")
```

### 第三步：验证——"改一小点，看效果"

不要一次改 10 行。改 1 行，跑一次，确认好了再改下一行。

## 你今天用到的 4 种 Debug 方法

### 方法1：print 调试（最基础、最有效）

```python
# 不是随便 print，而是在"关键节点"埋标记
print("[DEBUG] 读到 API 密钥前10位:", api_key[:10])
print("[DEBUG] 正在向 NewsAPI 发送请求...")
print("[DEBUG] 服务器返回状态码:", response.status_code)
print("[DEBUG] 返回数据的一级键:", list(data.keys()))
print("[DEBUG] 共获取到", data.get("totalResults", 0), "条新闻")
```

如果程序在"发送请求"之后没有输出 → 网络请求卡住了。
如果状态码是 401 → API 密钥有问题。
如果 data.keys() 里没有 "articles" → API 返回格式变了。

### 方法2：type() 看类型

```python
data = response.json()
print(type(data))           # <class 'dict'> ← 不是 str，可以用 ["key"]
print(type(data["articles"]))  # <class 'list'> ← 可以用 for 循环
```

### 方法3：看嵌套结构

```python
# 看顶层有哪些键
print(list(data.keys()))
# ['status', 'totalResults', 'articles']

# 看 articles 第一个元素的内容
print(data["articles"][0])
# {'source': {...}, 'title': '...', ...}
```

### 方法4：try/except 逐层捕获

```python
try:
    response = requests.get(url, params=params)
except Exception as e:
    print(f"网络请求失败: {e}")
    # 这时候你可以检查：是不是网断了？URL 拼错了？

try:
    data = response.json()
except Exception as e:
    print(f"JSON 解析失败: {e}")
    # 这时候你可以检查：response.text 到底是什么？
```

## 今天实际遇到的一个 Bug

### 错误现象

```
NameError: name '__init__' is not defined
```

### 根本原因

`src/__init__.py` 文件的内容被写成了 `__init__.py` 这行文字。Python 把它当成代码执行，`__init__` 不是 Python 关键字，所以报 NameError。

### 如何 Debug

1. 看报错最后一行：`NameError` — 某个名字不存在
2. 看倒数第二行：报错在 `__init__.py` 第 1 行
3. 看 `__init__.py` 的内容：竟然是 `__init__.py` 这几个字
4. 正确的内容应该是空的或者只有注释

### 正确工程写法

```python
# __init__.py 的正确内容：注释或空
# 这个文件让 src 文件夹成为一个 Python 包
```

### 以后如何避免

写完任何 `.py` 文件后，先确认文件内容是 Python 代码（或空），而不是文件名本身。

## Debug 工具箱速查

| 方法 | 代码 | 解决的问题 |
|------|------|-----------|
| 看类型 | `print(type(x))` | "x 是 str 还是 dict？" |
| 看内容 | `print(x)` | "x 里面到底是什么？" |
| 看键 | `print(list(d.keys()))` | "这个 dict 有哪些 key？" |
| 看长度 | `print(len(L))` | "这个 list 里有多少元素？" |
| 看第一个 | `print(L[0])` | "列表第一个元素长什么样？" |
| 看切片 | `print(str[:200])` | "太长的字符串，只看前 200 字符" |
| 安全取值 | `d.get("key", "默认")` | "这个 key 可能存在也可能不存在" |

## 三个 Debug 原则

1. **print 不是随便用，而是在"关键节点"埋标记** — 每完成一个步骤就打印，出问题立刻知道死在哪步
2. **遇到变量先看类型（type）和内容（print/keys/len）** — 不要猜，直接看
3. **读报错从下往上** — 错误类型 → 出错行号 → 调用链
