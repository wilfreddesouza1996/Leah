import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from leah.agent import LeahAgent
from leah.config import settings


def main() -> None:
    console = Console()

    console.print(
        Panel(
            "[bold cyan]Leah[/bold cyan] is ready.\n"
            "[dim]Type your message and press Enter. Ctrl+C or 'bye' to exit.[/dim]",
            border_style="cyan",
        )
    )

    try:
        agent = LeahAgent()
    except Exception as e:
        console.print(f"[red]Failed to start:[/red] {e}")
        sys.exit(1)

    session: PromptSession = PromptSession(
        history=FileHistory(".leah_history"),
    )

    while True:
        try:
            user_input = session.prompt("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Leah: Later.[/dim]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("bye", "exit", "quit"):
            console.print("\n[dim]Leah: Later.[/dim]")
            break

        try:
            response = agent.chat(user_input)
        except Exception as e:
            console.print(f"\n[red]Error:[/red] {e}")
            continue

        console.print(f"\n[bold cyan]Leah:[/bold cyan]")
        console.print(Markdown(response))


if __name__ == "__main__":
    main()
