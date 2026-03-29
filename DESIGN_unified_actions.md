# Unified Actions 设计方案

## 目标

模型调用统一的 GUI action 接口，不需要知道底层用什么工具。脚本根据 target 自动选择正确的实现。

## 架构

```
模型
  ↓ 调用
统一接口 (gui_action.py)
  ↓ 根据 target 路由
┌─────────────┐    ┌──────────────────┐
│ local (Mac)  │    │ vm:IP (Linux VM) │
│ pynput       │    │ HTTP API →       │
│ screencapture│    │   pyautogui      │
│ pbcopy       │    │   xdotool        │
│ osascript    │    │   wmctrl         │
└─────────────┘    └──────────────────┘
```

## 激活 (activate.py --target)

`--target` 是**必填参数**。

```bash
# 操作本机
python3 activate.py --target local

# 操作远程 VM
python3 activate.py --target vm:172.16.105.128

# 切换目标（重新 activate）
python3 activate.py --target local
```

activate.py 做的事：
1. 检测 target 平台（local → 读本机 / vm:IP → 通过 API 检测远程）
2. 输出平台摘要到 stdout（进入模型上下文）
3. 写状态文件 `~/.gui_agent_target`（记录当前 target）
4. 复制对应 `_actions.yaml`（模型后续 read 用）

## 统一接口 (gui_action.py)

```bash
# 模型这样调用：
python3 gui_action.py click 500 300
python3 gui_action.py type "Hello World"
python3 gui_action.py screenshot /tmp/screen.png
python3 gui_action.py shortcut ctrl+s
python3 gui_action.py focus "window title"
python3 gui_action.py close "window title"
python3 gui_action.py key enter
```

脚本内部：
```python
# 读取当前 target
target = read_target_file()  # 从 ~/.gui_agent_target

if target == "local":
    # Mac: 用 pynput / screencapture
    execute_local(action, args)
elif target.startswith("vm:"):
    # VM: 通过 HTTP API 执行
    vm_ip = target.split(":")[1]
    execute_vm(action, args, vm_ip)
```

## 可用 Actions

| Action | 参数 | 说明 |
|--------|------|------|
| `click` | x y | 点击坐标 |
| `double_click` | x y | 双击 |
| `right_click` | x y | 右键点击 |
| `type` | "text" | 输入文本 |
| `key` | keyname | 按键（enter, tab, escape, delete, up, down...） |
| `shortcut` | keys | 组合键（ctrl+s, ctrl+shift+t, alt+F4...） |
| `screenshot` | [path] | 截图（默认 /tmp/gui_screenshot.png） |
| `focus` | "title" | 激活窗口 |
| `close` | "title" | 关闭窗口 |
| `list_windows` | | 列出所有窗口 |

## 内部实现映射

| Action | local (Mac) | vm (Linux) |
|--------|------------|------------|
| click | `pynput click_at(x, y)` | `POST /execute → pyautogui.click(x, y)` |
| type | `pynput paste_text(text)` | `POST /execute → xdotool type "text"` |
| key | `pynput key_press(key)` | `POST /execute → pyautogui.press(key)` |
| shortcut | `pynput key_combo(keys)` | `POST /execute → pyautogui.hotkey(keys)` |
| screenshot | `screencapture -x path` | `GET /screenshot → save to path` |
| focus | `osascript activate app` | `POST /execute → wmctrl -a "title"` |
| close | `osascript close` | `POST /execute → wmctrl -c "title"` |
| list_windows | `osascript` | `POST /execute → wmctrl -l` |

## 坐标处理

| Target | 检测空间 | 点击空间 | 缩放 |
|--------|---------|---------|------|
| local Mac (Retina) | 2x | 1x | detect_to_click() 自动 |
| local Mac (非 Retina) | 1x | 1x | 无 |
| vm Linux | 1x | 1x | 无 |

screenshot action 返回时附带坐标空间信息，OCR 在 host 上跑完后坐标直接可用。

## 状态文件

`~/.gui_agent_target`:
```json
{
    "target": "vm:172.16.105.128",
    "platform": "linux",
    "activated_at": "2026-03-29 13:50:00"
}
```

每次 activate 覆写。gui_action.py 每次执行时读取。

## 文件结构

```
scripts/
├── activate.py          # 激活 + 平台检测 + 写状态
├── gui_action.py        # 统一 action 接口
├── backends/
│   ├── local_mac.py     # Mac 本机实现
│   └── remote_vm.py     # VM 远程实现
```

## SKILL.md 改动

```markdown
## STEP 0: Activate (MANDATORY)
python3 {baseDir}/scripts/activate.py --target <local|vm:IP>

## Actions
All GUI operations go through:
python3 {baseDir}/scripts/gui_action.py <action> [args...]
```

模型只需要知道两件事：activate 指定 target，gui_action 执行操作。
