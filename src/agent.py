"""
AI 金融新闻 Agent - 阶段7
功能：把流水线升级为真正的 Agent（观察→判断→决策→行动）
"""

import json
import os
from datetime import datetime
from src import news_fetcher
from src import news_analyzer
from src import market_data
from src import report_saver


# ============================================================
# 第1步：定义"信号词库"——快速判断新闻是否值得关注
# ============================================================

# 这是 Agent 的"直觉系统"——不需要调用 AI，靠关键词就能快速初筛
# 为什么要有这个？
#   1. 节省 API 费用（不用每条都送给 AI 分析）
#   2. 速度极快（字符串匹配比 API 调用快1000倍）
#   3. 可以根据自己的关注点定制

HIGH_SIGNAL_KEYWORDS = [
    # 宏观
    "fed", "federal reserve", "rate hike", "rate cut", "interest rate",
    "inflation", "cpi", "ppi", "gdp", "recession",
    "jobs report", "nonfarm", "unemployment",

    # 地缘政治
    "war", "sanction", "tariff", "trade war", "geopolitical",
    "iran", "china", "russia", "north korea",

    # 市场
    "stock market", "dow", "s&p 500", "nasdaq", "futures",
    "bull", "bear", "crash", "rally", "sell-off", "plunge", "surge",

    # 资产
    "oil", "crude", "gold", "bitcoin", "crypto", "treasury", "bond",
    "dollar", "forex", "yield",

    # 科技/芯片
    "nvidia", "amd", "intel", "chip", "semiconductor", "ai chip",
    "tsmc", "apple", "microsoft", "google", "amazon", "meta",
    "tesla", "openai",

    # 金融事件
    "ipo", "merger", "acquisition", "layoff", "earnings", "bankruptcy",
    "regulation", "sec", "doj",
]

# 低信号词：通常不重要的新闻
LOW_SIGNAL_KEYWORDS = [
    "celebrity", "entertainment", "sports", "weather",
    "recipe", "lifestyle", "fashion",
]


# ============================================================
# 第2步：快速筛选——判断新闻是否和金融相关
# ============================================================

def _calculate_signal_score(article):
    """
    根据关键词计算一条新闻的"信号分数"

    这是一个简单的规则引擎（Rule Engine）：
      - 匹配到高信号词 → 加分
      - 匹配到低信号词 → 减分
      - 分数越高 → 越值得分析

    参数:
        article: 新闻 dict

    返回:
        (分数, 匹配到的高信号词列表)
    """

    # 把标题和摘要合并成一段文字（统一转小写）
    title = article.get("title", "").lower()
    description = article.get("description", "").lower()
    text = title + " " + description

    score = 0
    matched_keywords = []

    # 匹配高信号词
    for keyword in HIGH_SIGNAL_KEYWORDS:
        if keyword in text:
            score += 2                    # 每个高信号词 +2 分
            matched_keywords.append(keyword)

    # 匹配低信号词（扣分）
    for keyword in LOW_SIGNAL_KEYWORDS:
        if keyword in text:
            score -= 3                    # 每个低信号词 -3 分

    # 来源加分：知名金融媒体更有价值
    source_name = article.get("source", {}).get("name", "").lower()
    premium_sources = ["bloomberg", "cnbc", "reuters", "wsj", "financial times",
                       "barrons", "investor's business daily"]
    if any(src in source_name for src in premium_sources):
        score += 1

    return score, matched_keywords


def _is_duplicate(article, analyzed_urls):
    """
    检查这条新闻是否已经分析过

    用 URL 作为唯一标识（去重）

    参数:
        article: 新闻 dict
        analyzed_urls: 已经分析过的 URL 集合（set）

    返回:
        True = 重复, False = 新新闻
    """

    url = article.get("url", "")
    if not url:
        return False

    if url in analyzed_urls:
        return True

    return False


# ============================================================
# 第3步：Agent 决策系统——根据分数决定行动
# ============================================================

