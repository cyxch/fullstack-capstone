# 第 7 周复盘：FastAPI 基础骨架

## 本周目标

- [x] 为应用加入统一配置对象和环境变量入口。
- [x] 增加 `/health` 健康检查和明确的应用版本号。
- [x] 建立 `/api/v1/items` 版本化条目 CRUD API。
- [x] 使用 Pydantic Schema 校验字段长度、必填项和未知字段。
- [x] 用 TestClient 覆盖健康检查、CRUD、校验、重复资源和 OpenAPI。

## 关键实践

1. `create_app()` 继续作为应用工厂，测试可以注入独立的任务存储、条目存储和 `Settings`，避免共享全局状态。
2. 条目路由使用 `/api/v1/items`，保留 `/tasks` 作为前几周的兼容练习接口；版本化路径为后续 API 演进预留空间。
3. 路由只负责 HTTP 协议适配，唯一性、ID 分配和更新规则放在 `ItemService`，存储由 `ItemStore` Protocol 隔离。
4. `Item` 使用不可变响应模型，并保留 UTC 的 `created_at`/`updated_at`，更新时只改变后者。
5. FastAPI 的请求体校验、领域异常和资源异常分别映射到 422、409、404，并保持统一的 `error.code/message` 结构。

## 验证记录

```text
27 passed ✅
ruff check ✅
ruff format --check ✅
mypy app ✅
```

手工 TestClient 流程也验证了 `/health`、条目新增/查询/更新/删除，以及空标题、重复标题和不存在资源的错误响应。

## 复盘与下周计划

当前条目仍存储在内存中，进程重启后数据会清空，这是有意保留的最小骨架边界。下一周将把 API 设计扩展到分页、过滤、排序、统一的 Service/Repository 错误边界，并完善接口说明和重复操作测试；数据库接入留到第 12 周。
