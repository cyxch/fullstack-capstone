# 第 5 周：原生 HTML、CSS 与 JavaScript 页面

## 启动两个本地服务

先启动第 4 周的 API：

~~~powershell
Set-Location backend
$env:UV_CACHE_DIR = "G:\_user\.uv-cache"
uv run --no-sync uvicorn app.http_api:app --reload
~~~

再启动静态前端：

~~~powershell
Set-Location frontend
python -m http.server 5500
~~~

打开 http://127.0.0.1:5500。页面会通过 fetch 请求
http://127.0.0.1:8000/tasks。后端已配置 CORS，因此两个本地端口可以协作。

## 页面交互

| 操作 | 浏览器行为 | API 请求 |
|---|---|---|
| 首次打开或点击刷新 | 显示加载状态，再渲染任务 | GET /tasks |
| 添加任务 | 禁用提交按钮，显示保存提示并追加新任务 | POST /tasks |
| 点击圆形状态按钮 | 更新完成样式和筛选结果 | PUT /tasks/{id} |
| 点击删除 | 弹出确认，再移除任务 | DELETE /tasks/{id} |
| 点击全部、待完成、已完成 | 只更新当前 DOM 列表 | 无网络请求 |
| 输入搜索词 | 按标题实时过滤 | 无网络请求 |

页面明确区分了加载、成功、空结果和请求失败状态；任务标题通过
textContent 写入 DOM，避免把用户输入当成 HTML 解释。

## 手工验收清单

- API 未启动时打开页面，顶部显示“连接失败”，列表显示恢复提示。
- API 启动后点击刷新，空列表显示“还没有任务，先添加一件吧”。
- 添加任务后可以在全部和待完成筛选中看到它。
- 完成任务后，它从待完成筛选消失，在已完成筛选出现。
- 搜索不存在的标题时显示“没有匹配的任务”。
- 窄屏宽度下，新增表单改为单列，右侧观察卡片移动到主列表下方。
- 通过键盘 Tab 可以访问输入框、筛选按钮、刷新按钮和任务操作按钮。
