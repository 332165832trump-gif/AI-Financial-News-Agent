"""
新闻分析模块 - 阶段3+6
功能：使用 DeepSeek API 分析金融新闻，输出结构化 JSON
阶段6新增：注入市场行情数据，让分析更准确
"""

import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from src.market_data import fetch_all_market_data, format_market_data_for_prompt

load_dotenv()


# ============================================================
# 第1步：创建 DeepSeek 客户端（不变）
# ============================================================

def _create_client():
    """
    创建并返回 OpenAI 兼容客户端
    通过 base_url 参数，可以连接任何兼容 OpenAI 接口的服务
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if api_key is None or "请在这里填入" in api_key:
        print("❌ 错误：请先在 .env 文件中填入 DEEPSEEK_API_KEY")
        print("   去 https://platform.deepseek.com/api_keys 获取")
        return None

    print(f"[DEBUG] DeepSeek 密钥前10位: {api_key[:10]}...")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )
    return client


# ============================================================
# 第2步：构造 JSON 格式的提示词（阶段3核心改动！）
# ============================================================

def _build_prompt(article, market_data_text=None):
    """
    构造发给 AI 的提示词，要求输出 JSON 格式

    阶段6新增：market_data_text 参数
    — 把当前市场行情注入 Prompt，AI 分析时就有了"背景"
    — 这就像医生看病前先看体温和血压

    参数:
        article: 新闻 dict
        market_data_text: 市场行情文本（format_market_data_for_prompt 的输出）
    """

    title = article.get("title", "无标题")
    source_name = article.get("source", {}).get("name", "未知来源")
    url = article.get("url", "")
    description = article.get("description", "")

    # 构造市场行情部分（阶段6新增！）
    market_section = ""
    if market_data_text:
        market_section = f"""
========================================
当前市场行情（分析时请参考这些数据）：
{market_data_text}
========================================
"""

    prompt = f"""
你是一个专业的金融分析师。请分析以下新闻，并严格按照JSON格式输出。

新闻标题：{title}
新闻来源：{source_name}
新闻链接：{url}
新闻摘要：{description if description else "无"}
{market_section}
========================================
你必须输出以下JSON结构（不要输出任何其他内容）：
========================================

{{
  "summary": "用一句话概括这条新闻（中文，20字以内）",
  "importance": "为什么这条新闻对金融市场重要（中文，2-3句话）",
  "impact": {{
    "stocks": "对股票市场的影响分析（结合当前市场行情数据）",
    "bonds": "对债券市场的影响分析（结合当前国债收益率水平）",
    "forex": "对美元汇率的影响分析（结合当前美元指数水平）",
    "gold": "对黄金市场的影响分析（结合当前金价水平）"
  }},
  "macro_logic": "背后的宏观经济学逻辑（中文，2-3句话）",
  "sentiment": "整体市场情绪（只能填 bullish / bearish / neutral 三个词之一）",
  "key_assets": ["受影响的关键资产代码", "例如 NVDA"]
}}

