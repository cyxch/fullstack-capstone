# 第 6 周复盘：TypeScript 与 React 入门

## 本周目标

- [x] 用 Vite 建立 React + TypeScript 前端工程。
- [x] 将第 5 周页面拆分为 `TaskForm`、`TaskList`、`TaskItem` 和 `EmptyState`。
- [x] 为任务模型、筛选联合类型、请求体和 API 错误定义类型。
- [x] 保留新增、完成、删除、筛选、搜索、刷新和空/错状态。
- [x] 通过 TypeScript 检查和 Vite 生产构建。

## 关键实践

1. `App` 持有跨组件共享的任务数组和请求状态；子组件通过 Props 接收数据和回调。
2. `TaskStatus` 使用字面量联合类型，筛选按钮不再依赖任意字符串。
3. `api.ts` 集中处理 Base URL、JSON 请求头、204 响应和稳定的错误消息，组件只处理用户体验。
4. `TaskForm` 是受控表单，提交失败时保留输入内容，成功时清空输入并给出状态反馈。
5. 列表使用 React 的 `key={task.id}`，任务标题由 React 文本节点渲染，不把用户输入当作 HTML。

## 验证记录

```text
npm run lint   ✅
npm run build  ✅
```

生产构建产物位于 `frontend/dist`（已被 `.gitignore` 忽略）。后端回归测试仍使用第 4 周的命令执行。

## 复盘与下周计划

本周最重要的变化是把“能操作的页面”变成“有明确边界的组件树”：状态放在真正需要共享的最近父组件，输入和事件通过类型化 Props 传递。当前 API 地址和错误类型仍是手工维护的，后续可以在第 16 周进一步引入自动生成或共享 Schema 类型。

下周进入 FastAPI 基础，先为结业项目建立独立的 API 骨架、健康检查和配置入口。
