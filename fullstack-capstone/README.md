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

## 第 3 周：类型、配置与质量

任务输入和 JSON 记录使用 Pydantic 严格模型校验：`TaskCreate`、`TaskQuery` 和 `Task` 禁止题目外的隐式类型转换，并会把错误转换成稳定的领域异常。CLI 错误格式为 `Error [error_code]: message`。

配置可由环境变量提供：

```powershell
$env:TASK_DATA_FILE = "data/dev-tasks.json"
$env:TASK_LOG_LEVEL = "DEBUG"
python -m app.cli query
```

`TASK_DATA_FILE` 和 `TASK_LOG_LEVEL` 也可分别用全局 `--data-file` 和 `--log-level` 覆盖。日志默认写入 stderr，每行是可被采集的 JSON 对象，包含 `event`、`level` 和可选的 `context` 字段。

## 开发质量命令

```powershell
Set-Location backend
$env:UV_CACHE_DIR = "G:\_user\.uv-cache"
uv run --no-sync pytest -p no:cacheprovider
uv run --no-sync pytest --cov=app --cov-report=term-missing
uv run --no-sync ruff check app tests
uv run --no-sync ruff format --check app tests
uv run --no-sync mypy app
git diff --check
```

仓库根目录的 `.pre-commit-config.yaml` 会依次运行通用文件检查、Ruff 修复/格式化和后端测试；依赖安装后可执行 `pre-commit install`。

模块职责分别位于 `app/task_models.py`、`app/task_storage.py`、`app/task_service.py` 和 `app/cli.py`。任务数据使用 JSON 数组保存；文件缺失会按空列表处理，非法 JSON、重复标题和未知任务 id 会返回错误并以非零状态退出。
