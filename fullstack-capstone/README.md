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
