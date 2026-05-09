# 今天的学习笔记

> 日期：2026-05-09  
> 项目：AI Financial News Agent  
> 从 0 行代码到完整 Agent（8 个阶段）

---

## 我今天真正学到了什么

### 1. HTTP 请求和 API

**之前**：只知道浏览器输入网址能看到网页。
**现在**：懂了代码怎么向互联网上的服务器"要数据"。

```python
# 这行代码相当于"在浏览器里输入网址并回车"
response = requests.get("https://newsapi.org/v2/top-headlines", params=params)

# 关键理解：
# - response.status_code = 服务器说"200（OK）"还是"401（没权限）"
# - response.text = 服务器返回的原始字符串
# - response.json() = 把那个字符串解析成 Python 能用的 dict/list
```

**变量里到底是什么？**
- `response` 是一个 Response 对象（不是字符串也不是数字，是 requests 库定义的"包裹"）
- `response.text` 是 str（原始 JSON 字符串）
- `response.json()` 返回的是 dict（解析后的数据）

### 2. JSON 和 Python dict/list 的关系

**之前**：以为 JSON 和 Python dict 是同一个东西。
**现在**：懂了它们是"翻译关系"。

```
JSON 字符串                 Python dict
（存在于文件、网络）          （存在于代码变量）

'{"name": "张三"}'    ←→    {"name": "张三"}
      ↑ json.loads() 翻译 →      ↑
      ← json.dumps() 翻译 ←
```

**踩过的坑**：对字符串用 `data["key"]` 会报 `TypeError`。必须先 `json.loads()` 转成 dict。

### 3. 嵌套数据结构取值

API 返回的数据是"俄罗斯套娃"——dict 里面套 list，list 里面套 dict。

```python
# 取第1条新闻的标题
title = data["articles"][0]["title"]
#       dict key→  list索引→  dict key→

# 安全写法（推荐）
title = data.get("articles", [{}])[0].get("title", "无标题")
```

**口诀**：dict 用 `["键"]`，list 用 `[数字]`，交替套。

### 4. API Key 和安全

**之前**：不懂为什么不能把密钥写在代码里。
**现在**：懂了。

```python
# ❌ 如果这样写，上传 GitHub 后全世界都能用你的 API
api_key = "053ea94351..."

# ✅ 正确：放 .env 文件，.gitignore 忽略它
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("NEWS_API_KEY")
```

### 5. 模块化的意义

**之前**：所有代码写在一个文件里，改一行怕炸一片。
**现在**：一个功能一个文件。

```
news_fetcher.py    → 只负责"从互联网拿新闻"
news_analyzer.py   → 只负责"调用 AI 分析"
market_data.py     → 只负责"获取行情数据"
report_saver.py    → 只负责"把结果存到文件"
agent.py           → 只负责"协调所有步骤"
```

出 bug 的时候，看报错文件名就知道该去哪个文件修。

### 6. Agent 的思维模型

**之前**：认为 AI Agent 很玄乎。
**现在**：懂了就是一个循环。

```
👁 Observe   → 获取新闻 + 行情数据
🧠 Think     → 关键词打分（0.0001秒，免费）
🎯 Decide    → 高分=深度分析，低分=跳过
⚡ Act       → 调 AI → 生成简报 → 保存
```

Agent 不是魔法，是 **if/else + for + API 调用** 的合理组合。

### 7. Debug 的系统方法

**之前**：出错了就慌，不知道从哪下手。
**现在**：有三步法——

1. **读报错从下往上**：错误类型 → 出错行号 → 调用链
2. **print 看变量**：`print(type(x))` `print(len(x))` `print(x)`
3. **改一行测一次**：不要一次性改 10 行

### 8. 工程习惯

| 习惯 | 为什么 |
|------|--------|
| 每步都加 `[DEBUG]` print | 出问题立刻知道死在哪一步 |
| 外部调用永远 try/except | API/网络/文件总会出错 |
| 用 `.get()` 而不是 `[]` | 键不存在不报错，返回 None |
| Ctrl+C 要 except 处理 | 优雅退出，不变红字报错 |
| `ensure_ascii=False` | 中文 JSON 不乱码 |
| `encoding='utf-8'` | 读写中文文件必须加 |

### 9. Token 和成本

**之前**：不懂 API 调用的成本。
**现在**：知道每次调 AI 都按 token 计费。

```
DeepSeek: 输入 ¥0.001/千token, 输出 ¥0.002/千token
一条新闻分析 ≈ 600输入 + 250输出 ≈ ¥0.0016
分析 10 条 ≈ ¥0.016（不到 2 分钱！）
```

所以先用关键词免费筛选，再送 AI 分析——这是成本控制的工程思维。

### 10. 数据持久化

终端打印的结果关了窗口就消失了。
写到文件的数据会一直在，可以被搜索、备份、分析。

```python
with open("data/daily/2026-05-09.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
```

---

## 今天遇到的实际错误

### 错误1：`NameError: name '__init__' is not defined`

**原因**：`src/__init__.py` 文件内容写成了 `__init__.py` 这几个字。
**修复**：改成注释 `# 这个文件让 src 变成一个 Python 包`。
**教训**：约定文件的格式是固定的，不能随便写内容。

---

## 今天写的代码量

| 文件 | 行数 | 功能 |
|------|------|------|
| `src/news_fetcher.py` | ~110 | 获取新闻 |
| `src/news_analyzer.py` | ~340 | AI 分析 + JSON 输出 |
| `src/market_data.py` | ~160 | 市场行情数据 |
| `src/report_saver.py` | ~170 | 保存日报 |
| `src/agent.py` | ~450 | Agent 核心 |
| `main.py` | ~55 | 主循环 |
| `review.py` | ~230 | 人工审核 |
| `evaluate.py` | ~190 | 正确率统计 |
| **总计** | **~1700 行** | **从 0 到完整 Agent** |

---

## 我的理解程度自评

| 知识 | 理解程度 | 备注 |
|------|----------|------|
| requests.get() | ★★★★★ | 会用，能解释 |
| JSON / dict / list | ★★★★☆ | 会用，嵌套深了有点晕 |
| API Key / .env | ★★★★★ | 完全理解 |
| Prompt 工程 | ★★★☆☆ | 知道原理，需要多练习 |
| json.loads/dumps | ★★★★☆ | 会用，容易跟 load/dump 搞混 |
| 模块化 | ★★★★★ | 完全理解 |
| Agent 思维 | ★★★★☆ | 概念清晰，需要更多实践 |
| Debug 方法 | ★★★★☆ | 知道三步法，需要积累经验 |
| 异常处理 | ★★★☆☆ | 知道为什么，语法不熟练 |
| 文件读写 | ★★★★☆ | 会用，with open 已形成肌肉记忆 |

---

## 下次要复习的

1. `json.loads` / `json.dumps` / `json.load` / `json.dump` 四个的区别
2. dict 嵌套取值：什么时候用 `["key"]`，什么时候用 `.get()`
3. `try/except` 的语法：`except Exception as e` 和 `except KeyboardInterrupt` 的区别
4. `set()` 的用法：为什么 `analyzed_urls = set()` 能自动去重

---

## 给自己的一句话

> 今天不是学了 1700 行代码，是学了 8 个工程思维。代码可以忘，思维不会。