def _decide_action(score):
    """
    根据信号分数，决定采取什么行动

    这是 Agent 的"决策模块"——类似 if/else 但更有层次

    返回:
        (行动类型, 优先级)
    """

    if score >= 6:
        return "HIGH_PRIORITY", 1       # 高优先级：必须深度分析
    elif score >= 3:
        return "ANALYZE", 2             # 正常分析
    elif score >= 0:
        return "RECORD_ONLY", 3         # 只记录标题，不调用 AI
    else:
        return "SKIP", 4                # 跳过


# ============================================================
# 第4步：生成每日简报（Agent 的"输出产品"）
# ============================================================

def _generate_briefing(all_results, market_data_text=""):
    """
    把今天的分析结果汇总成一份"每日简报"

    这是 Agent 的最终输出——不只是一堆 JSON，
    而是有逻辑、有层次的总结报告

    参数:
        all_results: 当天所有分析结果列表
        market_data_text: 市场行情文本

    返回:
        简报 dict
    """

    if not all_results:
        return {"summary": "今日无重要金融新闻。"}

    # 统计
    total = len(all_results)
    bullish_count = 0
    bearish_count = 0
    neutral_count = 0
    all_key_assets = []
    high_priority = []

    for item in all_results:
        analysis = item.get("analysis", {})
        if isinstance(analysis, dict):
            sentiment = analysis.get("sentiment", "neutral")
            if sentiment == "bullish":
                bullish_count += 1
            elif sentiment == "bearish":
                bearish_count += 1
            else:
                neutral_count += 1

            # 收集关键资产
            assets = analysis.get("key_assets", [])
            all_key_assets.extend(assets)

            # 高优先级新闻
            if item.get("priority") == 1:
                high_priority.append({
                    "title": item.get("article", {}).get("title", ""),
                    "summary": analysis.get("summary", ""),
                    "sentiment": sentiment,
                })

    # 去重关键资产
    unique_assets = list(set(all_key_assets))

    # 判断整体市场情绪
    if bullish_count > bearish_count and bullish_count > neutral_count:
        overall_sentiment = "偏多 (Bullish)"
    elif bearish_count > bullish_count and bearish_count > neutral_count:
        overall_sentiment = "偏空 (Bearish)"
    else:
        overall_sentiment = "中性 (Neutral)"

    briefing = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall_sentiment": overall_sentiment,
        "statistics": {
            "total_analyzed": total,
            "bullish": bullish_count,
            "bearish": bearish_count,
            "neutral": neutral_count,
        },
        "key_assets_today": unique_assets,
        "high_priority_news": high_priority,
        "market_snapshot": market_data_text,
    }

    return briefing


# ============================================================
# 第5步：保存简报
# ============================================================

