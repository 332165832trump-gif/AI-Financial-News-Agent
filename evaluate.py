"""
AI金融新闻分析Agent - 评估统计工具
阶段8：统计 AI 分析准确率

用法：
    python evaluate.py              # 统计所有日期
    python evaluate.py --detail     # 显示每条错误记录
"""

import json
import os
import sys
from collections import Counter


# ============================================================
# 配置
# ============================================================

REVIEW_DIR = "data/review"


# ============================================================
# 第1步：加载所有审核文件
# ============================================================

def load_all_review_files():
    """
    扫描 data/review/ 目录，加载所有审核 JSON 文件

    返回:
        列表，每个元素是 (日期字符串, 审核数据 dict)
        按日期倒序排列（最新的在前）
    """

    if not os.path.exists(REVIEW_DIR):
        print(f"❌ 审核目录不存在: {REVIEW_DIR}")
        return []

    all_files = []
    for filename in os.listdir(REVIEW_DIR):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(REVIEW_DIR, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            date_str = data.get("date", filename.replace("review_", "").replace(".json", ""))
            all_files.append((date_str, data))

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️  跳过损坏文件 {filename}: {e}")

    # 按日期倒序
    all_files.sort(key=lambda x: x[0], reverse=True)
    return all_files


# ============================================================
# 第2步：统计汇总
# ============================================================

def compute_stats(all_files):
    """
    从所有审核文件中汇总统计数据

    返回:
        stats dict
    """

    # 全局计数器
    total_items = 0
    total_checked = 0
    total_correct = 0
    total_questionable = 0
    total_wrong = 0
    total_unchecked = 0

    # 按天明细
    daily_stats = []

    # 所有备注（用于分析常见问题）
    all_notes = []
    wrong_items = []

    # 按情绪统计正确率
    sentiment_stats = {}  # {"bullish": {"total": 5, "correct": 3}, ...}

    for date_str, data in all_files:
        items = data.get("items", [])

        day_correct = 0
        day_questionable = 0
        day_wrong = 0
        day_unchecked = 0

        for item in items:
            total_items += 1
            check = item.get("human_check")

            if check is None:
                day_unchecked += 1
                total_unchecked += 1
                continue

            total_checked += 1

            if check == "correct":
                day_correct += 1
                total_correct += 1
            elif check == "questionable":
                day_questionable += 1
                total_questionable += 1
            elif check == "wrong":
                day_wrong += 1
                total_wrong += 1

            # 按情绪统计
            sentiment = item.get("sentiment", "unknown")
            if sentiment not in sentiment_stats:
                sentiment_stats[sentiment] = {"total": 0, "correct": 0, "wrong": 0,
                                              "questionable": 0}
            sentiment_stats[sentiment]["total"] += 1
            if check == "correct":
                sentiment_stats[sentiment]["correct"] += 1
            elif check == "wrong":
                sentiment_stats[sentiment]["wrong"] += 1
            elif check == "questionable":
                sentiment_stats[sentiment]["questionable"] += 1

            # 收集备注
            note = item.get("human_note", "").strip()
            if note:
                all_notes.append(note)

            # 收集错误条目
            if check in ("wrong", "questionable"):
                wrong_items.append({
                    "date": date_str,
                    "title": item.get("title", ""),
                    "ai_sentiment": sentiment,
                    "human_check": check,
                    "note": note,
                    "ai_summary": item.get("summary", ""),
                })

        day_checked = day_correct + day_questionable + day_wrong
        day_rate = (day_correct / day_checked * 100) if day_checked > 0 else 0

        daily_stats.append({
            "date": date_str,
            "total": len(items),
            "checked": day_checked,
            "correct": day_correct,
            "questionable": day_questionable,
            "wrong": day_wrong,
            "unchecked": day_unchecked,
            "correct_rate": day_rate,
        })

    # 整体正确率
    overall_rate = (total_correct / total_checked * 100) if total_checked > 0 else 0

    # 最常见的备注（top 5）
    note_counter = Counter(all_notes)
    top_notes = note_counter.most_common(5)

    return {
        "total_items": total_items,
        "total_checked": total_checked,
        "total_correct": total_correct,
        "total_questionable": total_questionable,
        "total_wrong": total_wrong,
        "total_unchecked": total_unchecked,
        "overall_correct_rate": overall_rate,
        "daily_stats": daily_stats,
        "sentiment_stats": sentiment_stats,
        "top_notes": top_notes,
        "wrong_items": wrong_items,
    }


# ============================================================
# 第3步：打印统计报告
# ============================================================

def print_evaluation_report(stats, show_detail=False):
    """
    打印评估报告

    参数:
        stats: compute_stats() 的返回值
        show_detail: 是否显示每条错误详情
    """

    print(f"\n{'='*60}")
    print(f"📊 AI金融新闻分析 - 质量评估报告")
    print(f"{'='*60}")

    # 汇总
    print(f"\n📈 汇总统计:")
    print(f"   {'─'*40}")
    print(f"   总分析数:    {stats['total_items']}")
    print(f"   已审核数:    {stats['total_checked']}")
    print(f"   未审核数:    {stats['total_unchecked']}")
    print(f"   {'─'*40}")
    print(f"   ✅ 正确:     {stats['total_correct']}")
    print(f"   ❓ 存疑:     {stats['total_questionable']}")
    print(f"   ❌ 错误:     {stats['total_wrong']}")
    print(f"   {'─'*40}")
    print(f"   🎯 正确率:   {stats['overall_correct_rate']:.1f}%")
    print(f"   {'─'*40}")

    if stats["total_checked"] == 0:
        print(f"\n⚠️  还没有审核过任何记录，请先运行 review.py")
        return

    # 按情绪统计
    print(f"\n📊 按情绪分类的正确率:")
    print(f"   {'情绪':<12} {'总数':>5} {'正确':>5} {'错误':>5} {'正确率':>8}")
    print(f"   {'─'*40}")
    for sentiment, data in sorted(stats["sentiment_stats"].items()):
        total = data["total"]
        if total == 0:
            continue
        rate = data["correct"] / total * 100
        print(f"   {sentiment:<12} {total:>5} {data['correct']:>5} "
              f"{data['wrong']:>5} {rate:>7.1f}%")

    # 按天统计
    if len(stats["daily_stats"]) > 1:
        print(f"\n📅 按日期统计:")
        print(f"   {'日期':<12} {'总':>4} {'正确':>4} {'存疑':>4} {'错误':>4} {'正确率':>8}")
        print(f"   {'─'*45}")
        for day in stats["daily_stats"]:
            print(f"   {day['date']:<12} {day['total']:>4} {day['correct']:>4} "
                  f"{day['questionable']:>4} {day['wrong']:>4} "
                  f"{day['correct_rate']:>7.1f}%")

    # 常见问题备注
    if stats["top_notes"]:
        print(f"\n💬 最常见的审核备注:")
        for note, count in stats["top_notes"]:
            print(f"   [{count}次] {note}")

    # 详情模式：显示每条错误/存疑
    if show_detail and stats["wrong_items"]:
        print(f"\n📋 错误和存疑记录详情:")
        print(f"   {'─'*50}")
        for i, item in enumerate(stats["wrong_items"], 1):
            label = "❌" if item["human_check"] == "wrong" else "❓"
            print(f"\n   {label} [{i}] {item['date']}")
            print(f"      标题: {item['title'][:60]}")
            print(f"      AI判断: {item['ai_sentiment']} → 人工: {item['human_check']}")
            if item["note"]:
                print(f"      备注: {item['note']}")

    print(f"\n{'='*60}")


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":

    show_detail = "--detail" in sys.argv

    all_files = load_all_review_files()

    if not all_files:
        print("⚠️  没有找到任何审核文件。")
        print("   请先运行 review.py 对分析结果进行审核。")
        sys.exit(0)

    print(f"\n📂 找到 {len(all_files)} 个审核文件")

    stats = compute_stats(all_files)
    print_evaluation_report(stats, show_detail=show_detail)
