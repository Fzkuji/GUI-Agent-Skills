# Agentic Programming：把 LLM 当 CPU 用的编程范式

> 一句话：MCP 让 LLM 能调 Python 函数，我们让 Python 能调 LLM 函数。方向反过来了。

## 你遇到过这些问题吗？

用 LLM 做 agent 的时候，你可能会这样写：

```python
while not done:
    response = llm.chat([
        system_prompt,           # 越来越长
        *all_previous_messages,  # 越来越长
        "请观察屏幕并点击登录按钮"
    ])
    # 解析 response... 格式不对怎么办？
    # 执行动作... 失败了怎么办？
    # 继续循环... 上下文爆炸了怎么办？
```

问题很多：上下文无限增长、输出格式不可靠、没有隔离、没有复用。

但仔细想想，你写 Python 的时候有这些问题吗？没有。因为 Python 有函数、有类型、有作用域。

**那为什么不把这些概念搬到 LLM 上呢？**

## 核心类比

```
传统编程                        Agentic Programming
───────────                    ────────────────────
CPU 执行代码                    LLM 执行指令
函数体 = Python 代码            函数体 = 自然语言（docstring）
类型签名                        return_type（Pydantic model）
result = fn(args)              result = fn(session, args)
标准库                          内置函数（ask, extract, classify...）
if / for / while               同样的 Python 控制流
```

**没有额外的 Runtime、Workflow、Pipeline 类。LLM 就是 runtime。**

## 看起来是什么样的

```python
from harness import function, Session
from pydantic import BaseModel

# 定义返回类型——LLM 必须返回这个格式
class ObserveResult(BaseModel):
    elements: list[str]
    target_visible: bool

# 定义函数——docstring 就是发给 LLM 的 prompt
# 改 docstring = 改功能
@function(return_type=ObserveResult)
def observe(session: Session, task: str):
    """看屏幕，找到所有可见的按钮和输入框。
    检查 task 描述的目标是否在屏幕上。
    列出你能看到的每一个交互元素。"""

# 调用——跟普通函数一模一样
session = ClaudeCodeSession(model="sonnet")
result = observe(session, task="找到登录按钮")

print(result.elements)        # ["登录按钮", "用户名输入框", ...]
print(result.target_visible)  # True
```

就这么多。装饰器帮你：组装 prompt → 发给 LLM → 解析 JSON → 校验类型 → 失败重试 → 返回保证格式的结果。

## 跟现有方案的区别

### vs MCP（Model Context Protocol）

**MCP：LLM 调 Python**

```
LLM 决定调什么 → get_weather(city="北京") → Python 执行 → 结果回 LLM
```

函数里面是 Python 代码，由 CPU 执行。LLM 只是调用者。

**Agentic Programming：Python 调 LLM**

```
Python 决定调什么 → observe(session, task="...") → LLM 执行 → 结果回 Python
```

函数里面是自然语言，由 LLM 执行。Python 只是调用者。

**方向完全反过来了：**

```
MCP:                给 LLM 加了「手」（能操作外部工具）
Agentic Programming: 给 Python 加了「脑」（能调用 LLM 思考）
```

两者不冲突，可以组合。我们的函数可以被包装成 MCP 工具，也可以在内部调 MCP 工具。

### vs Pydantic AI / LangChain

| | Pydantic AI | LangChain | Agentic Programming |
|---|---|---|---|
| 方向 | LLM → Python | LLM → Python | Python → LLM |
| 谁控制流程 | LLM 决定调什么 tool | LLM + Chain | Python 代码 |
| 函数里面是 | Python 代码 | Python 代码 | 自然语言 |
| 上下文管理 | 一个大对话 | 一个大对话 | Scope（精确控制） |
| 适合 | 数据查询、API 调用 | 各种 | 推理、感知、分析 |

## 两层 Session 设计

实际做 agent 时，一个关键问题是**上下文管理**。如果所有细节都堆在一个对话里，context 会爆炸。

我们的方案：**Programmer Session + Worker Sessions**

```
Programmer Session（编排者，知道全局但不知道细节）
  │
  │ 只看到: "observe 返回: Discord, #常规, 目标找到"
  │ 不看到: 77条OCR文字、156个检测元素、LLM推理过程
  │
  ├── observe() → Worker Session A
  │     完整上下文：OCR + 检测器 + 截图 + 推理
  │     执行完销毁，只有结果存活
  │
  ├── act() → Worker Session B
  │     完整上下文：坐标匹配 + 模板 + 截图
  │     执行完销毁
  │
  └── verify() → Worker Session C
        执行完销毁
```

Programmer 的上下文增长极慢（每步只加一行摘要），Worker 的上下文在函数结束后释放。这就像 Python 函数的局部变量——函数返回后，局部变量消失，只有返回值保留。

## Scope：LLM 版的变量作用域

Python 有 LEGB 作用域规则，我们有 Scope：

```python
from harness import Scope

# 完全隔离——每次调用都是全新的
Scope.isolated()

# 看到同级函数的输入输出
Scope.chained()

# 看到所有：完整调用栈 + 同级推理过程
Scope.full()

# 自定义
Scope(depth=2, peer="io", compact=True)
```

不同类型的 Session 自动处理 Scope：
- **API Session**（Anthropic/OpenAI）：注入上下文到 history，可以压缩
- **CLI Session**（Claude Code/Codex）：自带记忆，compact 时 fork 新 session

Session 自己决定怎么处理 Scope，不需要 if/else——多态。

## 实际效果

我们在 GUI 桌面自动化上验证了这个范式：

```python
# 低层函数（Python 确定性操作）
shot = take_screenshot()           # 截图
ocr = run_ocr(shot.path)           # OCR：77 个文字元素
det = detect_all(shot.path)        # GPA-GUI-Detector：106 个 UI 元素
click(500, 300)                    # 点击

# 高层函数（Python 准备数据 → LLM 推理 → Python 执行）
result = observe(session, task="找登录按钮")
# 内部：截图 → OCR → 检测 → 注入到 prompt → LLM 分析 → 结构化结果

result = act(session, action="click", target="登录按钮")
# 内部：OCR + 模板匹配 → LLM 找坐标 → Python 点击 → 截图对比
```

端到端测试：OCR 检测到 77 个文字、GPA 检测到 106 个 UI 元素，合并 156 个元素，LLM 正确识别出 "Discord, LLM Harness 服务器, #常规 频道"。

## 代码

GitHub: [Fzkuji/Agentic-Programming](https://github.com/Fzkuji/Agentic-Programming)

框架只有 4 个模块：

```
harness/
├── function/    # @function 装饰器 + 内置函数
├── session/     # 6 种 LLM 后端（Anthropic, OpenAI, Claude Code, Codex, OpenClaw, CLI）
├── scope/       # 上下文可见性规则
└── memory/      # 执行日志
```

53 个测试全通过。MIT 开源。

## 总结

**Agentic Programming 的核心思想：**

1. **函数就是函数**——调它，拿结果。不需要 Runtime 类。
2. **Docstring = Prompt**——改注释就改功能。
3. **LLM 是 runtime**——`session.send()` 就是 "CPU 指令"。
4. **Python 是控制流**——if/for/while，不需要自定义 DSL。
5. **Scope 控制可见性**——像 Python 的变量作用域，但用于 LLM 上下文。

MCP 给 LLM 加了手，我们给 Python 加了脑。两者正交，可以组合。

---

*欢迎在评论区讨论。如果你在做 agent 开发，希望这个范式能给你新的思路。*
