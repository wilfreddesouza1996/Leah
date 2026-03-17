class ConversationMemory:
    """In-memory conversation history for a single session.

    Stores messages in the format the Claude API expects.
    Trims oldest user+assistant pairs when the message count exceeds the limit
    to keep context window usage bounded.
    """

    def __init__(self, max_messages: int = 100) -> None:
        self._messages: list[dict] = []
        self.max_messages = max_messages

    def add_user(self, content: str) -> None:
        self._messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant(self, content) -> None:
        """content can be a str or a list of content blocks (text + tool_use)."""
        self._messages.append({"role": "assistant", "content": content})

    def add_tool_results(self, tool_results: list[dict]) -> None:
        """Appends tool results as a user-role message (required by Claude API)."""
        self._messages.append({"role": "user", "content": tool_results})

    def get_messages(self) -> list[dict]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)

    def _trim(self) -> None:
        """Remove the oldest user+assistant pair when over the limit."""
        while len(self._messages) > self.max_messages:
            # Drop the two oldest messages (a user+assistant pair)
            self._messages = self._messages[2:]
