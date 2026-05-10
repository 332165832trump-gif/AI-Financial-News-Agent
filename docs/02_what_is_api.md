# 02 - 什么是 API（用你能听懂的话）

## 这一节你要真正学会什么

这一节不是为了背概念，而是为了让你真正理解项目的第一步：

```text
Python 程序如何从互联网上拿到金融新闻？
```

学完这一节，你要能独立解释并手敲这几行：

```python
response = requests.get(url, params=params)
print(response.status_code)
data = response.json()
articles = data["articles"]
print(articles[0]["title"])
```

如果你能说清楚每个变量里面长什么样，这一节才算真的学会。

---

## 一句话解释

**API 就是“别人开放给你的程序入口”。**

更具体一点：

```text
别人把数据或功能放在服务器上，
你用 Python 通过一个网址去请求，
服务器再把结果返回给你。
```

在这个项目里，新闻不在你的电脑里，而是在 NewsAPI 的服务器里。

所以你的 Python 程序要做的事情是：

```text
向 NewsAPI 服务器发送请求：
“请给我 10 条英文财经新闻。”
```

这就是 API 调用。

---

## 普通网页和 API 的区别

普通网页是给人看的：

```text
你打开网页 → 看新闻标题、图片、正文
```

API 是给程序用的：

```text
Python 访问 API → 拿到结构化数据 → 程序继续处理
```

所以：

```text
普通网页返回 HTML，适合浏览器显示。
API 返回 JSON，适合 Python 处理。
```

---

## 类比：餐厅点餐

```text
你（Python代码）                       餐厅厨房（别人的服务器）
     │                                        │
     │  ① 看菜单（读API文档）                    │
     │  ② 点菜：我要 10 条财经新闻                │
     │     requests.get("https://api.xxx", ...) │
     │  ──────────────────────────────────────→│
     │                                        │ ③ 服务器查数据
     │  ④ 返回结果                              │
     │  ←──────────────────────────────────────│
     │  response.json() = {                    │
     │      "status": "ok",                  │
     │      "articles": [...]                 │
     │  }                                     │
     │                                        │
     │  ⑤ 你的代码继续处理新闻数据                │
```

- **菜单** = API 文档，告诉你能请求什么、参数怎么写
- **点菜** = `requests.get(url, params=params)`
- **上菜** = 服务器返回数据
- **API Key** = 会员卡 / 身份证，证明你有权限调用
- **状态码** = 服务员先告诉你“成功了还是失败了”

---

# 第一部分：NewsAPI 是怎么被调用的

## 1. 准备 API 地址

```python
url = "https://newsapi.org/v2/top-headlines"
```

这个 `url` 是 NewsAPI 给你的入口。

你可以理解为：

```text
我要去哪个柜台点餐？
```

这里的柜台就是：

```text
NewsAPI 的 top-headlines 接口
```

它专门用来获取头条新闻。

---

## 2. 准备请求参数

```python
params = {
    "category": "business",
    "language": "en",
    "pageSize": 10,
    "apiKey": "你的密钥"
}
```

`params` 是一个 Python 字典。

它告诉服务器：

```text
category = business：我要商业/财经类新闻
language = en：我要英文新闻
pageSize = 10：我要 10 条
apiKey = 你的密钥：证明我有权限
```

这个变量里面大概长这样：

```python
{
    "category": "business",
    "language": "en",
    "pageSize": 10,
    "apiKey": "xxxxxxxxxxxxxxxx"
}
```

注意：真实项目里不要把密钥直接写死在代码里，后面会讲 `.env`。

---

## 3. 发请求：requests.get()

```python
response = requests.get(url, params=params)
```

这行代码的意思是：

```text
Python 帮你访问 url，
并且把 params 里的要求一起带给服务器。
```

翻译成人话：

```text
NewsAPI 你好，我要 10 条英文商业新闻，这是我的 API Key。
```

---

## 4. response 是什么

很多新手会误以为：

```python
response = requests.get(...)
```

