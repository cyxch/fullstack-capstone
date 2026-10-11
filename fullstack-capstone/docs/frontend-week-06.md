# 第 6 周：TypeScript 与 React 入门

本周把第 5 周的原生浏览器页面迁移为 Vite + React + TypeScript。页面继续调用第 4 周的 FastAPI 任务接口，但视图拆成可复用组件，并让任务、筛选条件和 API 错误都经过 TypeScript 类型检查。

## 组件结构

```text
src/
├── App.tsx                    # 页面状态、请求协调和布局
├── api.ts                     # fetch 封装和 API 地址配置
├── types.ts                   # Task、TaskStatus、请求和错误类型
├── main.tsx                   # React 根节点
└── components/
    ├── EmptyState.tsx         # 加载、空结果和错误状态
    ├── TaskForm.tsx           # 受控新增表单
    ├── TaskItem.tsx           # 单条任务及完成/删除操作
    └── TaskList.tsx           # 筛选、搜索和任务列表
```

状态放在 `App`，因为新增、切换、删除、刷新和筛选都需要共享同一份任务数据。表单输入是 `TaskForm` 的局部状态，列表的筛选条件由 `App` 管理并作为 Props 传入，避免组件之间直接修改彼此的数据。

## 启动

先启动后端：

```powershell
Set-Location backend
$env:UV_CACHE_DIR = "G:\_user\.uv-cache"
uv run --no-sync uvicorn app.http_api:app --reload
```

再安装依赖并启动 Vite：

```powershell
Set-Location frontend
npm install
npm run dev
```

默认 API 地址是 `http://127.0.0.1:8000`。可以使用 `VITE_API_BASE_URL`，或在页面加载前设置 `window.TASK_API_BASE_URL` 覆盖它。

## 验收路径

- 空列表显示空状态；API 不可用时显示错误状态和连接失败。
- 新增任务后，任务出现在列表中，提交按钮在请求期间禁用。
- 点击圆形按钮切换完成状态，待完成和已完成筛选会同步更新。
- 删除任务前需要确认，删除成功后列表和计数立即更新。
- 输入关键词会实时过滤标题；刷新按钮重新从 API 加载任务。
- 使用 Tab 可以访问表单、筛选、刷新和每条任务的操作按钮。

## 验证命令

```powershell
Set-Location frontend
npm run lint
npm run build
```

`lint` 执行 TypeScript 严格类型检查，`build` 先执行项目引用检查，再生成 Vite 生产包。
