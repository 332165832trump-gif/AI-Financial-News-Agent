# AI Financial News Agent

> 一个从零开始构建的 AI 金融新闻分析 Agent —— 适合 Python 初学者的工程项目。

## 这是什么？

每天自动获取全球金融新闻 → AI 智能分析 → 判断市场情绪 → 生成日报和简报 → 保存到本地。

它不是一个"一次性脚本"，而是一个**真正的 AI Agent**——有观察、有思考、有决策、有行动。

## 今天实现了什么？

```
阶段1: ✅ 自动获取金融新闻（NewsAPI）
阶段2: ✅ AI 智能分析（DeepSeek，便宜且强）
阶段3: ✅ 结构化 JSON 输出（程序可读）
阶段4: ✅ 自动循环运行（定时任务）
阶段5: ✅ 保存日报（JSON持久化）
阶段6: ✅ 注入市场行情数据（股票/债券/黄金/原油/美元）
阶段7: ✅ 真正 Agent 化（筛选→打分→决策→行动）
阶段8: ✅ 质量评估系统（人工审核+准确率统计）
```

## Agent 架构

```
┌──────────────────────────────────────────────────┐
│                                                  │
│  👁 OBSERVE   获取新闻 + 市场行情数据               │
│       │                                          │
│       ▼                                          │
│  🧠 THINK     关键词打信号分 → 去重 → 排序          │
│       │                                          │
│       ▼                                          │
│  🎯 DECIDE    高分=深度分析，中分=记录，低分=跳过     │
│       │                                          │
│       ▼                                          │
│  ⚡ ACT       调用 AI → 生成简报 → 保存文件         │
│       │                                          │
│       ▼                                          │
│  💾 MEMORY    每日 JSON 日报 + URL 去重           │
│       │                                          │
│       ▼                                          │
│  📊 REVIEW    人工审核 → 统计正确率                │
│                                                  │
└──────────────────────────────────────────────────┘
```

## 数据流

```
NewsAPI ────→ news_fetcher.py ──→ 10条新闻（list of dict）
                                        │
Yahoo Finance  ──→  market_data.py  ──→ 市场行情（dict）
                                        │
                              ┌─────────┴─────────┐
                              ▼                   ▼
                         agent.py            DeepSeek API
                      信号打分+筛选              │
                              │                │
                              ▼                ▼
                         只分析高分新闻  ←──  AI 分析 (JSON)
                              │
                              ▼
                    ┌─────────┴─────────┐
                    ▼                   ▼
            data/daily/*.json    data/briefings/*.json
              (日报存档)            (每日简报)
                    │
                    ▼
            data/review/*.json
              (质量评估)
                    │
              ┌─────┴─────┐
              ▼           ▼
          review.py    evaluate.py
         (人工打分)    (正确率统计)
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置密钥

打开 `.env` 文件，填入你的 API 密钥：

```
NEWS_API_KEY=你的NewsAPI密钥      # https://newsapi.org/
DEEPSEEK_API_KEY=你的DeepSeek密钥  # https://platform.deepseek.com/
```

### 3. 运行 Agent

```bash
python main.py
```

### 4. 审核分析结果

```bash
python review.py          # 逐条打分
python evaluate.py        # 看正确率统计
```

## 我今天学到了什么

| 类别 | 具体内容 |
|------|----------|
| **API 思维** | HTTP 请求、JSON、状态码、API Key 鉴权 |
| **数据流思维** | dict/list 嵌套结构、数据在各模块间如何传递 |
| **结构化输出** | JSON Schema、Prompt 工程、容错解析 |
| **自动化思维** | 定时循环、守护进程、Ctrl+C 优雅退出 |
| **Agent 思维** | Observe→Think→Decide→Act 循环 |
| **工程思维** | 模块化、日志、异常处理、防御性编程 |
| **成本意识** | Token 计费、API 速率限制、按需分析 |
| **质量保障** | 人工审核、正确率统计、持续改进 |

## 为什么这个项目适合 AI Agent 入门？

1. **数据免费**：NewsAPI + yfinance 都不花钱
2. **AI 便宜**：DeepSeek 分析一条新闻不到 1 分钱
3. **层层递进**：8 个阶段，每阶段只加一个新概念
4. **真实运行**：不是玩具代码，是真正能长期跑的 Agent
5. **可扩展**：加邮件推送、加更多数据源、加回测系统……

## 项目结构

```
AI-Financial-News-Agent/
├── main.py                  ← Agent 主循环
├── review.py                ← 人工审核工具
├── evaluate.py              ← 准确率统计
├── .env                     ← API 密钥（别提交 Git）
├── requirements.txt
├── src/
│   ├── news_fetcher.py      ← 阶段1：获取新闻
│   ├── news_analyzer.py     ← 阶段2-3：AI分析+JSON输出
│   ├── market_data.py       ← 阶段6：市场行情数据
│   ├── report_saver.py      ← 阶段5：保存日报
│   └── agent.py             ← 阶段7-8：Agent核心+审核文件生成
├── docs/                    ← 学习文档
│   ├── 01_project_overview.md
│   ├── 02_what_is_api.md
│   ├── 03_json_and_python_dict.md
│   ├── 04_news_pipeline.md
│   ├── 05_agent_workflow.md
│   ├── 06_debugging_lessons.md
│   ├── 07_common_errors.md
│   ├── 08_engineering_thinking.md
│   └── 09_next_steps.md
├── examples/                ← 可运行的短小 Demo
│   ├── simple_requests_demo.py
│   ├── json_demo.py
│   ├── loop_demo.py
│   └── debug_demo.py
├── notes/
│   └── today_learning_notes.md
└── data/
    ├── daily/               ← 日报 JSON
    ├── briefings/           ← 每日简报 JSON
    └── review/              ← 审核文件 JSON
```

## 后续怎么扩展

- 📧 把日报发送到邮箱或微信
- 🌐 用 Playwright 爬更多新闻源
- 📊 接入图表：每天的情绪走势、资产热度
- 🔍 语义搜索：查询历史分析
- 📈 回测：验证 AI 判断的准确率
- 🗄️ 用 SQLite 替代 JSON 做数据存储
