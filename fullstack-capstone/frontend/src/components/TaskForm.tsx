import { useState, type FormEvent } from "react";

interface TaskFormProps {
  submitting: boolean;
  onSubmit: (title: string) => Promise<void>;
}

export function TaskForm({ submitting, onSubmit }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [validationMessage, setValidationMessage] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalizedTitle = title.trim();
    if (!normalizedTitle) {
      setValidationMessage("请输入任务标题");
      return;
    }
    setValidationMessage("");
    try {
      await onSubmit(normalizedTitle);
      setTitle("");
    } catch {
      // The parent renders the API error and keeps the user's input for retry.
    }
  }

  return (
    <>
      <form className="task-form" onSubmit={handleSubmit}>
        <label className="sr-only" htmlFor="task-title">
          任务标题
        </label>
        <input
          id="task-title"
          name="title"
          type="text"
          maxLength={120}
          autoComplete="off"
          placeholder="例如：完成 TypeScript 类型练习"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          required
        />
        <button className="button button-primary" type="submit" disabled={submitting}>
          <span aria-hidden="true">＋</span>
          {submitting ? "保存中…" : "添加任务"}
        </button>
      </form>
      {validationMessage && (
        <p className="form-message" data-tone="error" role="alert">
          {validationMessage}
        </p>
      )}
    </>
  );
}