之后，`response` 就是新闻。

不对。

`response` 不是新闻本身。

它是服务器返回的“完整响应包”，里面包括：

```text
状态码
返回内容
响应头
编码信息
错误信息
```

所以你第一步应该先看状态码：

```python
print(response.status_code)
```

如果输出：

```text
200
```

说明请求成功。

如果输出：

```text
401
```

说明 API Key 错了。

如果输出：

```text
429
```

说明请求太频繁。

---

## 5. 把响应变成 Python 数据：response.json()

服务器返回的数据通常长这样：

```json
{
  "status": "ok",
  "totalResults": 58,
  "articles": [
    {
      "title": "Stock futures are higher...",
      "description": "Markets rose today...",
      "url": "https://..."
    }
  ]
}
```

刚从服务器回来时，它本质上是 JSON 数据。

你写：

```python
data = response.json()
```

意思是：

```text
把服务器返回的 JSON 数据，转换成 Python 能处理的 dict/list。
```

转换之后，`data` 大概是一个 Python 字典：

```python
data = {
    "status": "ok",
    "totalResults": 58,
    "articles": [
        {
            "title": "Stock futures are higher...",
            "description": "Markets rose today...",
            "url": "https://..."
        }
    ]
}
```

这时你就能用 Python 的方式取值。

---

# 第二部分：新闻数据怎么一层层取出来

假设我们已经有：

```python
data = response.json()
```

## 1. 先取新闻列表

```python
articles = data["articles"]
```

这里的意思是：

```text
从 data 这个字典里，取出 articles 这一项。
```

`articles` 是一个列表，大概长这样：

```python
articles = [
    {
        "title": "Stock futures are higher...",
        "description": "Markets rose today...",
        "url": "https://..."
    },
    {
        "title": "Oil prices rise...",
        "description": "Oil moved higher...",
        "url": "https://..."
    }
]
```

---

## 2. 取第一条新闻

```python
first_article = articles[0]
```

注意：Python 列表从 0 开始数。

```text
articles[0] = 第一条新闻
articles[1] = 第二条新闻
articles[2] = 第三条新闻
```

`first_article` 是一个字典，大概长这样：

```python
first_article = {
    "title": "Stock futures are higher...",
    "description": "Markets rose today...",
    "url": "https://..."
}
```

---

## 3. 取第一条新闻标题

```python
title = first_article["title"]
```

也可以连起来写：

```python
title = data["articles"][0]["title"]
```

这条路线要反复记：

```text
data
↓
data["articles"]
↓
data["articles"][0]
↓
data["articles"][0]["title"]
```

对应含义是：

```text
整个返回数据
↓
新闻列表
↓
第一条新闻
↓
第一条新闻标题
```

---

# 第三部分：你必须手敲的最小 Demo

新建一个文件：

```text
lesson_01_api_demo.py
```

写入下面代码：

```python
import requests

# 1. API 地址：我要请求哪个服务器入口？
url = "https://newsapi.org/v2/top-headlines"

# 2. 请求参数：我要什么数据？
params = {
    "category": "business",
    "language": "en",
    "pageSize": 3,
    "apiKey": "这里换成你的 NewsAPI Key"
}

# 3. 发送请求
response = requests.get(url, params=params)

# 4. 先看状态码，判断请求是否成功
print("状态码：", response.status_code)

# 5. 把 JSON 转成 Python dict/list
# 注意：如果状态码不是 200，这里也可能拿到错误信息
# 所以真实项目里通常要先判断 status_code
data = response.json()

# 6. 观察 data 这个变量
print("data 的类型：", type(data))
print("data 里面有哪些 key：", data.keys())

# 7. 取出新闻列表
articles = data["articles"]

print("articles 的类型：", type(articles))
print("articles 的长度：", len(articles))

# 8. 取第一条新闻
first_article = articles[0]

print("第一条新闻的类型：", type(first_article))
print("第一条新闻有哪些 key：", first_article.keys())

# 9. 打印第一条新闻的关键字段
print("第一条新闻标题：", first_article["title"])
print("第一条新闻链接：", first_article["url"])
```

