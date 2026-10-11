# 第 4 周复盘：Web 与 HTTP 基础

## 本周目标

- [x] 理解 HTTP 请求、响应、方法、状态码、Headers、Cookie、CORS 和 JSON。
- [x] 用 FastAPI 实现内存版任务 REST API。
- [x] 覆盖列表、详情、创建、更新和删除五类资源操作。
- [x] 为成功、校验失败、重复资源、资源不存在和删除场景编写接口测试。
- [x] 提供可复制的请求示例和自动生成的 /docs 入口。

## 输入：本周学习记录

阅读 FastAPI、Pydantic 和 MDN HTTP 文档后，记录三个关键概念：

1. HTTP 方法描述客户端意图：GET 读取、POST 创建、PUT 更新、DELETE 删除。
2. 状态码是机器可读的结果分类，2xx 表示成功，4xx 表示请求或资源问题。
3. JSON body 负责传输结构化数据，Headers 负责描述媒体类型、缓存、来源和认证等元数据。

暂时没有完全理解的问题：浏览器的 CORS 预检为什么需要 OPTIONS，以及
允许凭据时为什么不能把 Access-Control-Allow-Origin 设置成 *。

## 实现记录

- app/http_api.py 创建 create_app() 工厂，默认使用 InMemoryTaskStorage，
  让每个测试拥有独立的数据快照。
- GET /tasks 支持 status 和 keyword 查询；GET /tasks/{id} 提供详情。
- POST 返回 201，PUT 返回 200，DELETE 返回空响应 204。
- 领域错误映射为稳定的 JSON：重复标题为 409 duplicate_task，资源不存在为
  404 task_not_found，输入问题为 422 invalid_request 或 invalid_task。
- CORSMiddleware 允许学习阶段的跨域预检，并通过 allow_origins 参数支持收紧。
- TaskService 新增详情读取和部分字段更新，内存存储与 JSON 文件存储共用同一套业务规则。

## 验证

~~~powershell
Set-Location backend
$env:UV_CACHE_DIR = "G:\_user\.uv-cache"
uv run --no-sync pytest -p no:cacheprovider
uv run --no-sync ruff check app tests
uv run --no-sync ruff format --check app tests
uv run --no-sync mypy app
git diff --check
~~~

结果：22 个测试通过，Ruff、格式化检查、mypy 和 diff 检查通过。
tests/test_http_api.py 覆盖了 200、201、204、404、409 和 422，
并检查了 CORS 预检响应。

使用 Uvicorn 启动后，curl 实测完成 POST 201、GET 200、PUT 200 和 DELETE 204
链路；服务日志记录了对应的 HTTP 状态码。

请求示例见 backend/http-api-examples.http，接口说明见 docs/http-api.md。

## 复盘与下周计划

- 新增能力：可以从浏览器或 API 工具完整执行任务 CRUD，并能根据状态码定位常见错误。
- 本周坑点：Pydantic 校验错误的 ctx 可能含有 Python 异常对象，直接放入 JSON
  会序列化失败；现在先通过 jsonable_encoder 转换。
- 待改进：内存存储没有跨进程共享和持久化能力，后续用 FastAPI 项目骨架接入数据库。
- 下周任务：继续 HTML、CSS 和 JavaScript，制作调用公开 API 的响应式页面原型。
