# PythonTest

## 项目简介

这是一个个人/工具类的 Python 项目集合，包含若干脚本用于文件处理、截图及重命名、照片与视频分类、Jar 比较、数据处理等实用工具。

仓库中脚本多为独立的小工具，适合直接阅读并按需运行或二次开发。

## 目录概览（选取常用文件/目录）

- `baidu_input_mi_test.py`：与输入法或文本处理相关的测试脚本。
- `venera_input*.py`：与“venera”相关的数据输入与测试脚本（示例数据见 `venera_input.json`）。
- `screenshot_*.py`：与截图数据创建、渲染、扫描相关的脚本。
- `PhotoClassification/`：照片与视频分类、重命名工具及子目录（`FolderRename/` 等）。
- `LLOneBot/`：与 OneBot/QQ 好友、群组数据处理相关的脚本及 CSV 数据。
- `jar_read.py`, `compare_jars.py`, `compare_delete_jars.py`：用于读取与比较 Jar 包的脚本。
- `file_test.py`, `find_incomplete_jpegs.py`：通用文件检查/处理脚本。

仓库根目录中还有若干示例数据文件（CSV/JSON/TXT）可供测试与参考。

## 快速开始

先决条件：

- 已安装 Python 3.8+（推荐 3.10/3.11）。
- 建议为项目创建虚拟环境并安装依赖（如果将来添加 `requirements.txt`，请按其安装）。

创建并激活虚拟环境（Windows PowerShell）：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

运行脚本示例（在激活的虚拟环境中）：

```powershell
# 运行截图扫描脚本
python .\screenshot_scan.py

# 运行 venera 测试脚本
python .\venera_input_test.py

# 检查重复照片（位于 PhotoClassification）
python .\PhotoClassification\photo_duplicate.py
```

注意：多数脚本为独立工具，运行时可能需要传入命令行参数或准备输入文件（CSV/JSON）。请打开具体脚本查看顶部注释或 `if __name__ == "__main__":` 部分以获取用法说明。

## 开发和测试

- 建议将常用依赖写入 `requirements.txt` 并在 README 更新后使用 `pip install -r requirements.txt` 安装。
- 若需快速检查语法或类型，可使用 `flake8`/`pylint`/`mypy` 等工具。

示例（安装 lint 工具）：

```powershell
pip install flake8
flake8 .
```

## 贡献

如果你希望贡献改进或修复：

1. fork 该仓库并新建分支（feature/xxx 或 fix/yyy）。
2. 提交清晰的 commit，并发起 PR，描述变更目的与测试说明。
3. 我会审阅并合并合适的更改。

若需我为仓库添加 `requirements.txt`、示例运行脚本或 CI 配置（GitHub Actions），请告诉我具体需求，我可以代为创建。

## 许可证

本仓库默认采用 MIT 许可证（如需其他许可证，请在仓库根目录添加 LICENSE 文件并告知）。

---

如需我根据你的使用场景（例如：照片去重自动化、批量重命名流程、或将某些脚本打包成 CLI）进一步整理 README 或添加示例/测试，请说明优先级与目标脚本，我会继续实现。