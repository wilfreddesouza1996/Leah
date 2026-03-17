import anthropic

from leah.config import settings
from leah.memory import ConversationMemory
from leah.personality import get_system_prompt
from leah.tools import TOOL_DEFINITIONS, execute_tool, initialize_services


class LeahAgent:
    """Core agent: manages the Claude API conversation loop with tool dispatch."""

    def __init__(self) -> None:
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.memory = ConversationMemory(max_messages=settings.leah_max_memory_messages)
        initialize_services(settings)

    def chat(self, user_input: str) -> str:
        """Send a user message and return Leah's final text response.

        Handles multi-step tool_use loops automatically: keeps calling Claude
        until stop_reason is 'end_turn', dispatching any tool calls in between.
        """
        self.memory.add_user(user_input)
        system = get_system_prompt(
            timezone=settings.leah_user_timezone,
            name=settings.leah_user_name,
        )

        while True:
            response = self.client.messages.create(
                model=settings.leah_model,
                max_tokens=4096,
                system=system,
                messages=self.memory.get_messages(),
                tools=TOOL_DEFINITIONS if TOOL_DEFINITIONS else [],
            )

            if response.stop_reason == "end_turn":
                text = _extract_text(response.content)
                self.memory.add_assistant(response.content)
                return text

            elif response.stop_reason == "tool_use":
                self.memory.add_assistant(response.content)
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = execute_tool(block.name, block.input)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(result),
                            }
                        )
                self.memory.add_tool_results(tool_results)

            else:
                # Unexpected stop reason — return whatever text we have
                return _extract_text(response.content) or f"[stopped: {response.stop_reason}]"


def _extract_text(content_blocks) -> str:
    """Pull plain text out of a list of content blocks."""
    parts = []
    for block in content_blocks:
        if hasattr(block, "type") and block.type == "text":
            parts.append(block.text)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block["text"])
    return "\n".join(parts).strip()
