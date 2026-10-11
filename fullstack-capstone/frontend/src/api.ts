import type { ApiErrorBody, Task, TaskCreate, TaskUpdate } from "./types";
import { ApiError } from "./types";

const DEFAULT_API_URL = "http://127.0.0.1:8000";

declare global {
  interface Window {
    TASK_API_BASE_URL?: string;
  }
}

export const API_BASE_URL = (
  window.TASK_API_BASE_URL ?? import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_URL
).replace(/\/$/, "");

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let body: ApiErrorBody = {};
    try {
      body = (await response.json()) as ApiErrorBody;
    } catch {
      // Keep the HTTP status as the fallback when the response is not JSON.
    }
    const message = body.error?.message ?? `请求失败（HTTP ${response.status}）`;
    throw new ApiError(message, response.status, body.error?.code);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export function listTasks(): Promise<Task[]> {
  return request<Task[]>("/tasks");
}

export function createTask(payload: TaskCreate): Promise<Task> {
  return request<Task>("/tasks", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateTask(id: number, payload: TaskUpdate): Promise<Task> {
  return request<Task>(`/tasks/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteTask(id: number): Promise<void> {
  return request<void>(`/tasks/${id}`, { method: "DELETE" });
}
