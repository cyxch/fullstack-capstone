import type { Task } from "../types";

interface TaskItemProps {
  task: Task;
  busy: boolean;
  onToggle: (task: Task) => void;
  onDelete: (task: Task) => void;
}

export function TaskItem({ task, busy, onToggle, onDelete }: TaskItemProps) {
  return (
    <li className={`task-item${task.completed ? " is-completed" : ""}`}>
      <button
        className="task-checkbox"
        type="button"
        aria-pressed={task.completed}
        aria-label={`${task.completed ? "标记任务未完成" : "完成任务"}：${task.title}`}
        disabled={busy}
        onClick={() => onToggle(task)}
      />
      <p className="task-title">{task.title}</p>
      <div className="task-actions">
        <button
          className="icon-button"
          type="button"
          aria-label={`删除任务：${task.title}`}
          disabled={busy}
          onClick={() => onDelete(task)}
        >
          ×
        </button>
      </div>
    </li>
  );
}