========================================
严格规则：
1. 只输出上面的JSON，不要有任何解释、前缀、后缀
2. 不要用 ```json ``` 包裹，直接输出纯JSON
3. sentiment 必须是 bullish / bearish / neutral 之一
4. 所有分析用中文
5. 每个影响分析控制在1-2句话
6. 如果有当前市场行情数据，请在分析中引用
========================================
"""

    return prompt


# ============================================================
# 第3步：安全解析 AI 返回的 JSON（阶段3新增！）
# ============================================================

def _safe_parse_json(raw_text):
    """
    安全地把 AI 返回的文字解析成 Python dict

    AI 不一定严格输出纯 JSON，可能夹杂 markdown 标记或额外文字，
    所以需要"容错解析"——这是工程里的一个重要思维。

    参数:
        raw_text: AI 返回的原始文本

    返回:
        解析成功的 dict，失败则返回 None
    """

    if not raw_text:
        return None

    # 策略1：去掉常见的 markdown 代码块标记 ```json ... ```
    # re.sub(正则, 替换内容, 源字符串) — 替换操作
    # r"```(?:json)?\s*" 匹配 ``` 或 ```json
    cleaned = re.sub(r"```(?:json)?\s*", "", raw_text)
    cleaned = cleaned.strip()

    # 【debug】看看清洗后的文本
    print(f"[DEBUG] 清洗后JSON前80字: {cleaned[:80]}...")

    try:
        # json.loads() — 把 JSON 字符串变成 Python dict
        # 这是整个阶段3最核心的一行
        result = json.loads(cleaned)
        print("[DEBUG] ✅ JSON解析成功")
        return result

    except json.JSONDecodeError as e:
        # JSON 格式不对（比如少了一个引号、逗号等）
        print(f"[DEBUG] ❌ JSON解析失败: {e}")

        # 策略2：尝试用正则从文本中提取 JSON 对象
        # r"\{.*\}" — 匹配从 { 到 } 的内容
        # re.DOTALL — 让 . 也能匹配换行符
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group())
                print("[DEBUG] ✅ 策略2：从文本中提取JSON成功")
                return result
            except json.JSONDecodeError:
                pass

        return None


# ============================================================
# 第4步：单条新闻分析（返回值变了！str → dict）
# ============================================================

def analyze_single_news(article, client=None, market_data_text=None):
    """
    让 DeepSeek 分析一条新闻，返回结构化 dict

    阶段6新增：market_data_text 参数 — 注入当前市场行情

    参数:
        article: 一条新闻 dict
        client: DeepSeek 客户端
        market_data_text: 市场行情文本（可选）

    返回:
        结构化分析 dict
    """

    if client is None:
        client = _create_client()
        if client is None:
            return None

    prompt = _build_prompt(article, market_data_text=market_data_text)

    title = article.get("title", "无标题")[:40]
    print(f"\n[DEBUG] 正在分析: {title}...")

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800,
            # 【新增】response_format 是 OpenAI 新出的功能
            # 告诉 API 我们想要 JSON 格式输出（OpenAI 兼容的模型都支持）
            # 如果模型不支持这个参数，删掉这行就行
            response_format={"type": "json_object"}
        )

        raw_text = response.choices[0].message.content

        usage = response.usage
        print(f"[DEBUG] Token使用: "
              f"输入={usage.prompt_tokens}, "
              f"输出={usage.completion_tokens}, "
              f"总计={usage.total_tokens}")

        # 【阶段3核心】把 AI 返回的文字 → 解析成 Python dict
        structured = _safe_parse_json(raw_text)

        if structured is None:
            print("[DEBUG] ⚠️ JSON解析失败，回退为原始文本")
            # 降级方案：至少把原始文本保存下来
            return {"raw_text": raw_text}

        return structured

    except Exception as e:
        print(f"❌ 分析失败: {type(e).__name__} - {e}")
        return None


# ============================================================
# 第5步：批量分析（不变）
# ============================================================

def analyze_news_list(articles, max_count=None):
    """批量分析新闻列表（阶段6：注入市场数据）"""

    if not articles:
        print("⚠️  没有新闻可分析。")
        return []

    client = _create_client()
    if client is None:
        return []

    if max_count is not None:
        articles = articles[:max_count]

    # 【阶段6核心】获取一次市场数据，所有分析共享
    # 为什么放在这里而不是每条分析里取？
    #   1. 行情数据几秒钟不会变，重复取浪费
    #   2. yfinance 有请求限制，减少调用次数
    print("\n📈 正在获取市场行情数据（用于分析参考）...")
    market_data = fetch_all_market_data()
    market_data_text = format_market_data_for_prompt(market_data)
    print(f"[DEBUG] 市场数据已注入Prompt "
          f"({len(market_data_text)} 字符)")

    print(f"\n📊 准备分析 {len(articles)} 条新闻...")
    results = []

    for i, article in enumerate(articles, start=1):
        print(f"\n--- 分析第 {i}/{len(articles)} 条 ---")

        analysis = analyze_single_news(
            article,
            client=client,
            market_data_text=market_data_text    # 传入行情数据
        )

        result = {
            "article": article,
            "analysis": analysis     # 现在是 dict 了，不是 str！
        }
        results.append(result)

    print(f"\n✅ 分析完成：共 {len(results)} 条")
    return results


# ============================================================
# 第6步：打印结构化结果（阶段3改造）
# ============================================================

def print_analysis_results(results):
    """把结构化分析结果美观地打印出来"""

    if not results:
        print("⚠️  没有分析结果可显示。")
        return

    print(f"\n{'='*60}")
    print(f"📊 AI 金融新闻分析报告（结构化）")
    print(f"{'='*60}")

    for i, item in enumerate(results, start=1):
        article = item["article"]
        analysis = item["analysis"]  # 这是一个 dict

        title = article.get("title", "无标题")
        source = article.get("source", {}).get("name", "未知")

        print(f"\n{'━'*60}")
        print(f"【{i}】{title}")
        print(f"    来源: {source}")

        if analysis is None:
            print(f"\n⚠️  此条分析失败")
            continue

        # 检查是不是回退成了原始文本
        if "raw_text" in analysis:
            print(f"\n📝 原始文本（JSON解析失败）:")
            print(analysis["raw_text"][:300])
            continue

        # 【阶段3核心用法】从 dict 中按字段取值！
        # 这就是结构化输出的好处——程序知道每个字段的含义
        print(f"\n📌 市场情绪: {analysis.get('sentiment', 'N/A').upper()}")
        print(f"\n📝 摘要: {analysis.get('summary', 'N/A')}")
        print(f"\n💡 为什么重要: {analysis.get('importance', 'N/A')}")

        print(f"\n📈 资产影响:")
        impact = analysis.get("impact", {})
        print(f"   股票: {impact.get('stocks', 'N/A')}")
        print(f"   债券: {impact.get('bonds', 'N/A')}")
        print(f"   汇率: {impact.get('forex', 'N/A')}")
        print(f"   黄金: {impact.get('gold', 'N/A')}")

        print(f"\n🧠 宏观逻辑: {analysis.get('macro_logic', 'N/A')}")

        key_assets = analysis.get("key_assets", [])
        if key_assets:
            print(f"\n🎯 关键资产: {', '.join(key_assets)}")

    print(f"\n{'='*60}")
    print(f"✅ 报告生成完成。")


# ============================================================
# 第7步：主函数
# ============================================================

def run(articles, max_analyze=3):
    """主流程：接收新闻 → AI分析 → 打印结构化结果"""

    print("=" * 60)
    print("🤖 AI金融新闻分析 - 阶段3：结构化输出")
    print("=" * 60)

    if not articles:
        print("⚠️  没有新闻输入。")
        return []

    results = analyze_news_list(articles, max_count=max_analyze)
    print_analysis_results(results)

    return results


if __name__ == "__main__":
    from src.news_fetcher import fetch_financial_news
    articles = fetch_financial_news()
    run(articles, max_analyze=2)
