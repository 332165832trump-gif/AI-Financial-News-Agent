"""
AI金融新闻分析Agent - 人工审核工具
阶段8：逐条检查 AI 分析质量

用法：
    python review.py                        # 审核今天的
    python review.py 2026-05-08             # 审核指定日期的
    python review.py --stats                # 只看统计，不审核
"""

import json
import os
import sys
from datetime import datetime


# ============================================================
# 配置
# ============================================================

REVIEW_DIR = "data/review"


# ============================================================
# 第1步：加载审核文件
# ============================================================

def load_review_file(date_str=None):
    """
    加载指定日期的审核文件

    参数:
        date_str: "2026-05-09" 或 None（默认今天）

    返回:
        (review_data, filepath) 或 (None, None)
    """

    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    filepath = os.path.join(REVIEW_DIR, f"review_{date_str}.json")

    if not os.path.exists(filepath):
        print(f"❌ 审核文件不存在: {filepath}")
        print(f"   请先运行 main.py 生成当天的分析结果。")
        # 尝试列出已有的审核文件
        if os.path.exists(REVIEW_DIR):
            files = [f for f in os.listdir(REVIEW_DIR) if f.endswith(".json")]
            if files:
                print(f"\n   已有的审核文件:")
                for f in sorted(files, reverse=True):
                    print(f"     {f}")
        return None, None

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data, filepath


# ============================================================
# 第2步：打印单条待审记录的详情
# ============================================================

def _print_review_item(item, index, total):
    """
    在命令行美观地打印一条待审核记录

    参数:
        item: 审核记录 dict
        index: 当前是第几条
        total: 总共待审核几条
    """

    # 情绪 emoji
    sentiment_map = {
        "bullish": "🟢",
        "bearish": "🔴",
        "neutral": "🟡",
    }
    sentiment_emoji = sentiment_map.get(item.get("sentiment", "neutral"), "⚪")

    print(f"\n{'━'*60}")
    print(f"📋 第 {index}/{total} 条")
    print(f"{'━'*60}")

    # 标题和URL
    print(f"\n📰 新闻标题:")
    print(f"   {item.get('title', 'N/A')}")

    # AI 摘要和判断
    print(f"\n🤖 AI 摘要:")
    print(f"   {item.get('summary', 'N/A')}")

    print(f"\n{sentiment_emoji} AI 情绪判断: {item.get('sentiment', 'N/A').upper()}")

    # 为什么重要
    importance = item.get("importance", "")
    if importance:
        print(f"\n💡 为什么重要:")
        print(f"   {importance}")

    # 影响的资产
    assets = item.get("affected_assets", [])
    if assets:
        print(f"\n🎯 受影响资产: {', '.join(assets)}")

    # 宏观逻辑
    reasoning = item.get("reasoning", "")
    if reasoning:
        print(f"\n🧠 AI 推理:")
        print(f"   {reasoning}")

    # 如果之前已检查过，显示之前的记录
    if item.get("human_check"):
        print(f"\n📌 之前已检查: {item['human_check']}")
        if item.get("human_note"):
            print(f"   备注: {item['human_note']}")

    print(f"\n{'─'*60}")


# ============================================================
# 第3步：交互式审核
# ============================================================

