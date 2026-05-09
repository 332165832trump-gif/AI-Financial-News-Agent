# 08 - 工程思维：不只是写代码

## 什么是"工程思维"？

> **工程思维 = 写能长期运行、别人能看懂、出问题能快速定位的代码。**

"能跑起来"只是第一步。工程思维关心的是：

1. **一个月后你自己还看得懂吗？**
2. **半夜出 bug 了，能 5 分钟内定位吗？**
3. **加新功能的时候，会不会把旧功能搞坏？**
4. **别人能看懂你的代码结构吗？**

## 你今天学到的 8 个工程思维

### 1. 模块化：一个文件只做一件事

```
❌ 不要：一个 2000 行的 main.py
✅ 要：
   src/news_fetcher.py     ← 只管获取新闻
   src/news_analyzer.py   ← 只管 AI 分析
   src/market_data.py     ← 只管市场行情
   src/report_saver.py    ← 只管保存文件
   src/agent.py           ← 只管协调调度
```

**为什么？** 出 bug 时你立刻知道去哪个文件找。加新功能时你知道该改哪个文件。

### 2. 日志（Debug Print）：每一步都留下痕迹

```python
# 不写日志的代码：
data = fetch_data()
result = process(data)
save(result)
# → 如果中间炸了，你不知道死在哪一步

# 写日志的代码：
print("[DEBUG] 开始获取数据...")
data = fetch_data()
print(f"[DEBUG] 获取到 {len(data)} 条数据")

print("[DEBUG] 开始处理数据...")
result = process(data)
print(f"[DEBUG] 处理完成")

print("[DEBUG] 开始保存...")
save(result)
print("[DEBUG] 保存完成")
# → 看到最后一条日志卡在 "开始处理数据..." 就知道 process() 炸了
```

**关键**：不是所有 print 都是日志。只有"标记关键节点"的 print 才是。

### 3. 异常处理：假设一切都会出错

```python
# ❌ 乐观写法
response = requests.get(url)
data = response.json()
# 万一网络断了呢？万一 API 返回的不是 JSON 呢？

# ✅ 防御性写法
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # 状态码不是 200 就抛异常
    data = response.json()
except requests.Timeout:
    print("请求超时，跳过")
    data = None
except requests.HTTPError as e:
    print(f"API 返回错误: {e}")
    data = None
except Exception as e:
    print(f"未知错误: {e}")
    data = None
```

**原则**：外部依赖（网络、API、文件系统）一定会在某个时刻出问题。你的代码必须能够在出错时"降级运行"而不是直接崩溃。

### 4. 防御性编程：永远不要假设

```python
# ❌ 假设：article 一定有 "source" 键
source = article["source"]["name"]

# ✅ 防御：article["source"] 可能不存在
source = article.get("source", {}).get("name", "未知来源")

# 解释：
# article.get("source", {})
#   → 取 "source" 的值，如果不存在返回空 dict {}
# .get("name", "未知来源")
#   → 从上面的结果取 "name"，如果不存在返回 "未知来源"
```

### 5. 成本意识：AI 调用是按字收费的

```
一条新闻的 AI 分析成本：
  DeepSeek:  ~800 tokens × ¥0.002/1000 ≈ ¥0.0016
  OpenAI:    ~800 tokens × ¥0.02/1000 ≈ ¥0.016 （贵10倍！）
```

工程决策：
- 先用关键词筛选（免费），再送 AI 分析（付费）
- 限制每轮最多分析 5 条（即使有 10 条高分新闻）
- 用便宜的模型（DeepSeek 替代 OpenAI）

### 6. 优雅退出：Ctrl+C 不应该报错

```python
# ❌ 丑陋：Ctrl+C 后满屏红色 Traceback
while True:
    do_work()
    time.sleep(60)

# ✅ 优雅：Ctrl+C 后干净的告别
try:
    while True:
        do_work()
        time.sleep(60)
except KeyboardInterrupt:
    print("用户手动停止，程序正常退出。")
```

### 7. 数据持久化：存下来才有价值

终端打印的结果会在关闭窗口后消失。写到文件的数据会一直存在。

```python
# JSON 文件可以：
# - 被任何编程语言读取
# - 被 Excel 打开（如果是扁平结构）
# - 被搜索引擎索引
# - 被备份到云端
# - 半年后还能查看

with open("data/daily/2026-05-09.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
```

### 8. 可评估性：不知道准确率 = 不敢信任

不管 AI 输出多漂亮，如果不验证准确率，你永远不敢真正依赖它。

```
阶段8 的质量评估系统：
  ① 自动生成待审核文件（data/review/*.json）
  ② 人工逐条打分（review.py）
  ③ 统计正确率（evaluate.py）
  ④ 按情绪维度分析（bullish 的正确率 vs bearish 的正确率）
```

## 工程思维的"检查清单"

每次写完一段代码，问自己：

- [ ] 如果这段代码半夜炸了，我能在 5 分钟内找到原因吗？
- [ ] 一个月后回来，我还能看懂这段代码在做什么吗？
- [ ] 如果 API 返回了意料之外的格式，程序会崩溃还是优雅降级？
- [ ] 关键步骤有没有 print 日志？
- [ ] 外部依赖的调用有没有 try/except？
- [ ] 能不能被 Ctrl+C 优雅地停止？
- [ ] 有价值的数据有没有存到文件里？
