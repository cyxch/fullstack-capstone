const DEFAULT_API_URL = "http://127.0.0.1:8000";
const API_URL = (window.TASK_API_BASE_URL || DEFAULT_API_URL).replace(/\/$/, "");

const state = {
  tasks: [],
  filter: "all",
  keyword: "",
  loading: false,
};

const elements = {
  apiUrlLabel: document.querySelector("#api-url-label"),
  connectionLabel: document.querySelector("#connection-label"),
  connectionStatus: document.querySelector("#connection-status"),
  form: document.querySelector("#task-form"),
  formMessage: document.querySelector("#form-message"),
  input: document.querySelector("#task-title"),
  list: document.querySelector("#task-list"),
  listState: document.querySelector("#list-state"),
  count: document.querySelector("#task-count"),
  refresh: document.querySelector("#refresh-button"),
  search: document.querySelector("#search-input"),
  filters: [...document.querySelectorAll("[data-filter]")],
};

elements.apiUrlLabel.textContent = API_URL;

function setConnectionStatus(status, label) {
  elements.connectionStatus.dataset.state = status;
  elements.connectionLabel.textContent = label;
}

function setFormMessage(message = "", tone = "") {
  elements.formMessage.textContent = message;
  if (tone) {
    elements.formMessage.dataset.tone = tone;
  } else {
    delete elements.formMessage.dataset.tone;
  }
}

function showListState(type, message) {
  elements.listState.dataset.state = type;
  elements.listState.querySelector("p").textContent = message;
  elements.listState.querySelector(".loader").hidden = type !== "loading";
}

function visibleTasks() {
  const normalizedKeyword = state.keyword.trim().toLocaleLowerCase();
  return state.tasks.filter((task) => {
    const matchesFilter =
      state.filter === "all" ||
      (state.filter === "pending" && !task.completed) ||
      (state.filter === "completed" && task.completed);
    const matchesKeyword =
      !normalizedKeyword || task.title.toLocaleLowerCase().includes(normalizedKeyword);
    return matchesFilter && matchesKeyword;
  });
}

function renderTask(task) {
  const item = document.createElement("li");
  item.className = "task-item";
  item.dataset.taskId = task.id;
  if (task.completed) {
    item.classList.add("is-completed");
  }

  const checkbox = document.createElement("button");
  checkbox.className = "task-checkbox";
  checkbox.type = "button";
  checkbox.dataset.action = "toggle";
  checkbox.setAttribute("aria-pressed", String(task.completed));
  checkbox.setAttribute(
    "aria-label",
    (task.completed ? "标记任务“" : "完成任务“") + task.title + "”",
  );

  const title = document.createElement("p");
  title.className = "task-title";
  title.textContent = task.title;

  const actions = document.createElement("div");
  actions.className = "task-actions";
  const removeButton = document.createElement("button");
  removeButton.className = "icon-button";
  removeButton.type = "button";
  removeButton.dataset.action = "delete";
  removeButton.setAttribute("aria-label", "删除任务“" + task.title + "”");
  removeButton.textContent = "×";
  actions.append(removeButton);
  item.append(checkbox, title, actions);
  return item;
}

function render() {
  const tasks = visibleTasks();
  elements.count.textContent = String(state.tasks.length);
  elements.list.replaceChildren(...tasks.map(renderTask));
  if (state.loading) {
    showListState("loading", "正在读取任务…");
  } else if (!tasks.length) {
    const message =
      state.keyword || state.filter !== "all" ? "没有匹配的任务" : "还没有任务，先添加一件吧";
    showListState("empty", message);
  } else {
    showListState("hidden", "");
  }
}

function errorMessage(error) {
  return error instanceof Error ? error.message : "请求失败，请稍后重试";
}

async function request(path, options = {}) {
  const headers = { ...options.headers };
  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(API_URL + path, {
    ...options,
    headers,
  });
  if (!response.ok) {
    let message = "请求失败（" + response.status + "）";
    try {
      const payload = await response.json();
      message = payload.error?.message || message;
    } catch {
      // A non-JSON response still gets the HTTP status message above.
    }
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}

async function loadTasks() {
  state.loading = true;
  render();
  setConnectionStatus("idle", "正在连接");
  try {
    state.tasks = await request("/tasks");
    setConnectionStatus("online", "API 已连接");
  } catch (error) {
    state.tasks = [];
    setConnectionStatus("error", "连接失败");
    showListState("error", errorMessage(error));
  } finally {
    state.loading = false;
    render();
    if (elements.connectionStatus.dataset.state === "error") {
      showListState("error", "无法读取任务，请确认 API 已启动后重试");
    }
  }
}

async function createTask(event) {
  event.preventDefault();
  const title = elements.input.value.trim();
  if (!title) {
    setFormMessage("请输入任务标题", "error");
    elements.input.focus();
    return;
  }

  const submit = elements.form.querySelector("button[type='submit']");
  submit.disabled = true;
  setFormMessage("正在保存…");
  try {
    const task = await request("/tasks", {
      method: "POST",
      body: JSON.stringify({ title }),
    });
    state.tasks.push(task);
    elements.form.reset();
    setFormMessage("已添加到清单");
    setConnectionStatus("online", "API 已连接");
    render();
    elements.input.focus();
  } catch (error) {
    setFormMessage(errorMessage(error), "error");
    setConnectionStatus("error", "请求失败");
  } finally {
    submit.disabled = false;
  }
}

async function toggleTask(task) {
  try {
    const updated = await request("/tasks/" + task.id, {
      method: "PUT",
      body: JSON.stringify({ completed: !task.completed }),
    });
    state.tasks = state.tasks.map((item) => (item.id === updated.id ? updated : item));
    setConnectionStatus("online", "API 已连接");
    render();
  } catch (error) {
    setFormMessage(errorMessage(error), "error");
    setConnectionStatus("error", "请求失败");
  }
}

async function deleteTask(task) {
  if (!window.confirm("确定删除“" + task.title + "”吗？")) {
    return;
  }
  try {
    await request("/tasks/" + task.id, { method: "DELETE" });
    state.tasks = state.tasks.filter((item) => item.id !== task.id);
    setFormMessage("任务已删除");
    setConnectionStatus("online", "API 已连接");
    render();
  } catch (error) {
    setFormMessage(errorMessage(error), "error");
    setConnectionStatus("error", "请求失败");
  }
}

elements.form.addEventListener("submit", createTask);
elements.refresh.addEventListener("click", loadTasks);
elements.search.addEventListener("input", (event) => {
  state.keyword = event.target.value;
  render();
});
elements.filters.forEach((button) => {
  button.addEventListener("click", () => {
    state.filter = button.dataset.filter;
    elements.filters.forEach((item) => {
      const isActive = item === button;
      item.classList.toggle("is-active", isActive);
      item.setAttribute("aria-pressed", String(isActive));
    });
    render();
  });
});
elements.list.addEventListener("click", (event) => {
  const action = event.target.closest("[data-action]")?.dataset.action;
  const item = event.target.closest("[data-task-id]");
  if (!action || !item) {
    return;
  }
  const task = state.tasks.find((candidate) => candidate.id === Number(item.dataset.taskId));
  if (!task) {
    return;
  }
  if (action === "toggle") {
    toggleTask(task);
  } else if (action === "delete") {
    deleteTask(task);
  }
});

loadTasks();
