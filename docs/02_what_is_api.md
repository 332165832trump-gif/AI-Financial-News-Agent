# 02 - 什么是 API（用你能听懂的话）

## 一句话解释

**API 就是"别人写好的函数，放在互联网上，你通过网址来调用"。**

## 类比：餐厅点餐

```
你（Python代码）                       餐厅厨房（别人的服务器）
     │                                        │
     │  ① 看菜单（读API文档）                    │
     │  ② 点菜 "我要一份宫保鸡丁"               │
     │     requests.get("https://api.xxx/菜单") │
     │  ──────────────────────────────────────→│
     │                                        │ ③ 厨师做菜
     │  ④ 上菜                                │
     │  ←──────────────────────────────────────│
     │  response.json() = {"菜名": "宫保鸡丁", │
     │                     "价格": 38,         │
     │                     "辣度": "中辣"}     │
     │                                        │
     │  ⑤ 你的代码处理数据                      │
```

- **菜单** = API 文档（告诉你有什么菜、怎么点）
- **点菜** = `requests.get("网址")`（你告诉服务器你要什么）
- **上菜** = `response.json()`（服务器把结果给你）
- **API Key** = 会员卡（证明你有权限点菜）

## 真实例子：今天用到的 3 个 API

### 1. NewsAPI（获取新闻）

```python
# 菜单上写着：访问这个网址就能拿到财经新闻
url = "https://newsapi.org/v2/top-headlines"

# 点菜：我要财经类、英文、10条
params = {
    "category": "business",
    "language": "en",
    "pageSize": 10,
    "apiKey": "你的密钥"     # ← 会员卡
}

# 下单
response = requests.get(url, params=params)

# 上菜：把返回的数据变成 Python 能用的格式
news_data = response.json()
```

### 2. DeepSeek API（AI 分析）

```python
# DeepSeek 的菜单：发一段文字，AI 回复一段文字
from openai import OpenAI

client = OpenAI(
    api_key="你的密钥",
    base_url="https://api.deepseek.com"  # ← 注意：不是 openai.com！
)

# 点菜：把新闻标题发给 AI，让它分析
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "请分析这条新闻..."}]
)

# 上菜：AI 返回的分析结果
analysis = response.choices[0].message.content
```

### 3. Yahoo Finance（市场行情）

```python
import yfinance as yf

# 点菜：我要标普500最近5天的数据
ticker = yf.Ticker("^GSPC")
data = ticker.history(period="5d")

# 上菜：一个表格，有开盘价、最高价、最低价、收盘价
latest_price = data["Close"].iloc[-1]
```

## 为什么 API Key 不能写在代码里？

```python
# ❌ 错误做法：密钥写在代码里
api_key = "053ea94351954b1595f4b1de820f8c1c"

# 问题：你把代码上传到 GitHub 后，全世界都能看到你的密钥
# 别人可以用你的密钥疯狂调用 API，你的额度会被用完，甚至收到账单
```

```python
# ✅ 正确做法：密钥放在 .env 文件里
# .env 文件：
# NEWS_API_KEY=053ea94351954b1595f4b1de820f8c1c

from dotenv import load_dotenv
import os

load_dotenv()                               # 读取 .env 文件
api_key = os.getenv("NEWS_API_KEY")         # 从环境变量获取

# .env 文件在 .gitignore 里，不会被上传到 GitHub
```

## HTTP 状态码速查

| 状态码 | 含义 | 你现在该做什么 |
|--------|------|---------------|
| **200** | 一切正常 | 继续处理数据 |
| **401** | API Key 错误 | 检查 .env 里的密钥 |
| **404** | 你要的东西不存在 | 检查网址拼写 |
| **429** | 你请求太频繁了 | 等一会再试 |
| **500** | 服务器自己出错了 | 不是你代码的问题，重试 |

```python
response = requests.get(url, params=params)
if response.status_code == 200:
    print("成功！")
elif response.status_code == 401:
    print("密钥错误！")
else:
    print(f"其他错误：{response.status_code}")
```

## 你今天学会的

- API = 别人放在互联网上的函数，你用网址来调用
- `requests.get()` = 你向 API 说"请给我数据"
- `response.json()` = 把 API 返回的字符串变成 Python 能用的格式
- API Key = 身份证/会员卡，必须放在 .env 里
- 状态码 = 服务器告诉你的第一句话（200=OK, 401=没权限）
