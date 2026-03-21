"use client";

import { useEffect, useState, useCallback } from "react";
import { supabase } from "@/lib/supabase";
import type { Todo } from "@/lib/types";
import { TodoCard } from "@/components/todo-card";
import { AddTodo } from "@/components/add-todo";

type Filter = "all" | "pending" | "in_progress" | "done";

export default function Dashboard() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [filter, setFilter] = useState<Filter>("all");
  const [connected, setConnected] = useState(false);

  const fetchTodos = useCallback(async () => {
    const { data } = await supabase
      .from("todos")
      .select("*")
      .order("created_at", { ascending: false });
    if (data) setTodos(data as Todo[]);
  }, []);

  useEffect(() => {
    fetchTodos();

    const channel = supabase
      .channel("todos-realtime")
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "todos" },
        (payload) => {
          if (payload.eventType === "INSERT") {
            setTodos((prev) => [payload.new as Todo, ...prev]);
          } else if (payload.eventType === "UPDATE") {
            setTodos((prev) =>
              prev.map((t) =>
                t.id === (payload.new as Todo).id ? (payload.new as Todo) : t
              )
            );
          } else if (payload.eventType === "DELETE") {
            setTodos((prev) =>
              prev.filter((t) => t.id !== (payload.old as Todo).id)
            );
          }
        }
      )
      .subscribe((status) => {
        setConnected(status === "SUBSCRIBED");
      });

    return () => {
      supabase.removeChannel(channel);
    };
  }, [fetchTodos]);

  const filtered =
    filter === "all" ? todos : todos.filter((t) => t.status === filter);

  const counts = {
    all: todos.length,
    pending: todos.filter((t) => t.status === "pending").length,
    in_progress: todos.filter((t) => t.status === "in_progress").length,
    done: todos.filter((t) => t.status === "done").length,
  };

  const filters: { key: Filter; label: string }[] = [
    { key: "all", label: "All" },
    { key: "pending", label: "Pending" },
    { key: "in_progress", label: "In Progress" },
    { key: "done", label: "Done" },
  ];

  return (
    <main className="mx-auto max-w-3xl px-4 py-12">
      <header className="mb-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Todos</h1>
            <p className="text-sm text-[var(--muted)] mt-1">
              {todos.length} task{todos.length !== 1 && "s"}
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-[var(--muted)]">
            <span
              className={`inline-block w-2 h-2 rounded-full ${
                connected
                  ? "bg-[var(--green)] animate-pulse-dot"
                  : "bg-[var(--red)]"
              }`}
            />
            {connected ? "Live" : "Connecting..."}
          </div>
        </div>
      </header>

      <AddTodo />

      <nav className="flex gap-1 mt-8 mb-6">
        {filters.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              filter === key
                ? "bg-[var(--foreground)] text-[var(--background)]"
                : "text-[var(--muted)] hover:text-[var(--foreground)] hover:bg-[var(--accent)]"
            }`}
          >
            {label}
            <span className="ml-1.5 opacity-50">{counts[key]}</span>
          </button>
        ))}
      </nav>

      <div className="space-y-2">
        {filtered.length === 0 ? (
          <p className="text-sm text-[var(--muted)] py-12 text-center">
            {filter === "all"
              ? "No tasks yet."
              : `No ${filter.replace("_", " ")} tasks.`}
          </p>
        ) : (
          filtered.map((todo) => <TodoCard key={todo.id} todo={todo} />)
        )}
      </div>
    </main>
  );
}
