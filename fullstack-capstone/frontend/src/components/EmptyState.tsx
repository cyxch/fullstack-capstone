interface EmptyStateProps {
  state: "loading" | "empty" | "error";
  message: string;
}

export function EmptyState({ state, message }: EmptyStateProps) {
  return (
    <div className="list-state" data-state={state} role="status" aria-live="polite">
      <div className="loader" aria-hidden="true" hidden={state !== "loading"} />
      <p>{message}</p>
    </div>
  );
}
