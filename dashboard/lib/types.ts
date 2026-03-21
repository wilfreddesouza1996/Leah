export type Todo = {
  id: string;
  title: string;
  status: "pending" | "in_progress" | "done";
  priority: "low" | "medium" | "high";
  assigned_agent: string | null;
  updated_at: string;
  created_at: string;
};

export type Database = {
  public: {
    Tables: {
      todos: {
        Row: Todo;
        Insert: Omit<Todo, "id" | "updated_at" | "created_at"> & {
          id?: string;
          updated_at?: string;
          created_at?: string;
        };
        Update: Partial<Omit<Todo, "id">>;
      };
    };
  };
};
