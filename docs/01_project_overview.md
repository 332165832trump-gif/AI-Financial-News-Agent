# 01 - 项目全景：今天到底做了什么

## 一句话总结

从 0 行代码开始，一步步搭建了一个 **能自动获取金融新闻、调用 AI 分析、生成日报、并自我评估质量** 的 AI Agent。

## 为什么要做这个项目？

大部分 Python 教程教你语法，但不知道"学了之后能做什么"。这个项目反过来——**以终为始**：

1. 先定目标：做一个能自动分析金融新闻的 AI
2. 再拆步骤：把"大目标"拆成 8 个"小阶段"
3. 每个阶段只学一个新概念
4. 每写完一步都能真正跑起来

## 8 个阶段一览

| 阶段 | 做什么 | 学到什么 |
|------|--------|----------|
| 阶段1 | 获取金融新闻并打印 | `requests.get()`, JSON, API Key |
| 阶段2 | 接入 AI 分析新闻 | OpenAI SDK, Prompt, Token |
| 阶段3 | 结构化输出 JSON | JSON Schema, `json.loads()`, 容错解析 |
| 阶段4 | 自动循环运行 | `while True`, `time.sleep()`, `try/except` |
| 阶段5 | 保存日报 | `json.dump()`, `with open()`, 文件读写 |
| 阶段6 | 加入市场行情数据 | `yfinance`, 数据注入 Prompt |
| 阶段7 | 真正 Agent 化 | 筛选→打分→决策→行动 |
| 阶段8 | 质量评估系统 | 人工审核、正确率统计 |

每个阶段增加的代码不多（通常 50-100 行），但每一步都在解决一个真实问题。

## 项目结构

```
AI-Financial-News-Agent/
├── main.py                  ← 主入口（Agent 循环）
├── review.py                ← 人工审核
├── evaluate.py              ← 正确率统计
├── src/
│   ├── news_fetcher.py      ← 获取新闻
│   ├── news_analyzer.py     ← AI 分析
│   ├── market_data.py       ← 市场行情
│   ├── report_saver.py      ← 保存日报
│   └── agent.py             ← Agent 核心
├── data/                    ← 所有数据存这里
└── docs/                    ← 学习文档（你正在看的）
```

## 数据怎么流动？

```
NewsAPI ──→ 10条新闻（dict列表）
                │
Yahoo Finance ──→ 市场行情（dict）
                │
        ┌───────┴────────┐
        ▼                ▼
   信号打分+筛选      DeepSeek AI
        │                │
        ▼                ▼
   只分析高分新闻  ←── JSON分析结果
        │
        ▼
   data/daily/*.json  ← 日报
   data/briefings/*.json ← 简报
   data/review/*.json ← 审核
```

## 为什么这件事值得做？

1. **真实的 AI Agent 入门**：不是玩具代码，是能每天跑的生产级工具
2. **层层递进**：8 个阶段，每阶段只加一个新概念
3. **成本极低**：NewsAPI 免费 + DeepSeek 便宜（一条分析不到 1 分钱）
4. **可扩展**：可以加邮件推送、更多数据源、回测系统……

## 下一步从哪里开始？

- 刚入门：从 `examples/` 里的小 demo 开始跑
- 想理解概念：按顺序读 `docs/02` → `docs/03` → `docs/04`
- 想改代码：打开 `src/` 下的任意文件，有大量中文注释
- 想验证理解：运行 `python review.py` 体验人工审核
