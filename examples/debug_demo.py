"""
Demo 4：Debug 的方法和思维
适合 Python 初学者的最小可运行示例

运行：
    python examples/debug_demo.py

这个脚本展示 4 种 debug 方法：
  1. print 调试（最基础、最常用）
  2. 看变量的类型
  3. 看变量的内容
  4. 定位"在哪一行死了"
"""

print("=" * 60)
print("Debug 工具箱")
print("=" * 60)

# ============================================================
# 方法1：print 调试 —— 看程序跑到哪了
# ============================================================
print("\n【方法1：print 看流程】")
print("─" * 40)

print("步骤A：开始处理数据")
# 假设这里有一些复杂逻辑...
print("步骤B：数据清洗完成")
# 又一些逻辑...
print("步骤C：正在调用 API...")
print("步骤D：API 返回结果")

print("""
如果程序在某一步卡住了：
  → 看最后一条 print 是哪个步骤
  → 就知道死在 "步骤C" 和 "步骤D" 之间
  → 问题出在 API 调用那里

这就是 print 调试的价值：
  不是随便打印，而是"在关键节点埋下标记"。
""")

# ============================================================
# 方法2：看变量的类型
# ============================================================
print("─" * 40)
print("\n【方法2：type() 看类型】")
print("─" * 40)

# 一堆不知道类型的变量
a = {"name": "张三"}
b = ["苹果", "香蕉"]
c = "hello"
d = 42
e = None

variables = [a, b, c, d, e]
names = ["a", "b", "c", "d", "e"]

for name, var in zip(names, variables):
    print(f"  {name} = {str(var)[:30]:<30} 类型: {type(var).__name__}")

print(f"\n为什么 type() 很重要？")
print(f"  因为不同操作需要不同类型:")
print(f"  dict 可以用 ['key'] 取值，list 用 [0]，str 不能")
print(f"  如果搞错类型，Python 会报 TypeError")

# ============================================================
# 方法3：看变量的内容
# ============================================================
print(f"\n{'─'*40}")
print("\n【方法3：看变量的内容】")
print("─" * 40)

# 假设你从 API 拿到了一个复杂的数据结构
complex_data = {
    "status": "ok",
    "count": 150,
    "results": [
        {"id": 1, "name": "项目A", "score": 95},
        {"id": 2, "name": "项目B", "score": 88},
    ],
    "metadata": {
        "page": 1,
        "total_pages": 15
    }
}

# 方法3a：看"顶层有哪些键"
print(f"\n顶层有哪些键: {list(complex_data.keys())}")

# 方法3b：看每个键对应的值是什么类型
print(f"\n每个键的类型:")
for key in complex_data:
    print(f"  complex_data['{key}'] → {type(complex_data[key]).__name__}")

# 方法3c：看列表的长度
results = complex_data.get("results", [])
print(f"\nresults 列表长度: {len(results)}")

# 方法3d：看列表的第一个元素
if results:
    print(f"\nresults[0] 的内容:")
    print(f"  {results[0]}")

print(f"\n调试口诀:")
print(f"  不知道变量的结构 → 先用 .keys() 看有哪些键")
print(f"  不知道值的类型   → 先用 type() 看")
print(f"  不知道列表的内容 → 先看 len()，再看第一个元素")

# ============================================================
# 方法4：定位"在哪一行死了"
# ============================================================
print(f"\n{'─'*40}")
print("\n【方法4：读错误信息】")
print("─" * 40)

# 这段代码故意写了一个错误，然后用 try/except 捕获
# 正常开发中你不需要这样写，这里只是教学演示
try:
    data = {"name": "张三"}
    # 下一行故意写错：访问不存在的 key
    value = data["不存在的键"]
except KeyError as e:
    print(f"[X] 发生了错误: {type(e).__name__}")
    print(f"   错误信息: {e}")
    print(f"")
    print(f"如果是真实的 Traceback，你会看到：")
    print(f"")
    print(f"  Traceback (most recent call last):")
    print(f"    File 'xxx.py', line 53, in <module>")
    print(f"      value = data['不存在的键']")
    print(f"  KeyError: '不存在的键'")
    print(f"")
    print(f"读法（从下往上）：")
    print(f"  1. 最后一行: KeyError → 错误类型")
    print(f"  2. 倒数第二行: value = data['不存在的键'] → 具体哪行代码出错")
    print(f"  3. 继续往上: 函数调用链")

print(f"\n{'─'*40}")
print("\nDebug 三个原则：")
print("  1. print 不是随便用，而是在关键节点埋标记")
print("  2. 遇到变量先看类型 (type) 和内容 (print/keys/len)")
print("  3. 读报错从下往上：错误类型 → 出错行号 → 调用链")
print(f"{'─'*40}")