def run_review(date_str=None):
    """
    交互式审核主流程

    用户操作：
      1 = 分析正确
      2 = 存疑
      3 = 分析错误
      4 = 跳过
      q = 退出

    参数:
        date_str: 日期字符串或 None
    """

    data, filepath = load_review_file(date_str)
    if data is None:
        return

    items = data.get("items", [])
    if not items:
        print("⚠️  审核文件为空。")
        return

    # 找出所有待审核的条目（human_check 为 None）
    unchecked_indices = [
        i for i, item in enumerate(items)
        if item.get("human_check") is None
    ]

    if not unchecked_indices:
        print(f"✅ 所有 {len(items)} 条记录都已审核完毕！")
        _print_stats(data)
        return

    # 找出已审核的条目
    checked_indices = [
        i for i, item in enumerate(items)
        if item.get("human_check") is not None
    ]

    print(f"\n{'='*60}")
    print(f"🔍 AI 分析审核工具")
    print(f"   日期: {data.get('date', '?')}")
    print(f"   总计: {len(items)} 条")
    print(f"   已审核: {len(checked_indices)} 条")
    print(f"   待审核: {len(unchecked_indices)} 条")
    print(f"{'='*60}")

    print(f"\n操作说明:")
    print(f"   1 = ✅ 分析正确 (correct)")
    print(f"   2 = ❓ 存疑 (questionable)")
    print(f"   3 = ❌ 分析错误 (wrong)")
    print(f"   4 = ⏭  跳过（不审核，跳到下一条）")
    print(f"   q = 退出（已审核的会自动保存）")
    print()

    # 逐个审核
    for idx in unchecked_indices:
        item = items[idx]

        # 计算显示序号（待审核中的第几条）
        display_index = unchecked_indices.index(idx) + 1
        total_unchecked = len(unchecked_indices)

        # 打印详情
        _print_review_item(item, display_index, total_unchecked)

        # 获取用户输入
        while True:
            choice = input("你的判断 (1=正确 2=存疑 3=错误 4=跳过 q=退出): ").strip().lower()

            if choice == "q":
                print("\n💾 正在保存...")
                _save_review_file(data, filepath)
                print("👋 已退出，已审核的结果不会丢失。")
                return

            if choice in ("1", "2", "3", "4"):
                break

            print("⚠️  请输入 1、2、3、4 或 q")

        # 处理跳过
        if choice == "4":
            print("   ⏭  已跳过")
            # 不给 human_check 赋值，保持 None，下次还会出现
            continue

        # 映射选择到标签
        label_map = {"1": "correct", "2": "questionable", "3": "wrong"}
        human_check = label_map[choice]

        # 获取备注
        note = input("备注（可选，直接回车跳过）: ").strip()

        # 更新记录
        items[idx]["human_check"] = human_check
        items[idx]["human_note"] = note
        items[idx]["checked_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 每审核一条就保存（防止意外退出丢失进度）
        _save_review_file(data, filepath)

        print(f"   💾 已保存 ({human_check})\n")

    # 全部审核完毕
    print(f"\n🎉 全部审核完毕！")
    _print_stats(data)


# ============================================================
# 第4步：保存审核结果
# ============================================================

def _save_review_file(data, filepath):
    """
    保存审核文件（更新统计数字）

    参数:
        data: 审核数据 dict
        filepath: 文件路径
    """

    items = data.get("items", [])
    data["checked"] = sum(1 for i in items if i["human_check"] is not None)
    data["unchecked"] = sum(1 for i in items if i["human_check"] is None)

    os.makedirs(REVIEW_DIR, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# 第5步：打印统计信息
# ============================================================

def _print_stats(data):
    """
    打印审核统计

    参数:
        data: 审核数据 dict
    """

    items = data.get("items", [])
    total = len(items)
    correct = sum(1 for i in items if i.get("human_check") == "correct")
    questionable = sum(1 for i in items if i.get("human_check") == "questionable")
    wrong = sum(1 for i in items if i.get("human_check") == "wrong")
    unchecked = sum(1 for i in items if i.get("human_check") is None)
    checked = correct + questionable + wrong

    print(f"\n{'='*60}")
    print(f"📊 审核统计 - {data.get('date', '?')}")
    print(f"{'='*60}")
    print(f"   总计:     {total}")
    print(f"   已审核:   {checked}")
    print(f"   正确:     {correct}")
    print(f"   存疑:     {questionable}")
    print(f"   错误:     {wrong}")
    print(f"   未审核:   {unchecked}")

    if checked > 0:
        rate = correct / checked * 100
        print(f"   正确率:   {rate:.1f}%")
    print(f"{'='*60}")


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":

    # 解析命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == "--stats":
            # 只显示统计，不审核
            data, filepath = load_review_file()
            if data:
                _print_stats(data)
            sys.exit(0)

        # 指定日期
        date_str = arg
    else:
        date_str = None

    run_review(date_str)
