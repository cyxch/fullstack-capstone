# 第 4 周：任务 HTTP API

## 启动

在 backend 目录执行：

~~~powershell
$env:UV_CACHE_DIR = "G:\_user\.uv-cache"
uv run --no-sync uvicorn app.http_api:app --reload
~~~

服务默认监听 http://127.0.0.1:8000。这是内存版 API，进程重启后任务会清空。

## 接口表

| 方法 | 路径 | 成功状态码 | 作用 |
|---|---|---:|---|
| GET | /tasks?status=pending&keyword=HTTP | 200 | 列出任务，可按状态和标题关键词过滤 |
| GET | /tasks/{task_id} | 200 | 查看单个任务 |
| POST | /tasks | 201 | 创建待完成任务 |
| PUT | /tasks/{task_id} | 200 | 更新 title 或 completed |
| DELETE | /tasks/{task_id} | 204 | 删除任务，无响应体 |
| GET | /docs | 200 | 查看 FastAPI 自动生成的 OpenAPI 页面 |

任务对象格式：

~~~json
{
  "id": 1,
  "title": "学习 HTTP",
  "completed": false
}
~~~

错误统一使用以下 JSON 信封：

~~~json
{
  "error": {
    "code": "task_not_found",
    "message": "task not found: 99"
  }
}
~~~

常见状态码：

- 201：创建成功。
- 200：读取或更新成功。
- 204：删除成功，响应没有 body。
- 409：标题忽略大小写后重复。
- 422：请求体、查询参数或路径参数校验失败。
- 404：任务不存在。

## CORS

应用默认允许浏览器从任意 Origin 发送本示例 API 的请求，并允许
GET、POST、PUT、DELETE 和 OPTIONS。create_app(allow_origins=[...])
可以在测试或部署时收紧允许的 Origin。生产环境应使用明确的前端域名列表。

## 一次完整请求生命周期

浏览器或 curl 发出带 JSON 的 HTTP 请求后，FastAPI 先解析路径、查询参数、
Headers 和 body，再用 Pydantic 校验输入。路由把已校验的数据交给
TaskService，服务层执行标题唯一性和任务存在性规则，内存存储替换快照，
最后由 FastAPI 将 Task 序列化为 JSON，并写入状态码和响应 Headers。
