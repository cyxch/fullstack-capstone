# 第 1 周复盘：环境与工具

## 本周目标

- [x] 确认 Python、Git、Node/npm 版本。
- [x] 创建贯穿项目目录和 Python 后端包。
- [x] 创建环境检查脚本、测试、Lint 和格式化配置。
- [x] 安装并验证 `uv`、`pytest`、`ruff`。

## 当前环境

- Python：3.12.10
- Git：2.54.0.windows.1
- Node：v24.16.0
- npm：11.13.0
- `uv`：0.13.0
- `pytest`：9.1.1（项目 `.venv`）
- `ruff`：0.17.0（项目 `.venv`）

## 验证命令

```powershell
Set-Location fullstack-capstone/backend
python -m app.environment_check
python -m pytest -p no:cacheprovider
ruff check .
ruff format --check .
```

## 问题与下一步

系统级安装曾受到临时目录权限影响，现已使用项目 `.venv` 和项目内 `UV_CACHE_DIR` 完成安装。受限环境下 pytest 缓存目录无法写入，因此验收命令禁用 pytest cache provider。
