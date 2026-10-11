import type { Task, TaskStatus } from "../types";
import { EmptyState } from "./EmptyState";
import { TaskItem } from "./TaskItem";

interface TaskListProps {
  tasks: Task[];
  filter: TaskStatus;
  keyword: string;
  loading: boolean;
  error: string | null;
  refreshPending: boolean;
  busyTaskId: number | null;
  onFilterChange: (filter: TaskStatus) => void;
  onKeywordChange: (keyword: string) => void;
  onRefresh: () => void;
  onToggle: (task: Task) => void;
  onDelete: (task: Task) => void;
}

const filters: Array<{ value: TaskStatus; label: string }> = [
  { value: "all", label: "全部" },
  { value: "pending", label: "待完成" },
  { value: "completed", label: "已完成" },
];

export function TaskList({
  tasks,
  filter,
  keyword,
  loading,
  error,
  refreshPending,
  busyTaskId,
  onFilterChange,
  onKeywordChange,
  onRefresh,
  onToggle,
  onDelete,
}: TaskListProps) {
  const normalizedKeyword = keyword.trim().toLocaleLowerCase();
  const visibleTasks = tasks.filter((task) => {
    const matchesFilter =
      filter === "all" ||
      (filter === "pending" && !task.completed) ||
      (filter === "completed" && task.completed);
    const matchesKeyword =
      !normalizedKeyword || task.title.toLocaleLowerCase().includes(normalizedKeyword);
    return matchesFilter && matchesKeyword;
  });

  let state: "loading" | "empty" | "error" | null = null;
  let stateMessage = "";
  if (loading) {
    state = "loading";
    stateMessage = "正在读取任务…";
  } else if (error) {
    state = "error";
    stateMessage = error;
  } else if (!visibleTasks.length) {
    state = "empty";
    stateMessage = keyword || filter !== "all" ? "没有匹配的任务" : "还没有任务，先添加一件吧";
  }

  return (
    <section className="panel list-panel" aria-labelledby="list-title">
      <div className="list-heading">
        <div>
          <p className="section-kicker">我的清单</p>
          <h2 id="list-title">{tasks.length} 个任务</h2>
        </div>
        <button className="button button-ghost" type="button" onClick={onRefresh} disabled={refreshPending}>
          <span aria-hidden="true">↻</span>
          {refreshPending ? "刷新中…" : "刷新"}
        </button>
      </div>

      <div className="list-tools">
        <div className="filter-group" role="group" aria-label="任务状态筛选">
          {filters.map((item) => (
            <button
              className={`filter-button${filter === item.value ? " is-active" : ""}`}
              type="button"
              aria-pressed={filter === item.value}
              key={item.value}
              onClick={() => onFilterChange(item.value)}
            >
              {item.label}
            </button>
          ))}
        </div>
        <label className="search-box">
          <span aria-hidden="true">⌕</span>
          <span className="sr-only">搜索任务</span>
          <input
            type="search"
            placeholder="搜索标题"
            autoComplete="off"
            value={keyword}
            onChange={(event) => onKeywordChange(event.target.value)}
          />
        </label>
      </div>

      {state ? (
        <EmptyState state={state} message={stateMessage} />
      ) : (
        <ul className="task-list" aria-label="任务列表">
          {visibleTasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              busy={busyTaskId === task.id}
              onToggle={onToggle}
              onDelete={onDelete}
            />
          ))}
        </ul>
      )}
    </section>
  );
}