运行：

```bash
python lesson_01_api_demo.py
```

你重点不是看新闻内容，而是观察：

```text
data 是不是 dict？
articles 是不是 list？
articles[0] 是不是 dict？
title 是不是 str？
```

这就是“变量里面到底长什么样”。

---

# 第四部分：API 调试模板

以后你调用任何 API，都可以先套这个模板。

```python
print("状态码：", response.status_code)
print("返回文本前200字符：", response.text[:200])

# 如果返回的是 JSON，再解析
try:
    data = response.json()
except Exception as e:
    print("JSON 解析失败：", e)
    print("服务器原始返回：", response.text[:500])
    raise

print("data 类型：", type(data))

# 如果 data 是 dict，看看它有哪些 key
if isinstance(data, dict):
    print("data keys：", data.keys())

articles = data.get("articles", [])
print("articles 类型：", type(articles))
print("articles 长度：", len(articles))

if len(articles) > 0:
    print("第一条新闻完整内容：", articles[0])
    print("第一条新闻标题：", articles[0].get("title"))
```

这个模板解决的问题是：

```text
我不知道请求有没有成功 → 看 status_code
我不知道服务器返回了什么 → 看 response.text[:200]
我不知道 data 是什么类型 → 看 type(data)
我不知道有哪些字段 → 看 data.keys()
我不知道 articles 有没有内容 → 看 len(articles)
我不知道第一条新闻长什么样 → 打印 articles[0]
```

不要猜变量，直接 print 出来看。

---

# 第五部分：HTTP 状态码速查

| 状态码 | 含义 | 你现在该做什么 |
|--------|------|---------------|
| **200** | 一切正常 | 继续处理数据 |
| **401** | API Key 错误 | 检查 `.env` 里的密钥 |
| **404** | 你要的东西不存在 | 检查网址拼写 |
| **429** | 请求太频繁 | 等一会再试，或者降低运行频率 |
| **500** | 服务器自己出错 | 不是你代码的问题，可以重试 |

基础判断代码：

```python
response = requests.get(url, params=params)

if response.status_code == 200:
    print("成功！")
elif response.status_code == 401:
    print("密钥错误！")
elif response.status_code == 429:
    print("请求太频繁！")
else:
    print(f"其他错误：{response.status_code}")
    print(response.text[:500])
```

---

# 第六部分：为什么 API Key 不能写在代码里

错误做法：

```python
api_key = "053ea94351954b1595f4b1de820f8c1c"
```

问题是：

```text
如果你把代码上传到 GitHub，别人就能看到你的密钥。
别人可以用你的密钥疯狂调用 API。
你的额度可能被用完，甚至产生账单风险。
```

正确做法：把密钥放进 `.env` 文件。

`.env` 文件内容类似：

```text
NEWS_API_KEY=你的NewsAPI密钥
DEEPSEEK_API_KEY=你的DeepSeek密钥
```

Python 读取：

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("NEWS_API_KEY")
```

这里：

```python
load_dotenv()
```

意思是读取 `.env` 文件。

```python
os.getenv("NEWS_API_KEY")
```

意思是从环境变量里拿到 `NEWS_API_KEY` 的值。

`.env` 文件应该放进 `.gitignore`，不要上传到 GitHub。

---

# 第七部分：真实例子：今天用到的 3 个 API

## 1. NewsAPI：获取新闻

```python
url = "https://newsapi.org/v2/top-headlines"

params = {
    "category": "business",
    "language": "en",
    "pageSize": 10,
    "apiKey": api_key
}

response = requests.get(url, params=params)
news_data = response.json()
```

作用：

```text
获取财经新闻。
```

---

## 2. DeepSeek API：AI 分析

```python
from openai import OpenAI

client = OpenAI(
    api_key="你的密钥",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "请分析这条新闻..."}]
)

