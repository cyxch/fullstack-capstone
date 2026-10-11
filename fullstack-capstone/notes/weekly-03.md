# 第 3 周复盘：类型、配置与代码质量

## 本周目标

- [x] 用严格 Pydantic 模型校验创建输入、查询参数和持久化记录。
- [x] 为配置、日志和领域错误补充明确的类型与稳定接口。
- [x] 加入覆盖率、mypy、Ruff 和 pre-commit 的可复现质量检查。
- [x] 补充空标题、严格类型、非法记录、配置和结构化日志测试。

## 实现记录

- `app/task_models.py`：`TaskCreate`、`TaskQuery` 和不可变 `Task` 使用严格字段类型；模型错误会转换为 `TaskValidationError`。
- `app/config.py`：`Settings` 从 `TASK_DATA_FILE`、`TASK_LOG_LEVEL` 读取配置，CLI 参数可以覆盖环境变量。
- `app/logging_config.py`：标准库日志输出 JSON 行，包含时间、级别、事件和上下文，默认写入 stderr。
- `app/task_service.py` 与 `app/task_storage.py`：业务操作和持久化操作记录事件，所有预期错误都带有稳定 `code` 与 `as_dict()`。
- `.pre-commit-config.yaml` 与 `pyproject.toml`：统一格式化、Lint、覆盖率和类型检查命令。

## 错误处理约定

| 错误码 | 场景 | CLI 行为 |
|---|---|---|
| `invalid_task` | 标题、任务 id 或任务记录不符合模型 | 输出错误并返回 1 |
| `duplicate_task` | 标题忽略大小写后重复 | 输出错误并返回 1 |
| `task_not_found` | 完成或删除未知 id | 输出错误并返回 1 |
| `task_data_error` | JSON 文件无法读取或结构非法 | 输出错误并返回 1 |
| `invalid_configuration` | 环境变量或参数值非法 | 输出错误并返回 1 |

库代码抛出领域异常，CLI 负责把异常转换为 `Error [code]: message`；日志记录 `command_failed`，不会把堆栈泄露给普通用户。

## 学习记录

本周掌握的三个关键概念是：边界输入应先经过严格模型、配置读取应与业务逻辑解耦、日志事件应包含机器可读上下文。仍需理解的问题是：当 JSON 文件被多个进程同时写入时，原子替换只能避免半写入，不能单独解决跨进程的并发覆盖。

## 验证命令

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

## 复盘与下周计划

- 新增能力：任务边界有严格类型、可配置路径和级别、结构化日志以及稳定错误码。
- 本周坑点：Pydantic 默认可能进行隐式类型转换，因此模型字段使用 `Strict*` 类型；空白字符串还需要显式去除并再次检查。
- 待改进：JSON 存储仍没有跨进程锁，后续迁移数据库时需要用事务解决并发一致性。
- 第 4 周任务：用 Python Web 框架实现内存版任务 HTTP API，覆盖 REST 路由、状态码、JSON 错误和接口测试。