def _save_briefing(briefing):
    """保存每日简报到 data/briefings/ 目录"""

    brief_dir = "data/briefings"
    os.makedirs(brief_dir, exist_ok=True)

    date_str = briefing["date"]
    filepath = os.path.join(brief_dir, f"briefing_{date_str}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(briefing, f, ensure_ascii=False, indent=2)

    print(f"📋 每日简报已保存: {filepath}")
    return filepath


# ============================================================
# 第6步：打印简报（给人看的）
# ============================================================

def _print_briefing(briefing):
    """打印每日简报摘要"""

    print(f"\n{'='*60}")
    print(f"📋 每日金融简报 - {briefing['date']}")
    print(f"{'='*60}")

    stats = briefing["statistics"]
    print(f"\n📊 今日统计:")
    print(f"   分析新闻数: {stats['total_analyzed']}")
    print(f"   偏多: {stats['bullish']}  偏空: {stats['bearish']}  中性: {stats['neutral']}")
    print(f"   整体情绪: {briefing['overall_sentiment']}")

    if briefing["key_assets_today"]:
        print(f"\n🎯 今日关键资产: {', '.join(briefing['key_assets_today'][:10])}")

    if briefing["high_priority_news"]:
        print(f"\n⚠️  高优先级新闻 ({len(briefing['high_priority_news'])} 条):")
        for item in briefing["high_priority_news"]:
            print(f"   • [{item['sentiment'].upper()}] {item['summary'][:60]}")

    print(f"{'='*60}")


# ============================================================
# 第7步：Agent 主循环（核心！）
# ============================================================

def run_agent_cycle(run_number, analyzed_urls=None):
    """
    Agent 单次循环：Observe → Think → Decide → Act

    这是整个项目最重要的函数——
    它把阶段1-6的所有模块串成一个真正的 Agent

    参数:
        run_number: 第几次运行
        analyzed_urls: 已分析过的 URL 集合（去重用）

    返回:
        (results, analyzed_urls, briefing)
    """

    if analyzed_urls is None:
        analyzed_urls = set()

    print("\n" + "=" * 60)
    print(f"🤖 Agent 运行 #{run_number}")
    print("=" * 60)

    # =========================================
    # 👁 Step 1: Observe（观察）
    # =========================================
    print("\n👁 [Observe] 获取新闻和市场数据...")
    articles = news_fetcher.fetch_financial_news()
    market_data_result = market_data.fetch_all_market_data()
    market_text = market_data.format_market_data_for_prompt(market_data_result)

    if not articles:
        print("⚠️  没有获取到新闻。")
        return [], analyzed_urls, None

    print(f"   获取到 {len(articles)} 条新闻")

    # =========================================
    # 🧠 Step 2: Think（思考/筛选）
    # =========================================
    print("\n🧠 [Think] 筛选和打分...")

    scored_articles = []
    for article in articles:
        # 去重检查
        if _is_duplicate(article, analyzed_urls):
            continue

        score, keywords = _calculate_signal_score(article)
        action, priority = _decide_action(score)

        scored_articles.append({
            "article": article,
            "score": score,
            "keywords": keywords,
            "action": action,
            "priority": priority,
        })

    # 按优先级排序（分数高的先分析）
    scored_articles.sort(key=lambda x: x["score"], reverse=True)

    # 统计筛选结果
    skip_count = sum(1 for s in scored_articles if s["action"] == "SKIP")
    analyze_count = sum(1 for s in scored_articles if s["action"] != "SKIP")
    high_count = sum(1 for s in scored_articles if s["action"] == "HIGH_PRIORITY")

    print(f"   筛选结果: {analyze_count} 条值得分析, {skip_count} 条跳过")
    print(f"   其中高优先级: {high_count} 条")

    # 打印每条新闻的信号分数（调试）
    for s in scored_articles:
        title = s["article"].get("title", "")[:50]
        print(f"   [分数:{s['score']:2d}] [{s['action']:15s}] {title}...")

    # =========================================
    # 🎯 Step 3: Decide + Act（决策 + 行动）
    # =========================================
    print(f"\n🎯 [Decide+Act] 开始分析...")

    client = news_analyzer._create_client()
    if client is None:
        print("❌ DeepSeek 客户端创建失败。")
        return [], analyzed_urls, None

    results = []
    analyzed_count = 0
    max_analyze = 5  # 每轮最多分析5条（控制费用）

    for item in scored_articles:
        if analyzed_count >= max_analyze:
            print(f"   达到本轮分析上限 ({max_analyze} 条)，剩余跳过")
            break

        action = item["action"]
        article = item["article"]
        url = article.get("url", "")

        if action == "SKIP":
            continue

        if action == "RECORD_ONLY":
            # 只记录，不调用 AI
            print(f"   📝 仅记录: {article.get('title', '')[:50]}...")
            results.append({
                "article": article,
                "analysis": {"summary": "低信号新闻，未深度分析"},
                "priority": item["priority"],
                "score": item["score"],
            })
            analyzed_urls.add(url)
            analyzed_count += 1
            continue

        # HIGH_PRIORITY 或 ANALYZE：调用 AI 深度分析
        print(f"   🤖 AI分析 [{item['action']}]: "
              f"{article.get('title', '')[:50]}...")

        analysis = news_analyzer.analyze_single_news(
            article,
            client=client,
            market_data_text=market_text
        )

        results.append({
            "article": article,
            "analysis": analysis,
            "priority": item["priority"],
            "score": item["score"],
        })

        analyzed_urls.add(url)
        analyzed_count += 1

    print(f"\n   本轮共分析 {analyzed_count} 条新闻")

    # =========================================
    # 📋 Step 4: 生成简报
    # =========================================
    briefing = _generate_briefing(results, market_text)
    _save_briefing(briefing)
    _print_briefing(briefing)

    # 也保存原始的日报（阶段5功能保留）
    report_saver.save_daily_report(
        [r for r in results if r.get("analysis")],
        news_count=len(articles)
    )

    # 阶段8新增：生成待审核文件
    _generate_review_file(results)

    return results, analyzed_urls, briefing


# ============================================================
# 阶段8：生成待审核文件
# ============================================================

def _generate_review_file(results):
    """
    从本轮分析结果生成 data/review/review_YYYY-MM-DD.json

    每条 AI 分析记录都带上 human_check / human_note / checked_at 字段，
    初始值为 null，等 review.py 来填写。

    参数:
        results: 本轮分析结果列表
    """

    # 只保留有实际 AI 分析的结果（跳过 RECORD_ONLY）
    valid_results = [r for r in results
                     if r.get("analysis") and isinstance(r["analysis"], dict)
                     and "raw_text" not in r.get("analysis", {})]

    if not valid_results:
        return

    date_str = datetime.now().strftime("%Y-%m-%d")
    review_path = os.path.join("data", "review", f"review_{date_str}.json")

    # 读取已有的审核文件（如果今天多次运行，要合并）
    existing_items = []
    if os.path.exists(review_path):
        try:
            with open(review_path, "r", encoding="utf-8") as f:
                old_review = json.load(f)
                existing_items = old_review.get("items", [])
            print(f"[DEBUG] 合并已有审核文件: {len(existing_items)} 条旧记录")
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    # 已存在的 URL 集合（避免重复添加）
    existing_urls = {item["url"] for item in existing_items if item.get("url")}

    # 把本轮结果转成审核记录格式
    new_items = []
    for r in valid_results:
        article = r.get("article", {})
        analysis = r.get("analysis", {})

        url = article.get("url", "")
        if url in existing_urls:
            continue  # 跳过已存在的

        # 组装审核记录（每一条都要人工打分）
        review_item = {
            "title": article.get("title", ""),
            "url": url,
            "summary": analysis.get("summary", ""),
            "importance": analysis.get("importance", ""),
            "affected_assets": analysis.get("key_assets", []),
            "market_impact": analysis.get("impact", {}),
            "sentiment": analysis.get("sentiment", "neutral"),
            "reasoning": analysis.get("macro_logic", ""),
            # 人工检查字段（初始为空，等用户填写）
            "human_check": None,       # null=未检查, "correct", "questionable", "wrong"
            "human_note": "",          # 人工备注
            "checked_at": None,        # 检查时间
        }
        new_items.append(review_item)

    if not new_items:
        print("[DEBUG] 没有新增的待审核记录")
        return

    # 合并旧+新
    all_items = existing_items + new_items

    review_data = {
        "date": date_str,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(all_items),
        "checked": sum(1 for i in all_items if i["human_check"] is not None),
        "unchecked": sum(1 for i in all_items if i["human_check"] is None),
        "items": all_items,
    }

    # 确保目录存在
    os.makedirs(os.path.join("data", "review"), exist_ok=True)

    with open(review_path, "w", encoding="utf-8") as f:
        json.dump(review_data, f, ensure_ascii=False, indent=2)

    print(f"📝 待审核文件已生成: {review_path}")
    print(f"   共 {len(all_items)} 条，其中 {review_data['unchecked']} 条待检查")
