"""
AI金融新闻分析Agent - 主入口
阶段7：真正的 Agent（观察→判断→决策→行动）
"""

import time
from src.agent import run_agent_cycle

# ============================================================
# 配置
# ============================================================
LOOP_INTERVAL_SECONDS = 60 * 30   # 30分钟
# LOOP_INTERVAL_SECONDS = 10      # 测试用


# ============================================================
# Agent 主循环
# ============================================================
if __name__ == "__main__":

    run_count = 0
    analyzed_urls = set()  # 去重集合：记住今天分析过哪些 URL

    print("=" * 60)
    print("🤖 AI金融新闻分析 Agent - Phase 7")
    print("   Agent循环: Observe → Think → Decide → Act")
    print(f"   每 {LOOP_INTERVAL_SECONDS // 60} 分钟自动运行一次")
    print("   按 Ctrl+C 停止")
    print("=" * 60)

    try:
        while True:
            run_count += 1

            # 执行一次 Agent 循环
            results, analyzed_urls, briefing = run_agent_cycle(
                run_count, analyzed_urls
            )

            print(f"\n⏰ Agent #{run_count} 完成")
            print(f"   已分析 URL 数: {len(analyzed_urls)}")
            print(f"⏳ 下次运行：{LOOP_INTERVAL_SECONDS // 60} 分钟后...")
            print(f"   （按 Ctrl+C 停止）")

            time.sleep(LOOP_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print(f"👋 Agent 已停止。共运行 {run_count} 次。")
        print(f"   日报: data/daily/")
        print(f"   简报: data/briefings/")
        print("=" * 60)