analysis = response.choices[0].message.content
```

作用：

```text
把新闻标题、摘要和市场数据发给 AI，让 AI 返回分析。
```

这一段后面单独讲，现在你先知道它也是 API 调用。

---

## 3. Yahoo Finance：获取市场行情

```python
import yfinance as yf

ticker = yf.Ticker("^GSPC")
data = ticker.history(period="5d")
latest_price = data["Close"].iloc[-1]
```

作用：

```text
获取标普500等市场行情。
```

这里的 `data` 不是普通 dict，而更像一个表格。后面讲市场数据时再细讲。

---

# 第八部分：常见错误

## 错误 1：忘记导入 requests

错误代码：

```python
response = requests.get(url)
```

报错：

```text
NameError: name 'requests' is not defined
```

原因：

```text
你用了 requests，但没有 import requests。
```

正确写法：

```python
import requests
```

---

## 错误 2：API Key 错误

现象：

```text
状态码：401
```

原因：

```text
apiKey 没传、写错、过期，或者 .env 没有正确读取。
```

debug：

```python
print("状态码：", response.status_code)
print("返回内容：", response.text[:500])
print("API Key 是否读取到：", api_key is not None)
```

不要把完整 API Key 打印到公开地方。

可以只打印前几位：

```python
print("API Key 前6位：", api_key[:6])
```

---

## 错误 3：key 写错

错误代码：

```python
print(data["article"])
```

真实 key 是：

```python
"articles"
```

报错：

```text
KeyError: 'article'
```

debug：

```python
print(data.keys())
```

原则：

```text
不要猜 key，先打印 keys。
```

---

## 错误 4：把 list 当 dict 用

错误代码：

```python
articles = data["articles"]
print(articles["title"])
```

原因：

```text
articles 是 list，不是 dict。
list 要先用 [0] 取出其中一条新闻。
```

正确写法：

```python
print(articles[0]["title"])
```

---

## 错误 5：articles 为空

错误代码：

```python
print(articles[0])
```

如果 `articles` 是空列表：

```python
articles = []
```

会报：

```text
IndexError: list index out of range
```

正确写法：

```python
if len(articles) > 0:
    print(articles[0])
else:
    print("没有新闻")
```

---

# 第九部分：这一节的核心总结

你要记住这条链路：

```text
url + params
    ↓
requests.get(url, params=params)
    ↓
response
    ↓
response.status_code
    ↓
response.json()
    ↓
data
    ↓
data["articles"]
    ↓
articles[0]["title"]
```

一句话总结：

```text
API 不是魔法。
它就是 Python 通过网址向服务器要数据。
服务器返回 JSON。
Python 用 response.json() 把 JSON 变成 dict/list。
然后你用 ["key"] 和 [0] 一层层取数据。
```

---

# 第十部分：本节练习

## 练习 1：打印状态码和顶层 key

目标：确认 API 请求成功，并观察返回数据结构。

```python
print(response.status_code)
print(data.keys())
```

---

## 练习 2：打印前三条新闻标题

```python
for article in articles[:3]:
    print(article["title"])
```

---

## 练习 3：故意写错 key，观察报错

```python
print(data["article"])
```

观察：

```text
KeyError: 'article'
```

然后改成：

```python
print(data.keys())
```

理解为什么应该先看 key。

---

## 练习 4：用 .get() 更安全地取值

```python
for article in articles[:3]:
    title = article.get("title", "无标题")
    url = article.get("url", "无链接")
    print(title)
    print(url)
```

`.get()` 的好处：

```text
如果 key 不存在，不会直接报错，可以给默认值。
```

---

# 和本项目的关系

在 AI Financial News Agent 里：

```text
Observe 阶段的第一步 = 调用 API 获取数据。
```

也就是：

```python
articles = fetch_financial_news()
market_data = fetch_all_market_data()
```

所以这一节不是孤立知识，而是整个 Agent 的地基。

如果你不理解 API、JSON、dict/list，后面的 AI 分析、筛选打分、日报保存都会变成“能跑但看不懂”。
