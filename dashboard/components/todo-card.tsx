"use client";

import { supabase } from "@/lib/supabase";
import type { Todo } from "@/lib/types";

const statusConfig = {
  pending: { label: "Pending", color: "bg-zinc-200 text-zinc-600" },
  in_progress: { label: "In Progress", color: "bg-blue-100 text-blue-700" },
  done: { label: "Done", color: "bg-emerald-100 text-emerald-700" },
};

const priorityConfig = {
  low: { label: "Low", dot: "bg-zinc-300" },
  medium: { label: "Med", dot: "bg-amber-400" },
  high: { label: "High", dot: "bg-red-500" },
};

const nextStatus: Record<Todo["status"], Todo["status"]> = {
  pending: "in_progress",
  in_progress: "done",
  done: "pending",
};

export function TodoCard({ todo }: { todo: Todo }) {
  const status = statusConfig[todo.status];
  const priority = priorityConfig[todo.priority];

  async function cycleStatus() {
    await supabase
      .from("todos")
      .update({ status: nextStatus[todo.status] })
      .eq("id", todo.id);
  }

  async function deleteTodo() {
    await supabase.from("todos").delete().eq("id", todo.id);
  }

  const age = formatAge(todo.updated_at);

  return (
    <div
      className={`group flex items-center gap-3 px-4 py-3 rounded-lg border border-[var(--border)] bg-white hover:border-zinc-300 transition-all animate-fade-in ${
        todo.status === "done" ? "opacity-50" : ""
      }`}
    >
      <button
        onClick={cycleStatus}
        className={`shrink-0 w-5 h-5 rounded-full border-2 transition-colors flex items-center justify-center ${
          todo.status === "done"
            ? "border-emerald-500 bg-emerald-500 text-white"
            : todo.status === "in_progress"
            ? "border-blue-400 bg-blue-50"
            : "border-zinc-300 hover:border-zinc-400"
        }`}
        title={`Mark as ${nextStatus[todo.status].replace("_", " ")}`}
      >
        {todo.status === "done" && (
          <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
            <path
              d="M2.5 6L5 8.5L9.5 3.5"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
        {todo.status === "in_progress" && (
          <span className="w-2 h-2 rounded-full bg-blue-400" />
        )}
      </button>

      <div className="flex-1 min-w-0">
        <p
          className={`text-sm font-medium truncate ${
            todo.status === "done" ? "line-through text-[var(--muted)]" : ""
          }`}
        >
          {todo.title}
        </p>
        <div className="flex items-center gap-2 mt-1">
          {todo.assigned_agent && (
            <span className="text-xs text-[var(--muted)]">
              {todo.assigned_agent}
            </span>
          )}
          <span className="text-xs text-[var(--muted)]">{age}</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <span className="flex items-center gap-1 text-xs text-[var(--muted)]">
          <span className={`w-1.5 h-1.5 rounded-full ${priority.dot}`} />
          {priority.label}
        </span>
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium ${status.color}`}
        >
          {status.label}
        </span>
        <button
          onClick={deleteTodo}
          className="opacity-0 group-hover:opacity-100 text-[var(--muted)] hover:text-[var(--red)] transition-all text-sm px-1"
          title="Delete"
        >
          &times;
        </button>
      </div>
    </div>
  );
}

function formatAge(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}
