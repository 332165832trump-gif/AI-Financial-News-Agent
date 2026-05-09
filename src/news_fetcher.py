"""
新闻抓取模块 - 阶段1 MVP
功能：从 NewsAPI 获取金融新闻并打印
"""

import os          # 用于读取系统环境变量
import requests    # 用于发送 HTTP 请求（即访问网页/API）

# ============================================================
# 第1步：加载 .env 文件中的 API 密钥
# ============================================================

# python-dotenv 库的作用：自动读取项目根目录的 .env 文件
# 把里面的 KEY=VALUE 变成 Python 能访问的变量
from dotenv import load_dotenv

# load_dotenv() 会找到项目里的 .env 文件，把内容加载到 os.environ 里
# 调用这个方法后，就可以用 os.getenv("变量名") 读取 .env 中的值
load_dotenv()

# ============================================================
# 第2步：定义函数 —— fetch_financial_news()
# ============================================================

def fetch_financial_news():
    """
    从 NewsAPI 获取金融新闻

    这个函数做了以下事情：
    1. 构造 API 请求地址（URL + 参数）
    2. 发送 GET 请求
    3. 检查请求是否成功
    4. 解析返回的 JSON 数据
    5. 返回新闻文章列表
    """

    # --- 2.1 读取 API 密钥 ---
    # os.getenv("变量名") 会从环境变量中读取值
    # 如果找不到这个变量，返回 None
    api_key = os.getenv("NEWS_API_KEY")

    # 【debug print】看看有没有读到密钥
    # 注意：正式项目里不能打印密钥！这里只是教学用
    print(f"[DEBUG] 读到的 API 密钥前10位: {api_key[:10]}...")

    # 安全检查：如果没有密钥，直接报错并退出
    if api_key is None or api_key == "请在这里填入你的API密钥":
        print("❌ 错误：请先在 .env 文件中填入你的 NewsAPI 密钥")
        print("   去 https://newsapi.org/ 免费注册获取")
        return []  # 返回空列表

    # --- 2.2 构造请求 ---
    # API 的网址（端点/endpoint）
    url = "https://newsapi.org/v2/top-headlines"

    # 请求参数：告诉 API 我们想要什么数据
    # params 是一个字典（dict），Python 里用 {} 表示
    # 键值对格式：{"key": "value"}
    params = {
        "category": "business",  # 商业/财经类新闻
        "language": "en",        # 英文新闻（金融新闻英文更全）
        "pageSize": 10,          # 只取10条（免费API有限制）
        "apiKey": api_key        # 你的密钥
    }

    print("[DEBUG] 正在向 NewsAPI 发送请求...")

    # --- 2.3 发送 GET 请求 ---
    # requests.get(网址, 参数) → 向服务器发送请求
    # 返回一个 Response 对象（服务器给你的"回复"）
    response = requests.get(url, params=params)

    # 【debug print】看看服务器返回的状态码
    # 200 = 成功, 401 = 密钥错误, 404 = 找不到, 500 = 服务器炸了
    print(f"[DEBUG] 服务器返回状态码: {response.status_code}")

    # --- 2.4 检查请求是否成功 ---
    if response.status_code != 200:
        print(f"❌ 请求失败，状态码: {response.status_code}")
        print(f"   错误信息: {response.text[:200]}")  # 只打印前200字符
        return []

    # --- 2.5 解析 JSON ---
    # response.json() 把服务器返回的 JSON 字符串 → Python 的 dict
    # JSON 长什么样？看下面的注释 ↓

    data = response.json()

    # 【debug print】看看整个 data 的"顶层结构"
    # .keys() 返回字典有哪些键，比如 {"status", "totalResults", "articles"}
    print(f"[DEBUG] 返回数据的一级键: {list(data.keys())}")

    # 【debug print】看看有多少条新闻
    print(f"[DEBUG] 共获取到 {data.get('totalResults', 0)} 条新闻")
    print(f"[DEBUG] 本页实际返回 {len(data.get('articles', []))} 条")

    # --- 2.6 提取新闻列表 ---
    # data["articles"] 从字典中取出 "articles" 这个键对应的值
    # 这个值是一个列表（list），里面每条新闻又是一个字典（dict）
    articles = data.get("articles", [])

    return articles


# ============================================================
# 第3步：定义函数 —— print_news()
# ============================================================

def print_news(articles):
    """
    把新闻列表打印到屏幕上

    参数:
        articles: 一个列表，里面每个元素是一条新闻的字典
    """

    # 安全检查
    if not articles:
        print("⚠️  没有新闻可显示。")
        return

    print(f"\n{'='*60}")
    print(f"📰 金融新闻头条 (共 {len(articles)} 条)")
    print(f"{'='*60}\n")

    # 遍历列表：for 循环
    # enumerate() 同时给出 序号 和 内容
    for i, article in enumerate(articles, start=1):
        # 从文章字典中提取标题和来源
        title = article.get("title", "(无标题)")
        source_name = article.get("source", {}).get("name", "未知来源")
        url = article.get("url", "")
        published = article.get("publishedAt", "")

        print(f"【{i}】{title}")
        print(f"    来源: {source_name} | 时间: {published}")
        print(f"    链接: {url}")
        print(f"    {'-'*50}")

    print(f"\n✅ 新闻打印完成。")


# ============================================================
# 第4步：主函数 —— 把上面的函数串起来
# ============================================================

def run():
    """
    主流程：获取新闻 → 打印新闻
    """
    print("=" * 60)
    print("🚀 AI金融新闻分析Agent - 阶段1：获取新闻")
    print("=" * 60)

    # 获取新闻
    articles = fetch_financial_news()

    # 打印新闻
    print_news(articles)

    return articles


# ============================================================
# Python 的入口检查
# ============================================================
# 这段代码的意思是：
# 如果直接运行这个文件（python news_fetcher.py），就执行 run()
# 如果是被别的文件 import，就不自动执行
if __name__ == "__main__":
    run()
