# 第 7 周：FastAPI 基础骨架

本周在第 4 周任务 API 之上建立结业项目后端骨架。旧的 `/tasks` 接口继续保留，新的结业项目入口使用版本化路径 `/api/v1/items`，便于后续加入认证、分页和数据库而不改变学习阶段的兼容接口。

## 启动

```powershell
Set-Location backend
$env:UV_CACHE_DIR = "G:\_user\.uv-cache"
uv run --no-sync uvicorn app.http_api:app --reload
```

默认地址：

- OpenAPI 页面：`http://127.0.0.1:8000/docs`
- ReDoc 页面：`http://127.0.0.1:8000/redoc`
- 健康检查：`http://127.0.0.1:8000/health`

## 配置

`app.config.Settings` 统一读取以下环境变量：

| 变量 | 默认值 | 作用 |
|---|---|---|
| `TASK_APP_NAME` | `fullstack-capstone-backend` | 健康检查中的服务名称 |
| `TASK_ENVIRONMENT` | `development` | 当前运行环境标识 |
| `TASK_LOG_LEVEL` | `INFO` | CLI 和日志级别 |
| `TASK_DATA_FILE` | `data/tasks.json` | 第 2～4 周任务 CLI 的 JSON 文件 |
| `TASK_CORS_ORIGINS` | `*` | 逗号分隔的允许来源列表 |

生产或共享环境应把 `TASK_CORS_ORIGINS` 设置为明确的前端来源，例如：

```powershell
$env:TASK_ENVIRONMENT = "production"
$env:TASK_CORS_ORIGINS = "https://app.example.com"
```

## 版本化条目接口

| 方法 | 路径 | 成功状态 | 说明 |
|---|---|---:|---|
| GET | `/health` | 200 | 返回服务状态、环境和版本 |
| GET | `/api/v1/items` | 200 | 列出内存中的条目 |
| GET | `/api/v1/items/{item_id}` | 200 | 获取单个条目 |
| POST | `/api/v1/items` | 201 | 创建条目 |
| PUT | `/api/v1/items/{item_id}` | 200 | 更新标题或内容 |
| DELETE | `/api/v1/items/{item_id}` | 204 | 删除条目 |

创建请求示例：

```json
{
  "title": "FastAPI 依赖注入",
  "content": "记录本周阅读笔记"
}
```

响应包含 `id`、`title`、`content`、`created_at` 和 `updated_at`。标题长度为 1～120 个字符，内容最多 5000 个字符；请求体的未知字段会被拒绝。重复标题返回 409，不存在条目返回 404，输入校验失败返回 422，错误格式沿用：

```json
{
  "error": {
    "code": "item_not_found",
    "message": "item not found: 99"
  }
}
```

## 分层结构

- `item_models.py`：请求、响应和校验规则。
- `item_service.py`：唯一性、ID 分配和更新规则。
- `item_storage.py`：当前使用内存快照，后续可替换为 Repository/PostgreSQL。
- `http_api.py`：路由、依赖配置、CORS、异常映射和 OpenAPI 元数据。

## 验证

```powershell
Set-Location backend
$env:UV_CACHE_DIR = "G:\_user\.uv-cache"
uv run --no-sync pytest -p no:cacheprovider
uv run --no-sync ruff check app tests
uv run --no-sync ruff format --check app tests
uv run --no-sync mypy app
git diff --check
```
