export type TaskStatus = "all" | "pending" | "completed";

export interface Task {
  id: number;
  title: string;
  completed: boolean;
}

export interface TaskCreate {
  title: string;
}

export interface TaskUpdate {
  title?: string;
  completed?: boolean;
}

export interface ApiErrorBody {
  error?: {
    code?: string;
    message?: string;
  };
}

export class ApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}
