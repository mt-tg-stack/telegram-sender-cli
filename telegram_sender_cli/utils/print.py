from __future__ import annotations

from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from telegram_sender.client.sender.response import MessageResponse

from telegram_sender_cli.config import AppConfig

console = Console()
INDENT = 4


def targets_label(targets: list[int | str]) -> str:
    if not targets:
        return "[no targets]"
    return ",".join(str(t) for t in targets)


def print_header(text: str, sub_step: int = 0) -> None:
    indent = sub_step * INDENT

    panel = Panel(
        f"[bold cyan]{text}[/bold cyan]",
        expand=False,
    )

    console.print(Padding(panel, (0, 0, 0, indent)))


def print_response(
    chat_id: int | str | list[int],
    response: MessageResponse,
) -> None:

    if isinstance(chat_id, list):
        chat_id = ", ".join(str(cid) for cid in chat_id)

    if response.error is None:
        assert response.original is not None
        if isinstance(response.original, list):
            msg_id = ", ".join(
                str(m.id) for m in response.original
            )
        else:
            msg_id = str(response.original.id)
        console.print(
            f"  [green]\u2713[/green] [bold]{chat_id}[/bold]"
            f" \u2192 message_id={msg_id}"
        )
    else:
        console.print(
            f"  [red]\u2717[/red] [bold]{chat_id}[/bold]"
            f" \u2192 {response.error}"
        )


def print_config(config: AppConfig) -> None:
    table = Table(
        title="Current Configuration",
        show_header=False,
        expand=False,
    )
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("session.name", config.session.name)
    table.add_row(
        "session.api_id", str(config.session.api_id or "")
    )
    table.add_row(
        "session.api_hash", config.session.api_hash or ""
    )

    for proxy in config.proxy.proxies:
        scheme = proxy.get("scheme", config.proxy.default_scheme)
        host = proxy.get("host", config.proxy.default_host)
        port = proxy.get("port", config.proxy.default_port)
        username = proxy.get(
            "username", config.proxy.default_username
        )
        secret = proxy.get(
            "secret", config.proxy.default_secret
        )
        password = proxy.get(
            "password", config.proxy.default_password
        )

        table.add_row("proxy.scheme", scheme)
        table.add_row("proxy.host", host)
        table.add_row("proxy.port", str(port))
        if username:
            table.add_row("proxy.username", username)
        if secret:
            table.add_row("proxy.secret", secret)
        if password:
            table.add_row("proxy.password", password)

    strategies = config.strategies
    table.add_row("strategies.delay", str(strategies.delay))
    table.add_row(
        "strategies.rate_limit", str(strategies.rate_limit)
    )
    table.add_row(
        "strategies.rate_period", str(strategies.rate_period)
    )
    table.add_row(
        "strategies.timeout", str(strategies.timeout)
    )
    table.add_row(
        "strategies.retry_attempts",
        str(strategies.retry_attempts),
    )
    table.add_row(
        "strategies.retry_delay", str(strategies.retry_delay)
    )
    if strategies.jitter_ratio is not None:
        table.add_row(
            "strategies.jitter_ratio",
            str(strategies.jitter_ratio),
        )

    chat_targets = config.chat_targets.targets

    for chat_target in chat_targets:
        table.add_row("Chat target", str(chat_target))

    console.print(table)
