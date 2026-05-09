"""
日报保存模块 - 阶段5
功能：把分析结果保存为 JSON 文件，按日期组织
"""

import os
import json
from datetime import datetime


# ============================================================
# 第1步：生成文件名
# ============================================================

def _get_today_filename():
    """
    根据今天的日期生成文件名

    例如：2026-05-09.json

    datetime.now() — 获取当前日期时间
    .strftime("格式") — 把日期格式化成字符串
      %Y = 年份4位 (2026)
      %m = 月份2位 (05)
      %d = 日期2位 (09)

    返回格式：(文件路径, 日期字符串)
    """
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")           # "2026-05-09"
    timestamp = today.strftime("%Y-%m-%d %H:%M:%S") # "2026-05-09 16:30:00"

    # 文件路径：data/daily/2026-05-09.json
    # os.path.join() — 自动用正确的斜杠拼接路径（Windows用\，Mac/Linux用/）
    filename = os.path.join("data", "daily", f"{date_str}.json")

    return filename, date_str, timestamp


# ============================================================
# 第2步：构建日报数据结构
# ============================================================

def _build_report(results, news_count, date_str, timestamp):
    """
    把分析结果打包成一个"日报"dict

    参数:
        results: 分析结果列表 [{"article": {...}, "analysis": {...}}, ...]
        news_count: 总共获取了多少条新闻
        date_str: 日期字符串 "2026-05-09"
        timestamp: 时间戳 "2026-05-09 16:30:00"

    返回:
        日报 dict
    """

    # 这个 dict 就是最终存到文件里的内容
    # 设计原则：顶层放"元信息"，analyses 放具体内容
    report = {
        "date": date_str,
        "generated_at": timestamp,
        "total_news_fetched": news_count,
        "total_analyzed": len(results),
        "analyses": []        # 空列表，后面逐个填充
    }

    # 遍历每条分析结果，精简后放入日报
    for item in results:
        article = item["article"]
        analysis = item["analysis"]

        # 只保留有用的字段，不存全部（节省空间）
        record = {
            "title": article.get("title", ""),
            "source": article.get("source", {}).get("name", ""),
            "url": article.get("url", ""),
            "published_at": article.get("publishedAt", ""),
            "analysis": analysis    # 这就是阶段3产出的 JSON dict
        }
        report["analyses"].append(record)

    return report


# ============================================================
# 第3步：读取已有日报（如果今天存过就合并）
# ============================================================

def _load_existing_report(filepath):
    """
    读取今天已经保存过的日报文件

    如果文件存在 → 读取并返回
    如果文件不存在 → 返回 None
    """

    # os.path.exists(路径) — 检查文件是否存在
    if not os.path.exists(filepath):
        print(f"[DEBUG] 今天还没有日报文件，将创建新文件")
        return None

    try:
        # with open(路径, 模式, 编码) as f:
        #   "r" = read（只读模式）
        #   encoding="utf-8" = 用 UTF-8 编码读（处理中文必备）
        with open(filepath, "r", encoding="utf-8") as f:
            # json.load() — 从文件对象直接解析 JSON（注意不是 loads！）
            # json.loads() = 从字符串解析
            # json.load()  = 从文件对象解析
            existing = json.load(f)

        print(f"[DEBUG] 读取已有日报：{len(existing.get('analyses', []))} 条旧分析")
        return existing

    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"[DEBUG] ⚠️ 读取已有日报失败: {e}，将创建新文件")
        return None


# ============================================================
# 第4步：保存日报（核心函数）
# ============================================================

def save_daily_report(results, news_count=10):
    """
    把分析结果保存到 data/daily/YYYY-MM-DD.json

    参数:
        results: 分析结果列表（来自 news_analyzer.run()）
        news_count: 总共抓了多少条新闻

    返回:
        保存的文件路径
    """

    if not results:
        print("⚠️  没有分析结果，跳过保存。")
        return None

    # 生成文件名和日期
    filepath, date_str, timestamp = _get_today_filename()
    print(f"\n[DEBUG] 日报文件路径: {filepath}")

    # 确保 data/daily/ 文件夹存在
    # os.makedirs(路径, exist_ok=True)
    #   — 创建文件夹（如果父文件夹不存在也会自动创建）
    #   — exist_ok=True 表示如果已存在不报错
    data_dir = os.path.join("data", "daily")
    os.makedirs(data_dir, exist_ok=True)

    # 读取已有日报（如果今天多次运行，会合并结果）
    existing = _load_existing_report(filepath)

    if existing:
        # 已有日报：把新分析追加进去（而不是覆盖）
        old_analyses = existing.get("analyses", [])

        # 构建新日报，合并 old + new
        report = _build_report(results, news_count, date_str, timestamp)

        # 【注意】这里用旧的总数，因为今天可能跑过多次
        report["total_news_fetched"] = existing.get("total_news_fetched", 0) + news_count
        report["total_analyzed"] = len(old_analyses) + len(report["analyses"])

        # 把旧分析放到新分析前面
        report["analyses"] = old_analyses + report["analyses"]

        print(f"[DEBUG] 合并旧日报：{len(old_analyses)} 条 + 新增 {len(results)} 条")
    else:
        # 新日报：直接构建
        report = _build_report(results, news_count, date_str, timestamp)

    # =====================================
    # 写文件（整个阶段5最核心的2行！）
    # =====================================
    with open(filepath, "w", encoding="utf-8") as f:
        # json.dump() — 把 Python 对象写入文件
        #   ensure_ascii=False — 不把中文转成 \uXXXX 编码（关键！）
        #   indent=2 — 每层缩进2个空格，让 JSON 文件人类也可读
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"💾 日报已保存: {filepath}")
    print(f"   共 {report['total_analyzed']} 条分析，"
          f"文件大小约 {os.path.getsize(filepath)} 字节")

    return filepath


# ============================================================
# 第5步：打印文件内容（用于验证）
# ============================================================

def preview_file(filepath, max_lines=20):
    """
    快速预览保存的文件内容（验证用）

    参数:
        filepath: 文件路径
        max_lines: 最多显示多少行
    """
    if not filepath or not os.path.exists(filepath):
        print("⚠️  文件不存在，无法预览。")
        return

    print(f"\n📄 文件前 {max_lines} 行预览:")
    print("-" * 40)

    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            if i > max_lines:
                print(f"... (剩余内容省略)")
                break
            # .rstrip() — 去掉行尾的换行符
            print(f"{i:>3}| {line.rstrip()}")
