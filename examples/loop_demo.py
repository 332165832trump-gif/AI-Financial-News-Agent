"""
Demo 3：while 循环和 time.sleep() 到底在做什么
适合 Python 初学者的最小可运行示例

运行：
    python examples/loop_demo.py

这个脚本只讲：
  1. for 循环：遍历列表
  2. while True：无限循环
  3. time.sleep()：暂停
  4. try/except：捕获 Ctrl+C
"""

import time

print("=" * 60)
print("循环和暂停")
print("=" * 60)

# ============================================================
# 第1部分：for 循环 —— 遍历列表中的每个元素
# ============================================================
print("\n【for 循环：一条一条处理】")
print("─" * 40)

# 准备一个列表（list）
news_titles = ["Nvidia股价大涨", "美联储降息", "黄金涨至新高"]

print(f"news_titles 是一个列表: {news_titles}")
print(f"列表长度: {len(news_titles)} 条\n")

# for 循环：每次从列表中取出一个元素，赋给变量 title
for i, title in enumerate(news_titles, start=1):
    # enumerate(列表, start=1) = 同时给出 序号 和 内容
    # i = 第几条（从1开始）
    # title = 列表中的元素
    print(f"  处理第 {i} 条: {title}")

# ============================================================
# 第2部分：while True —— 无限循环
# ============================================================
print("\n【while True：不停重复】")
print("─" * 40)

print("下面这个循环每 2 秒打印一次，按 Ctrl+C 停止。")

# run_count = 记录运行了多少次
# 每次循环 run_count += 1（run_count = run_count + 1 的缩写）
run_count = 0

try:
    while True:
        run_count = run_count + 1         # 计数器+1
        print(f"\n  第 {run_count} 次循环")
        print(f"  当前时间: {time.strftime('%H:%M:%S')}")

        # time.sleep(秒数) = 暂停
        # 程序在这里"睡着"，不占 CPU，等指定秒数后再醒来继续
        print(f"  暂停 2 秒...")
        time.sleep(2)

except KeyboardInterrupt:
    # KeyboardInterrupt 是用户按 Ctrl+C 时触发的"信号"
    # except 捕获这个信号，执行下面的代码，而不是直接报错退出
    print(f"\n\n{'─'*40}")
    print(f"检测到 Ctrl+C！")
    print(f"共运行了 {run_count} 次")
    print(f"优雅退出，没有任何报错。")
    print(f"{'─'*40}")

# ============================================================
# 第3部分：演示"不用 try/except 会怎样"
# ============================================================
print("\n【对比：不处理 Ctrl+C 会怎样？】")
print("─" * 40)

print("""
如果代码是这样写的：

    while True:
        print("运行中...")
        time.sleep(2)

你按 Ctrl+C 后会看到这样的红字报错：

    Traceback (most recent call last):
      File "xxx.py", line 5, in <module>
        time.sleep(2)
    KeyboardInterrupt

虽然程序也停了，但给人一种"出错了"的感觉。
工程上，我们希望在用户 Ctrl+C 时"干净地告别"。
""")

print("=" * 60)
print("总结：")
print("  for 循环：知道要跑多少次 → 遍历列表")
print("  while True：不知道要跑多少次 → 一直跑到被叫停")
print("  time.sleep(n)：暂停 n 秒 → 控制节奏")
print("  try/except KeyboardInterrupt：优雅退出 → 不乱报错")
print("=" * 60)
