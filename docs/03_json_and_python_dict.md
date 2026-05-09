# 03 - JSON 和 Python dict/list 的关系

## 核心关系

```
JSON（字符串）          ←→          Python dict/list（内存对象）
  存在于：                           存在于：
  - API 返回的文本                   - 你的代码变量里
  - .json 文件                       - 程序运行时的内存
  - 网络传输的数据                    - 可以被 .get() 取值
  - 不能直接用 .get()                - 可以被 for 循环遍历
```

**`json.loads()` 和 `json.dumps()` 就是两者之间的翻译官。**

## 先搞清楚两个基础数据结构

### dict（字典）：`{}`

```python
# dict 用花括号 {}，里面是 "键": 值
person = {
    "name": "张三",      # "name" 是键（key），"张三" 是值（value）
    "age": 25,           # "age" 是键，25 是值
    "city": "北京"
}

# 取值方法1：用方括号（键不存在会报错）
name = person["name"]        # "张三"

# 取值方法2：用 .get()（键不存在返回 None，不报错）
phone = person.get("phone")           # None（因为不存在）
phone = person.get("phone", "无")     # "无"（指定默认值）
```

### list（列表）：`[]`

```python
# list 用方括号 []，里面是元素
fruits = ["苹果", "香蕉", "橘子"]

# 用数字索引取值（从 0 开始！）
first = fruits[0]    # "苹果"（不是"香蕉"！）
second = fruits[1]   # "香蕉"
third = fruits[2]    # "橘子"

# 遍历列表
for fruit in fruits:
    print(fruit)
```

## JSON 字符串长什么样子？

```json
{
  "status": "ok",
  "totalResults": 58,
  "articles": [
    {
      "source": {"id": null, "name": "Bloomberg"},
      "author": "John Doe",
      "title": "Stock Market Rises",
      "description": "The stock market rose today..."
    },
    {
      "source": {"id": null, "name": "CNBC"},
      "title": "Fed Hints at Rate Cut",
      "description": "The Federal Reserve signaled..."
    }
  ]
}
```

注意：**这看起来像 Python 代码，但它实际上只是一个字符串。** 你看到的花括号、引号、冒号……全都是字符串的一部分。

## 怎么把 JSON 字符串变成 Python 能用的对象？

```python
import json

# 假设 response.text 是 API 返回的 JSON 字符串
json_string = '{"status": "ok", "totalResults": 58}'

# json.loads() 把它变成 Python dict
data = json.loads(json_string)

# 现在可以取值了！
print(data["status"])        # "ok"
print(data["totalResults"])  # 58
```

## 嵌套结构怎么一层层取？

这是今天项目中最常见的操作——API 返回的数据是"俄罗斯套娃"式的嵌套结构。

```python
# NewsAPI 返回的数据结构（简化版）
data = {
    "status": "ok",              # 顶层：dict
    "totalResults": 58,          # 顶层：数字
    "articles": [                # 顶层：list
        {                        # 列表第1个元素：dict
            "title": "...",
            "source": {          # 二级嵌套：dict 里面还有 dict！
                "name": "Bloomberg"
            }
        }
    ]
}

# 取值路线：
data["articles"]                         # 列表
data["articles"][0]                      # 第1篇文章（dict）
data["articles"][0]["title"]            # 标题（str）
data["articles"][0]["source"]           # 来源（dict）
data["articles"][0]["source"]["name"]   # 来源名称（str）
```

> **记忆：dict 用键访问 `["键名"]`，list 用数字索引 `[0]`，交替使用。**

## 四个最容易搞混的函数

| 函数 | 方向 | 记忆方法 |
|------|------|----------|
| `json.loads(str)` | JSON 字符串 → Python 对象 | **load** from **S**tring |
| `json.dumps(obj)` | Python 对象 → JSON 字符串 | **dump** to **S**tring |
| `json.load(file)` | JSON 文件 → Python 对象 | **load** from **F**ile |
| `json.dump(obj, file)` | Python 对象 → JSON 文件 | **dump** to **F**ile |

> **带 `s` 的操作字符串，不带 `s` 的操作文件。**

## 中文乱码问题：`ensure_ascii=False`

```python
data = {"name": "张三", "city": "北京"}

# 不加 ensure_ascii=False（默认 True）
text = json.dumps(data)
print(text)
# 输出: {"name": "\u5f20\u4e09", "city": "\u5317\u4eac"}
#      ↑ \u5f20\u4e09 是"张三"的 Unicode 编码，人类看不懂

# 加上 ensure_ascii=False
text = json.dumps(data, ensure_ascii=False)
print(text)
# 输出: {"name": "张三", "city": "北京"}
#      ↑ 中文直接显示，人类可读
```

> **任何需要人类看的 JSON 文件，都必须加 `ensure_ascii=False`。**

## 你今天的变量里到底长什么样？

```python
# 阶段1：news_fetcher.fetch_financial_news() 返回
articles = [
    {
        "source": {"id": "cnn", "name": "CNN"},
        "author": "John Doe",
        "title": "Stock Market Up",
        "description": "...",
        "url": "https://...",
        "publishedAt": "2026-05-09T..."
    },
    # ... 更多新闻
]
# articles 是一个 list（列表）
# articles[0] 是一个 dict（字典）
# articles[0]["source"] 又是一个 dict
# articles[0]["source"]["name"] 是一个 str（字符串）

# 阶段3：news_analyzer.analyze_single_news() 返回
analysis = {
    "summary": "美怀疑英伟达芯片经泰国走私至阿里",
    "importance": "此事件加剧中美科技脱钩风险...",
    "impact": {
        "stocks": "短期利空英伟达...",
        "bonds": "可能推升美国国债避险买盘...",
        "forex": "短期利好美元...",
        "gold": "小幅提振避险需求..."
    },
    "macro_logic": "核心逻辑在于美国对华技术封锁...",
    "sentiment": "bearish",
    "key_assets": ["NVDA", "SMCI", "BABA"]
}
# analysis 是一个 dict
# analysis["impact"] 又是一个 dict
# analysis["impact"]["stocks"] 是一个 str
# analysis["key_assets"] 是一个 list
```

## 小结

1. JSON 是**字符串格式**（用于传输和存储），Python dict/list 是**内存对象**（用于计算）
2. `json.loads()` 把字符串变成对象，`json.dumps()` 把对象变成字符串
3. 嵌套取值：dict 用 `["键"]`，list 用 `[数字索引]`，交替使用
4. `.get("键", 默认值)` 比 `["键"]` 更安全（键不存在不报错）
5. 保存中文 JSON 必须加 `ensure_ascii=False`
