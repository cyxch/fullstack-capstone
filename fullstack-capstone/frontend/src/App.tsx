import { useCallback, useEffect, useMemo, useState } from "react";
import { API_BASE_URL, createTask, deleteTask, listTasks, updateTask } from "./api";
import { TaskForm } from "./components/TaskForm";
import { TaskList } from "./components/TaskList";
import type { Task, TaskStatus } from "./types";
import { ApiError } from "./types";
import "../styles.css";

type ConnectionState = "idle" | "online" | "error";
type MessageTone = "info" | "error";

interface Message {
  text: string;
  tone: MessageTone;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "请求失败，请稍后重试";
}

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filter, setFilter] = useState<TaskStatus>("all");
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshPending, setRefreshPending] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [busyTaskId, setBusyTaskId] = useState<number | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [message, setMessage] = useState<Message | null>(null);
  const [connection, setConnection] = useState<ConnectionState>("idle");

  const loadTasks = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    setConnection("idle");
    try {
      setTasks(await listTasks());
      setConnection("online");
    } catch (error) {
      setTasks([]);
      setLoadError("无法读取任务，请确认 API 已启动后重试");
      setMessage({ text: getErrorMessage(error), tone: "error" });
      setConnection("error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadTasks();
  }, [loadTasks]);

  const connectionLabel = useMemo(() => {
    if (connection === "online") return "API 已连接";
    if (connection === "error") return "连接失败";
    return loading ? "正在连接" : "等待连接";
  }, [connection, loading]);

  async function handleCreate(title: string) {
    setSubmitting(true);
    setMessage({ text: "正在保存…", tone: "info" });
    try {
      const task = await createTask({ title });
      setTasks((current) => [...current, task]);
      setMessage({ text: "已添加到清单", tone: "info" });
      setConnection("online");
    } catch (error) {
      setMessage({ text: getErrorMessage(error), tone: "error" });
      setConnection("error");
      throw error;
    } finally {
      setSubmitting(false);
    }
  }

  async function handleToggle(task: Task) {
    setBusyTaskId(task.id);
    try {
      const updated = await updateTask(task.id, { completed: !task.completed });
      setTasks((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setConnection("online");
    } catch (error) {
      setMessage({ text: getErrorMessage(error), tone: "error" });
      setConnection("error");
    } finally {
      setBusyTaskId(null);
    }
  }

  async function handleDelete(task: Task) {
    if (!window.confirm(`确定删除“${task.title}”吗？`)) return;
    setBusyTaskId(task.id);
    try {
      await deleteTask(task.id);
      setTasks((current) => current.filter((item) => item.id !== task.id));
      setMessage({ text: "任务已删除", tone: "info" });
      setConnection("online");
    } catch (error) {
      setMessage({ text: getErrorMessage(error), tone: "error" });
      setConnection("error");
    } finally {
      setBusyTaskId(null);
    }
  }

  async function handleRefresh() {
    setRefreshPending(true);
    try {
      await loadTasks();
    } finally {
      setRefreshPending(false);
    }
  }

  return (
    <>
      <header className="site-header">
        <div className="header-inner">
          <a className="brand" href="./" aria-label="Task Garden 首页">
            <span className="brand-mark" aria-hidden="true">
              ✦
            </span>
            <span>Task Garden</span>
          </a>
          <span className="connection-status" data-state={connection}>
            <span className="status-dot" aria-hidden="true" />
            <span>{connectionLabel}</span>
          </span>
        </div>
      </header>

      <main className="page-shell">
        <section className="intro" aria-labelledby="page-title">
          <p className="eyebrow">WEEK 06 · REACT + TYPESCRIPT</p>
          <h1 id="page-title">
            把今天要做的事，<em>种</em>进清单里。
          </h1>
          <p className="intro-copy">
            React 组件负责界面结构，TypeScript 负责数据契约。每一次操作都会通过类型安全的 API 层同步到后端。
          </p>
        </section>

        <section className="workspace" aria-label="任务工作区">
          <div className="workspace-main">
            <section className="panel create-panel" aria-labelledby="create-title">
              <div className="section-heading">
                <div>
                  <p className="section-kicker">新增任务</p>
                  <h2 id="create-title">今天想完成什么？</h2>
                </div>
                <span className="shortcut-hint">Enter 提交</span>
              </div>
              <TaskForm submitting={submitting} onSubmit={handleCreate} />
              {message && (
                <p className="form-message" data-tone={message.tone} role="status" aria-live="polite">
                  {message.text}
                </p>
              )}
            </section>

            <TaskList
              tasks={tasks}
              filter={filter}
              keyword={keyword}
              loading={loading}
              error={loadError}
              refreshPending={refreshPending}
              busyTaskId={busyTaskId}
              onFilterChange={setFilter}
              onKeywordChange={setKeyword}
              onRefresh={() => void handleRefresh()}
              onToggle={(task) => void handleToggle(task)}
              onDelete={(task) => void handleDelete(task)}
            />
          </div>

          <aside className="panel tips-panel" aria-labelledby="tips-title">
            <p className="section-kicker">本周观察</p>
            <h2 id="tips-title">让组件响应你的动作</h2>
            <ul className="tips-list">
              <li>
                <span className="tip-icon" aria-hidden="true">01</span>
                <span>Props 描述组件边界，State 保存会随交互变化的数据。</span>
              </li>
              <li>
                <span className="tip-icon" aria-hidden="true">02</span>
                <span>TypeScript 类型让任务、事件和 API 响应在编译期更可靠。</span>
              </li>
              <li>
                <span className="tip-icon" aria-hidden="true">03</span>
                <span>加载、成功、空结果和失败状态都应该被用户看见。</span>
              </li>
            </ul>
            <div className="api-note">
              <span className="api-note-label">API 地址</span>
              <code>{API_BASE_URL}</code>
            </div>
          </aside>
        </section>
      </main>

      <footer className="site-footer">
        <span>Built with React · TypeScript · Vite</span>
        <a href={`${API_BASE_URL}/docs`} target="_blank" rel="noreferrer">
          查看 API 文档 →
        </a>
      </footer>
    </>
  );
}
