# 05 - Agent 工作流程：Observe → Think → Decide → Act

## 什么是 Agent？

> **Agent = 一个能自己观察环境、自己思考、自己决策、自己行动的程序。**

它不是"你告诉它做什么它就做什么"（那是普通脚本），而是"你告诉它目标，它自己决定怎么达成"。

## 阶段6之前 vs 阶段7之后

### 阶段6（流水线）

```
获取10条新闻 ──→ AI分析3条 ──→ 保存 ──→ 睡觉 ──→ 重复
    ↓              ↓            ↓
  不做筛选      每条都分析      全部存
```

问题：
- 10 条新闻里可能 4 条和金融无关（比如汽车、娱乐），也会被分析
- 没有优先级，重要和不重要的新闻同等对待
- 不会自己判断

### 阶段7（Agent）

```
获取10条新闻
    ↓
👁 观察：10条新闻 + 7项市场行情
    ↓
🧠 思考：关键词打分
    11分 → 高分！期货+利率+就业+芯片
    0分  → 低信号（汽车品牌联名）
    ↓
🎯 决策：
    分数 ≥ 6 → 深度 AI 分析
    分数 ≥ 3 → 正常分析
    分数 < 3 → 只记录标题
    分数 < 0 → 跳过
    ↓
⚡ 行动：AI分析 → 生成简报 → 保存文件
```

## Agent 循环四步骤详解

### 👁 Step 1: Observe（观察）

收集所有能收集到的信息：

```python
# 观察1：金融新闻
articles = news_fetcher.fetch_financial_news()
# 返回：10 条新闻的列表

# 观察2：市场行情
market_data = market_data.fetch_all_market_data()
# 返回：7 项资产的最新价格和涨跌幅

# 观察3：历史记录（哪些新闻已经分析过了）
# 用 analyzed_urls 这个 set 记录
```

### 🧠 Step 2: Think（思考/分析）

对观察到的信息做初步处理，决定哪些值得深入分析：

```python
def _calculate_signal_score(article):
    """关键词打分"""
    text = (article["title"] + " " + article["description"]).lower()
    score = 0
    
    for keyword in HIGH_SIGNAL_KEYWORDS:
        if keyword in text:
            score += 2      # 每匹配一个金融相关的词 +2 分
    
    return score
```

**为什么用关键词而不是用 AI 做筛选？**
- 关键词匹配：0.0001 秒，免费
- AI 筛选：2 秒，¥0.001/条
- 10 条先用关键词筛掉 4 条，只送 6 条给 AI，省钱省时间

### 🎯 Step 3: Decide（决策）

根据分数做不同的事：

```python
def _decide_action(score):
    if score >= 6:
        return "HIGH_PRIORITY", 1    # 必须深度分析
    elif score >= 3:
        return "ANALYZE", 2          # 正常 AI 分析
    elif score >= 0:
        return "RECORD_ONLY", 3      # 只记录标题，不调 AI
    else:
        return "SKIP", 4             # 直接跳过
```

**这就是阈值决策**——Agent 工程里最常用的模式。调高阈值 = Agent 更"保守"，调低 = 更"激进"。

### ⚡ Step 4: Act（行动）

执行决策，并留下记录：

```python
if action == "HIGH_PRIORITY" or action == "ANALYZE":
    analysis = news_analyzer.analyze_single_news(article)
    # AI 深度分析

elif action == "RECORD_ONLY":
    results.append({"article": article, "analysis": {"summary": "低信号新闻"}})
    # 只记录

else:
    continue  # 跳过
```

## Agent 的"记忆"：去重

```python
# analyzed_urls 是一个 set（集合）
# set 的特性：同一个值只会存一次
analyzed_urls = set()

# 检查是否已经分析过
url = article.get("url")
if url in analyzed_urls:
    continue            # 分析过了，跳过

# 分析完后标记
analyzed_urls.add(url)
```

这是最简单的 Agent 记忆——不需要数据库，一个 Python `set()` 就搞定了。

## Agent 的"输出产品"：每日简报

不再是散落的 JSON，而是有统计、有排序、有高亮的可读报告：

```
📋 每日金融简报 - 2026-05-09
📊 今日统计:
   分析新闻数: 5
   偏多: 2  偏空: 1  中性: 2
   整体情绪: 中性
🎯 今日关键资产: NVDA, SPY, GLD, BABA
⚠️  高优先级新闻:
   • [BEARISH] 美怀疑英伟达芯片经泰国走私至阿里
   • [BULLISH] HawkEye 360 IPO首日股价大涨
```

## 你今天写的 Agent 完整代码位置

所有 Agent 逻辑在 `src/agent.py` 的 `run_agent_cycle()` 函数中：

```python
def run_agent_cycle(run_number, analyzed_urls=None):
    # 👁 Observe
    articles = news_fetcher.fetch_financial_news()
    market_data = market_data.fetch_all_market_data()

    # 🧠 Think
    for article in articles:
        score = _calculate_signal_score(article)
        action, priority = _decide_action(score)

    # 🎯 Decide + ⚡ Act
    for item in scored_articles:
        if action in ("HIGH_PRIORITY", "ANALYZE"):
            analysis = analyze_single_news(article)
        elif action == "RECORD_ONLY":
            ...  # 只记录
        else:
            continue  # 跳过

    # 📋 生成简报
    briefing = _generate_briefing(results)
    _save_briefing(briefing)
```

## 小结

| 概念 | 一句话 |
|------|--------|
| Agent | 能自己观察→思考→决策→行动的程序 |
| 信号词库 | 关键词快速筛选，不调 AI，零成本 |
| 阈值决策 | 分数高就深度分析，分数低就跳过 |
| 去重 | 用 `set()` 记住分析过的 URL |
| 简报 | Agent 的输出产品，不是碎片 JSON |
