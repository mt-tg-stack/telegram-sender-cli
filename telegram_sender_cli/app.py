from __future__ import annotations

from telegram_sender_cli.config import (
    AppConfig,
    build_runner,
    build_sender,
    build_strategies,
    load_config,
    save_config,
)
from telegram_sender_cli.repl import run_repl
from telegram_sender_cli.utils.print import console, print_header
from telegram_sender_cli.wizard.wizard import run_wizard


async def main() -> None:
    try:
        print_header(text="[bold]telegram-sender-cli[/bold]\n")

        config = load_config() or AppConfig()
        config, should_save = await run_wizard(config=config)
        targets = config.chat_targets.targets

        if should_save:
            save_config(config=config)
            console.print("[green]Config saved to config.toml[/green]")

        strategies = build_strategies(cfg=config.strategies)
        sender = build_sender(cfg=config)

        console.print("\n[dim]Starting sender...[/dim]")
        async with build_runner(
            sender=sender, strategies=strategies
        ) as runner:
            await run_repl(runner=runner, targets=targets, config=config)
    finally:
        console.print("[dim]Goodbye.[/dim]")
