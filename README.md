# PythonTest

这是一个个人维护的 Python 脚本集合，包含若干用于文件处理、截图/图像处理、日志、分析与工具脚本的实用程序。

仓库目标：集中管理日常使用的脚本、便于复用与共享、并提供简单的贡献流程。

---

## 目录概览

- `LLOneBot/`：与 OneBot/聊天/群组数据处理相关的脚本与导出的 CSV 文件。
- `PhotoClassification/`：照片/视频自动重命名、分类与重命名日志脚本。
- 各类独立脚本（顶级文件）：如 `screenshot.py`、`screenshot_scan.py`、`hash.py`、`jar_read.py` 等，通常各自完成单一工具功能。

更多文件请参见仓库根目录。

## 快速开始

先决条件

- Python 3.8+（建议使用最新的 3.x 版本）
- 建议在虚拟环境中运行（venv / conda）

安装依赖

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

运行示例

```powershell
# 检查项目中的示例脚本
python test.py
python screenshot.py --help
python LLOneBot/duplicated_users.py
```

具体脚本通常带有 `--help` 或注释说明，建议先阅读脚本顶部注释或直接查看脚本源文件。

## 代码与风格

- 本仓库优先使用 PEP8 风格。
- 请尽量在提交前运行静态检查（例如 flake8 / pylint），并写明变更目的与测试步骤。

## 项目结构（部分）

```
PythonTest/
├─ README.md
├─ requirements.txt
├─ screenshot.py
├─ screenshot_scan.py
├─ LLOneBot/
│  ├─ duplicated_users.py
│  └─ ...
└─ PhotoClassification/
	├─ photo_rename.py
	└─ ...
```

## 贡献

欢迎提交 Issue 和 Pull Request。请先阅读 `CONTRIBUTING.md` 与 `CODE_OF_CONDUCT.md`，以便了解贡献流程与社区准则。

## 许可证

本项目使用 MIT 许可证，详见 `LICENSE` 文件。

---

作者：RecRivenVI
更新时间：2025

