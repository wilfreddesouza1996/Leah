"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";
import type { Todo } from "@/lib/types";

export function AddTodo() {
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState<Todo["priority"]>("medium");
  const [agent, setAgent] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) return;

    setSubmitting(true);
    await supabase.from("todos").insert({
      title: trimmed,
      priority,
      assigned_agent: agent.trim() || null,
      status: "pending",
    });
    setTitle("");
    setAgent("");
    setPriority("medium");
    setSubmitting(false);
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="New task..."
        className="flex-1 px-3 py-2 text-sm rounded-lg border border-[var(--border)] bg-white placeholder:text-[var(--muted)] focus:outline-none focus:ring-2 focus:ring-zinc-900/10"
      />
      <input
        type="text"
        value={agent}
        onChange={(e) => setAgent(e.target.value)}
        placeholder="Agent"
        className="w-28 px-3 py-2 text-sm rounded-lg border border-[var(--border)] bg-white placeholder:text-[var(--muted)] focus:outline-none focus:ring-2 focus:ring-zinc-900/10"
      />
      <select
        value={priority}
        onChange={(e) => setPriority(e.target.value as Todo["priority"])}
        className="px-3 py-2 text-sm rounded-lg border border-[var(--border)] bg-white text-[var(--foreground)] focus:outline-none focus:ring-2 focus:ring-zinc-900/10"
      >
        <option value="low">Low</option>
        <option value="medium">Med</option>
        <option value="high">High</option>
      </select>
      <button
        type="submit"
        disabled={submitting || !title.trim()}
        className="px-4 py-2 text-sm font-medium rounded-lg bg-[var(--foreground)] text-[var(--background)] hover:opacity-90 transition-opacity disabled:opacity-30"
      >
        Add
      </button>
    </form>
  );
}
