# 07 - 常见错误和工程教训

## 你今天实际遇到的错误

### 错误1：`__init__.py` 文件内容写错

**错误现象**
```
NameError: name '__init__' is not defined
```

**根本原因**
`__init__.py` 的内容被写成了 `__init__.py` 这几个字，Python 当成代码执行。

**正确写法**
```python
# __init__.py 的内容：空文件或只有注释
# 作用：告诉 Python "这个文件夹是一个包"
```

**教训**：工具的"约定文件"（如 `__init__.py`、`.env`、`.gitignore`）内容有固定格式，不能随便写。

---

## 工程中一定会遇到的错误（及其教训）

### 错误2：`NameError: name 'xxx' is not defined`

**错误现象**
```
Traceback (most recent call last):
  File "test.py", line 3, in <module>
    result = add(15)
NameError: name 'add' is not defined
```

**根本原因**
你在调用 `add(15)`，但 Python 在当前位置找不到 `add` 这个函数。可能的原因：
1. 函数定义在调用之后（Python 从上往下执行）
2. 函数定义在别的文件里但没有 import
3. 函数名拼写错了

**如何 debug**
1. 检查函数名拼写
2. 检查函数定义的位置：必须在调用之前
3. 如果函数在别的文件：确认有 `from xxx import add`

**正确写法**
```python
# ✅ 定义在前，调用在后
def add(n):
    return n + 1

result = add(15)  # 正确

# ❌ 调用在前，定义在后
result = add(15)  # 报错！
def add(n):
    return n + 1
```

---

### 错误3：`NameError: page is not defined`

**错误现象**
在一个函数里想用 `page` 变量，但 Python 说找不到。

**根本原因：变量作用域**

```python
page = None  # 这是全局变量

def init_browser():
    page = "浏览器页面"  # 这是局部变量！！！和上面的 page 不是同一个

init_browser()
print(page)  # 输出：None（不是 "浏览器页面"！）
```

**为什么**：函数内部的变量默认是"局部"的（private），只在函数内部有效。外部看不到。

**正确写法1：用 return 传递**
```python
def init_browser():
    page = "浏览器页面"
    return page  # ← 把值传出去

page = init_browser()  # ← 接收返回值
print(page)  # "浏览器页面" ✅
```

**正确写法2：用 global 关键字（不推荐初学者）**
```python
def init_browser():
    global page  # ← 声明"我要用外面的 page"
    page = "浏览器页面"
```

**教训**：函数里的变量和函数外的变量是"两个世界"。想传递数据，用 `return`，不要依赖全局变量。

---

### 错误4：iframe 找不到元素

**错误现象**
页面看起来加载完了，但代码找不到 iframe 里的元素。

**根本原因**
HTML 的 `<iframe>` 是一个"页面里的页面"。如果你不先切换到 iframe 里，代码只能看到"外层页面"，看不到"内层页面"里的元素。

**正确做法（Playwright 示例）**
```python
# ❌ 错误：直接在页面上找 iframe 里的元素
page.click("#button-inside-iframe")  # 找不到！

# ✅ 正确：先切换到 iframe，再操作
frame = page.frame_locator("#my-iframe")
frame.click("#button-inside-iframe")  # 找到了
```

---

### 错误5：页面"看起来加载完了"但代码还不能运行

**错误现象**
浏览器显示页面已经完整了，但代码执行到一半就报错"元素找不到"。

**根本原因**
"浏览器渲染完"和"所有 JS 执行完"是两件不同的事情。页面可能还有一些 JavaScript 在后台加载数据、渲染组件，这时候 DOM 还没完全稳定。

**正确做法**
```python
# ❌ 不可靠：固定等 3 秒
time.sleep(3)

# ✅ 可靠：等待特定元素出现
page.wait_for_selector("#stock-price", timeout=10000)
# 含义：等待 #stock-price 这个元素出现，最多等 10 秒
```

**教训**：`time.sleep()` 是"瞎等"，`wait_for_selector()` 是"等到真的准备好了"。永远优先用后者。

---

### 错误6：为什么不能乱用 sleep

```python
# ❌ 坏习惯
time.sleep(3)  # 永远等 3 秒
# 问题：
#   网络快的时候 → 浪费 2.5 秒
#   网络慢的时候 → 还是不够，仍然会报错

# ✅ 好习惯
page.wait_for_selector("#content", timeout=10000)
# 含义：等 #content 出现，出现了立即继续，10 秒还不出现才报错
```

---

### 错误7：`except: pass` 很危险

```python
# ❌ 危险写法
try:
    result = some_risky_operation()
except:
    pass  # 默默地吞掉所有错误

# 后果：
#   你不知道出错了
#   你不知道哪里出错了
#   你不知道为什么出错
#   程序悄悄地坏掉了
```

**正确写法**
```python
# ✅ 至少打印一下
try:
    result = some_risky_operation()
except Exception as e:
    print(f"⚠️ 操作失败: {type(e).__name__} - {e}")
    result = None  # 明确设置默认值

# ✅ 更好的：捕获具体异常类型
try:
    result = requests.get(url)
except requests.ConnectionError:
    print("网络连接失败，请检查网络")
except requests.Timeout:
    print("请求超时，服务器响应太慢")
except Exception as e:
    print(f"未知错误: {e}")
```

**教训**：
1. **永远不要 `except: pass`** — 这是在假装错误不存在
2. **至少 `print(f"出错: {e}")`** — 留下痕迹
3. **最好捕获具体异常类型** — 不同错误不同处理

---

## 错误速查表

| 错误类型 | 常见原因 | 第一反应 |
|----------|----------|----------|
| `NameError` | 变量/函数名拼错，或没 import | 检查拼写和 import |
| `TypeError` | 类型用错了（如对 str 用 [0]） | `print(type(x))` |
| `KeyError` | 字典里没有这个键 | 用 `.get()` 替代 `[]` |
| `IndexError` | 列表索引超出范围 | `print(len(L))` |
| `AttributeError` | 对象没有这个方法 | `print(dir(obj))` |
| `JSONDecodeError` | JSON 格式不合法 | 打印原始文本看看 |
| `ConnectionError` | 网络不通 | 检查网络/URL |
| `KeyboardInterrupt` | 用户按了 Ctrl+C | 用 `except KeyboardInterrupt` 处理 |
