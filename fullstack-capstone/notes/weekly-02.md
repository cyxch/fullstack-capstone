# 第 2 周复盘：Python 工程基础与 JSON 任务清单

## 本周目标

- [x] 将命令行参数解析、业务逻辑和 JSON 文件存储拆分为独立模块。
- [x] 支持新增、完成、删除、查询和状态/关键词过滤。
- [x] 对缺失文件、空文件、非法 JSON、重复标题和未知任务 id 做明确处理。
- [x] 编写 8 个测试，并完成格式化、Lint 和回归测试。

## 模块职责

- `app/task_models.py`：定义不可变的 `Task` 数据模型，集中校验 id、标题和完成状态。
- `app/task_storage.py`：负责 JSON 读写、数据格式校验和原子保存；缺失文件表示空列表。
- `app/task_service.py`：负责任务 id 分配、标题去重、完成、删除和查询过滤等业务规则。
- `app/cli.py`：负责 argparse 参数、命令输出和错误码，不直接操作 JSON 细节。

## 学习记录

本周掌握了三个关键概念：数据模型约束应该尽早执行；持久化模块应该隔离文件格式细节；命令行入口只负责适配用户输入，不应承载业务规则。

仍需理解的问题是：当任务数据量增大或多个进程同时写入时，JSON 文件的锁和并发一致性如何设计。当前版本通过同目录临时文件加替换避免半写入，但没有跨进程锁。

## 验证命令

```powershell
Set-Location fullstack-capstone/backend
$env:UV_CACHE_DIR = "G:\_user\.uv-cache"
uv run --no-sync pytest -p no:cacheprovider
.\.venv\Scripts\ruff.exe check app tests
.\.venv\Scripts\ruff.exe format --check app tests
git diff --check
```

## 复盘与下周计划

- 新增能力：可以在不依赖数据库的情况下运行完整任务清单，并能从服务层复用规则。
- 遇到的坑：JSON 文件的格式错误不能直接让底层异常泄漏到 CLI，需要转换成可理解的领域错误。
- 待改进：为 CLI 增加更丰富的输出格式和集成测试，同时考虑使用类型检查工具验证边界输入。
- 第 3 周任务：补充类型标注、Pydantic 模型、结构化日志和更严格的代码质量检查。
