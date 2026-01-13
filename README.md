# BookToNotes - 智能读书笔记引擎

[English](README.en.md) | 中文

> 一条命令，将任意书籍转化为结构化笔记。

BookToNotes 是一个 Claude Code 技能，自动化整个读书流程：
**搜索 → 下载 → 格式转换 → 上传 NotebookLM → AI 问答 → 结构化笔记**

## 功能特点

- **一键式流程**：只需提供书名，即可获得结构化笔记
- **Zlib 集成**：通过 Telegram 机器人搜索和下载电子书
- **格式转换**：使用 Calibre 自动将 epub/mobi/azw 转换为 PDF
- **NotebookLM 集成**：上传书籍并进行 AI 驱动的问答
- **结构化输出**：生成可自定义深度的全面笔记

## 前置要求

使用 BookToNotes 之前，你需要：

1. **Claude Code** - [安装 Claude Code CLI](https://github.com/anthropics/claude-code)
2. **Calibre** - [下载 Calibre](https://calibre-ebook.com/) 用于电子书格式转换
3. **Telegram 账号** - 用于访问 Zlib 机器人
4. **Google 账号** - 用于访问 NotebookLM
5. **NotebookLM Skill** - 安装 Claude Code 的 NotebookLM 技能

## 安装步骤

### 1. 克隆仓库

```bash
# 进入 Claude Code skills 目录
cd ~/.claude/skills

# 克隆仓库
git clone https://github.com/crisp0530/BookToNotes.git book-to-notes
```

### 2. 安装 Python 依赖

```bash
cd ~/.claude/skills/book-to-notes/scripts
pip install telethon
```

### 3. 配置路径（如需要）

编辑 `scripts/config.py` 来自定义你系统的路径：

```python
# Calibre 路径（根据你的操作系统调整）
CALIBRE_PATH = r"C:\Program Files\Calibre2\ebook-convert.exe"  # Windows
# CALIBRE_PATH = "/Applications/calibre.app/Contents/MacOS/ebook-convert"  # macOS
# CALIBRE_PATH = "ebook-convert"  # Linux（如果在 PATH 中）
```

### 4. 认证服务

#### Telegram（用于 Zlib 下载）
```bash
cd ~/.claude/skills/book-to-notes/scripts
python tg_auth.py setup
```

按提示输入：
1. 手机号（带国家代码，如 +86xxx）
2. 收到的验证码
3. 两步验证密码（如果开启了的话）

#### NotebookLM（用于 AI 问答）
```bash
cd ~/.claude/skills/notebooklm

# Windows
.venv/Scripts/python.exe scripts/auth_manager.py setup

# macOS/Linux
.venv/bin/python scripts/auth_manager.py setup
```

## 使用方法

### 在 Claude Code 中使用

直接告诉 Claude 你想分析什么书：

```
> 帮我分析《思考，快与慢》
> /digest-book "精益创业"
> 一键吃透《原子习惯》
```

### 命令行使用

```bash
cd ~/.claude/skills/book-to-notes/scripts

# 从 Zlib 下载并处理
python prepare.py "书名"

# 交互模式（从搜索结果中选择）
python prepare.py "书名" -i

# 使用本地文件
python prepare.py --file "path/to/book.epub" --name "书名"
```

## 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                    BookToNotes 工作流程                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 输入                                                     │
│     ├── 书名 → 从 Zlib 搜索并下载                            │
│     └── 本地文件 → 跳到格式转换                              │
│                                                              │
│  2. 转换                                                     │
│     └── epub/mobi/azw → PDF（通过 Calibre）                  │
│                                                              │
│  3. 上传                                                     │
│     └── PDF → NotebookLM                                    │
│                                                              │
│  4. 分析                                                     │
│     ├── 澄清需求（模式、聚焦点、受众）                        │
│     ├── 生成深度问题                                         │
│     └── 与 NotebookLM 进行问答循环                           │
│                                                              │
│  5. 输出                                                     │
│     └── 结构化 Markdown 笔记                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 分析模式

### 深度理解模式
适合想要深入理解一本书的用户：
- 核心论点和关键概念
- 作者背景和历史语境
- 论证方法和逻辑结构
- 批判性评估和思想遗产

**问题框架示例**：
1. 这本书的核心主张是什么？
2. 作者想解决什么问题？
3. 书中有哪些隐含的前提假设？
4. 论证的关键支柱是什么？
5. 有哪些反直觉的观点？

### 实用提取模式
适合想要快速获取可行动知识的用户：
- 可操作的框架和模型
- 案例研究和示例
- 常见误区
- 执行清单

**问题框架示例**：
1. 书中最重要的 3-5 个观点是什么？
2. 有哪些可以直接使用的方法论/框架/模型？
3. 有哪些可立即执行的行动建议？
4. 这些方法的适用场景和局限性是什么？

## 项目结构

```
book-to-notes/
├── SKILL.md              # Claude Code 技能定义
├── README.md             # 英文说明文档
├── README.zh-CN.md       # 中文说明文档（本文件）
├── LICENSE               # MIT 开源协议
├── .gitignore            # Git 忽略文件
├── scripts/
│   ├── config.py         # 配置文件（路径、设置）
│   ├── tg_auth.py        # Telegram 认证脚本
│   ├── zlib_download.py  # Zlib 搜索和下载脚本
│   └── prepare.py        # 一体化准备脚本
├── downloads/            # 下载的电子书（已 gitignore）
├── temp/                 # 转换后的 PDF（已 gitignore）
├── output/               # 生成的笔记（已 gitignore）
└── data/
    └── session/          # 认证会话（已 gitignore）
```

## 配置说明

所有配置都在 `scripts/config.py` 中：

| 设置 | 说明 | 默认值 |
|------|------|--------|
| `TELEGRAM_API_ID` | Telegram API ID | 2040（公开） |
| `TELEGRAM_API_HASH` | Telegram API Hash | （公开） |
| `ZLIB_BOT_USERNAME` | Zlib Telegram 机器人 | zlaboratory_bot |
| `CALIBRE_PATH` | ebook-convert 路径 | 取决于操作系统 |
| `DOWNLOAD_TIMEOUT` | 下载超时（秒） | 120 |
| `MAX_SEARCH_RESULTS` | 显示的最大搜索结果数 | 5 |

## 常见问题

### "Calibre not found"（找不到 Calibre）
- 从 https://calibre-ebook.com/ 安装 Calibre
- 更新 `config.py` 中的 `CALIBRE_PATH`

### "Not authenticated"（未认证）- Telegram
```bash
python tg_auth.py setup
```
按提示完成 Telegram 登录。

### "NotebookLM venv not initialized"（NotebookLM 虚拟环境未初始化）
- 确保 NotebookLM 技能已正确安装
- 运行 NotebookLM 的设置脚本

### "Upload failed"（上传失败）
- NotebookLM 对 epub 支持不稳定 - 始终先转换为 PDF
- 检查你的 Google 账号认证状态

### 下载超时
- 检查网络连接
- 尝试使用 VPN
- 增加 `config.py` 中的 `DOWNLOAD_TIMEOUT` 值

### 搜索不到书籍
- 尝试使用英文书名搜索
- 尝试使用作者名 + 书名
- 换一个 Zlib 机器人（在 Telegram 搜索 "zlib"）

## 隐私与安全

- **不存储个人数据**：所有路径都可配置
- **会话文件保存在本地**：Telegram/Google 会话只存在你的机器上
- **敏感目录已 gitignore**：downloads/、data/、output/ 不会被追踪

## 工作原理

### 1. Zlib 下载
通过 Telethon 库与 Telegram Zlib 机器人交互：
- 发送书名进行搜索
- 解析返回的搜索结果
- 发送 `/book` 命令下载文件

### 2. 格式转换
使用 Calibre 的 `ebook-convert` 命令行工具：
- 支持 epub、mobi、azw、azw3、txt、docx 等格式
- 统一转换为 PDF 以确保 NotebookLM 兼容性

### 3. NotebookLM 集成
通过 NotebookLM 技能：
- 自动上传 PDF 到 NotebookLM
- 创建新的 Notebook
- 通过 API 进行问答

### 4. AI 分析
Claude Code 根据选择的模式：
- 生成针对性的问题列表
- 循环向 NotebookLM 提问
- 整合答案生成结构化笔记

## 开源协议

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请随时提交 Pull Request。

如果你觉得这个项目有用，欢迎给个 Star ⭐

## 致谢

- [Calibre](https://calibre-ebook.com/) - 电子书转换
- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram API
- [NotebookLM](https://notebooklm.google.com/) - AI 驱动的文档分析
- [Claude Code](https://github.com/anthropics/claude-code) - AI 编程助手
