# 第 5 周复盘：HTML、CSS 与 JavaScript

## 本周目标

- [x] 使用语义化 HTML 组织页面、表单、列表和状态提示。
- [x] 使用 CSS Grid、Flexbox、媒体查询和焦点样式完成响应式布局。
- [x] 使用原生 JavaScript 完成 DOM 渲染、事件委托、筛选和搜索。
- [x] 使用 fetch 调用第 4 周任务 API，覆盖加载、成功、空状态和错误状态。
- [x] 提供桌面和移动端的手工验收清单。

## 输入：本周学习记录

本周重点记录三个概念：

1. HTML 元素表达内容关系，表单的 label、按钮的 type 和状态区域的
   aria-live 会直接影响键盘和辅助技术的使用体验。
2. CSS Grid 负责页面的主要区域布局，Flexbox 适合按钮组和工具栏；媒体查询
   在 760px 和 520px 处把双栏页面收拢成单栏。
3. fetch 是异步边界，加载中、成功、空结果和失败都必须显式更新界面，
   不能只处理成功响应。

暂时没有完全理解的问题：浏览器事件循环中 Promise 回调和渲染帧的精确调度，
以及不同浏览器开发者工具对 Network 面板瀑布图的差异。

## 实现记录

- frontend/index.html 使用 header、main、section、aside、form、label、ul
  等语义元素，提供清晰的页面结构和可访问名称。
- frontend/styles.css 建立浅色绿色主题，使用 CSS 变量、Grid、Flexbox、
  clamp() 字体尺寸、两个响应式断点和 :focus-visible 焦点反馈。
- frontend/app.js 维护单一页面状态：任务数组、当前筛选、搜索词和加载状态。
  列表使用事件委托处理完成和删除，标题使用 textContent 渲染。
- 页面默认请求 http://127.0.0.1:8000，也可以在打开页面前设置
  window.TASK_API_BASE_URL 指向其他 API 地址。
- 页面文案明确展示 API 连接状态，错误响应会读取后端 JSON 中的 message，
  后端未启动时则显示可操作的重试提示。

## 验证

~~~powershell
Set-Location frontend
node --check app.js
python -m http.server 5500
~~~

静态页面通过本地 HTTP 服务加载，避免 file:// 页面对 ES module 和 fetch
产生额外限制。启动 API 后手工完成新增、筛选、搜索、完成和删除流程。

同时回归后端：

~~~powershell
Set-Location backend
$env:UV_CACHE_DIR = "G:\_user\.uv-cache"
uv run --no-sync pytest -p no:cacheprovider
uv run --no-sync ruff check app tests
uv run --no-sync ruff format --check app tests
uv run --no-sync mypy app
git diff --check
~~~

## 复盘与下周计划

- 新增能力：可以解释浏览器从静态 HTML 加载页面、执行 JavaScript、发出 API
  请求并根据响应更新 DOM 的完整过程。
- 本周坑点：直接双击 HTML 会使用 file://，模块脚本和跨域请求的行为不稳定；
  使用本地静态服务器后，Network 面板和 CORS 行为才可复现。
- 待改进：当前页面还没有组件复用和类型检查，任务状态也只在内存中维护；
  下周迁移到 TypeScript 和 React。
- 下周任务：用 Vite 创建 React + TypeScript 任务列表，拆分表单、列表项和空状态组件。
