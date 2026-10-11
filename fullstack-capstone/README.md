# Fullstack Capstone

Python 全栈提升计划的贯穿项目，默认主题为个人知识库/任务协作应用。

## 第 1 周：环境检查

进入后端目录并运行环境检查脚本：

```powershell
Set-Location backend
python -m app.environment_check
```

运行测试和代码质量检查：

```powershell
python -m pytest -p no:cacheprovider
ruff check .
ruff format --check .
```

本机尚未安装 `uv` 时，可先使用 Python 内置虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

使用 `uv` 时，推荐将缓存放在项目目录，并在已安装依赖后使用 `--no-sync`：

```powershell
$env:UV_CACHE_DIR = "$PWD\.uv-cache"
uv venv .venv
uv pip install -e ".[dev]"
uv run --no-sync python -m app.environment_check
```

后续周次会在此目录继续添加 FastAPI 后端、React 前端、数据库和 Docker 配置。

## 第 2 周：JSON 任务清单 CLI

进入后端目录后，可以直接运行任务清单。默认数据文件为 `data/tasks.json`，也可以通过 `--data-file` 指定其他路径：

```powershell
Set-Location backend
python -m app.cli add "学习 Python 文件操作"
python -m app.cli query
python -m app.cli query --status pending --keyword Python
python -m app.cli complete 1
python -m app.cli delete 1
```

模块职责分别位于 `app/task_models.py`、`app/task_storage.py`、`app/task_service.py` 和 `app/cli.py`。任务数据使用 JSON 数组保存；文件缺失会按空列表处理，非法 JSON、重复标题和未知任务 id 会返回错误并以非零状态退出。
