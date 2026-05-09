# 04 - 新闻数据是如何流动的

## 一条新闻的完整旅程

从互联网上的文字，到你的硬盘上的 JSON 文件，一条新闻经历了这些步骤：

```
🌐 互联网（NewsAPI 服务器）
  │
  │ ① HTTP GET 请求
  │    requests.get("https://newsapi.org/v2/top-headlines", params=...)
  │
  ▼
📦 原始 JSON 字符串（纯文本）
  │  "{"status":"ok","articles":[{...},{...}]}"
  │
  │ ② response.json()
  │
  ▼
🐍 Python list（内存中）
  │  articles = [dict1, dict2, dict3, ...]
  │
  │ ③ 遍历 + 传给 AI
  │    for article in articles:
  │        analysis = analyze_single_news(article)
  │
  ▼
🤖 DeepSeek API
  │
  │ ④ AI 返回 JSON 字符串
  │    "{"summary":"...", "sentiment":"bearish", ...}"
  │
  │ ⑤ json.loads() 解析
  │
  ▼
🐍 Python dict（结构化分析结果）
  │  analysis = {"summary": "...", "sentiment": "bearish", ...}
  │
  │ ⑥ 打包 + 保存
  │    with open("data/daily/2026-05-09.json", "w") as f:
  │        json.dump(report, f, ensure_ascii=False, indent=2)
  │
  ▼
💾 硬盘文件（持久化）
     data/daily/2026-05-09.json
     data/briefings/briefing_2026-05-09.json
     data/review/review_2026-05-09.json
```

## 每一步的变量长什么样

### 步骤 ①→②：从字符串到列表

```python
# ① API 返回的原始文本
response.text
# 类型: str
# 内容: '{"status":"ok","totalResults":58,"articles":[{...}]}'
#       ↑ 这是一个很长很长的字符串

# ② 解析后
articles = response.json()["articles"]
# 类型: list
# 内容: [dict1, dict2, dict3, ..., dict10]
#       列表里有 10 个字典，每个字典是一条新闻
```

### 步骤 ③→④：新闻 + 市场数据 → AI Prompt

```python
# 一条新闻
article = {
    "title": "Oil prices rise after US and Iran exchange fire",
    "source": {"name": "BBC News"},
    "description": "...",
    "url": "https://..."
}

# 加上市场行情
market_text = """
【股票】
  标普500指数: 7398.93 (↑0.84%)
  纳斯达克指数: 26247.08 (↑1.71%)
【债券】
  美国10年期国债收益率: 4.36 (↓0.64%)
【商品】
  黄金期货: 4720.40 (↑0.44%)
  原油期货: 95.42 (↑0.64%)
"""

# 拼成一个 Prompt 发给 DeepSeek
prompt = f"""
你是一个专业的金融分析师...
新闻标题：{article['title']}
...
{market_text}
请分析...
"""
```

### 步骤 ④→⑥：AI 回复 → 文件

```python
# ④ AI 返回
raw_text = '{"summary":"美伊冲突推高油价","sentiment":"bearish",...}'
# 类型: str

# ⑤ 解析
analysis = json.loads(raw_text)
# 类型: dict
# analysis 现在可以直接按 key 取值

# ⑥ 打包成报告
report = {
    "date": "2026-05-09",
    "analyses": [
        {
            "title": article["title"],
            "source": article["source"]["name"],
            "analysis": analysis     # ← 把 AI 分析结果嵌套进去
        }
    ]
}

# 写入文件
with open("data/daily/2026-05-09.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
```

## 为什么这样设计数据流？

### 原则1：每一步只做一件事

```
news_fetcher.py    → 只负责"从互联网拿数据"
news_analyzer.py   → 只负责"调用 AI 分析"
report_saver.py    → 只负责"把结果写到硬盘"
agent.py           → 只负责"协调所有步骤"
```

如果所有功能写在一个文件里，出了问题你根本不知道是哪一步炸的。

### 原则2：模块之间通过"返回值"传递数据

```python
# agent.py 的调用链（每个箭头 = 函数返回值）

articles = news_fetcher.fetch_financial_news()   
# ↑ articles 是一个 list of dict

results = news_analyzer.analyze_news_list(articles)
# ↑ results 是一个 list of {"article": dict, "analysis": dict}

report_saver.save_daily_report(results)
# ↑ results 被传入，被保存到文件
```

**模块和模块之间不共享全局变量**，只通过参数和返回值通信。这样每个模块可以独立测试。

### 原则3：数据格式在"传输格式"和"内存格式"之间转换

```
网络/文件          ←→           Python 内存
(str/bytes)                    (dict/list/object)

requests.get()                response.json()
json.load()                   json.loads()
                              json.dumps()
                              json.dump()
```

## 你今天会遇到的变量类型速查

| 变量 | 类型 | 怎么取值 | 出现在 |
|------|------|----------|--------|
| `response` | Response 对象 | `.status_code`, `.json()` | `news_fetcher.py` |
| `articles` | list | `articles[0]`, `for a in articles` | 所有模块 |
| `article` | dict | `article["title"]`, `.get("url")` | 所有模块 |
| `analysis` | dict | `analysis["sentiment"]` | `news_analyzer.py` |
| `results` | list of dict | `results[0]["analysis"]["summary"]` | `agent.py` |
| `report` | dict | `report["analyses"]` | `report_saver.py` |
| `market_data` | list of dict | `market_data[0]["price"]` | `market_data.py` |
