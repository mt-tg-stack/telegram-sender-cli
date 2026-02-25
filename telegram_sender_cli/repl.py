from __future__ import annotations

import asyncio
import os

from prompt_toolkit import PromptSession
from telegram_sender.client.runner import SenderRunner
from telegram_sender.client.sender.request import MessageRequest

from telegram_sender_cli.commands import (
    COMMAND_NAMES,
    MEDIA_COMMANDS,
    format_help,
    format_usage,
)
from telegram_sender_cli.completers import CombinedCompleter
from telegram_sender_cli.config import AppConfig, save_config
from telegram_sender_cli.utils.interaction import ask
from telegram_sender_cli.utils.parse import parse_targets
from telegram_sender_cli.utils.print import (
    console,
    print_response,
    targets_label,
)
from telegram_sender_cli.wizard.wizard import run_wizard


async def _result_consumer(
    runner: SenderRunner,
) -> None:
    try:
        async for resp in runner.results():
            chat_id: int | str | list[int] = "?"
            if resp.original is not None:
                msg = resp.original
                if isinstance(msg, list):
                    chat_id = (
                        [m.chat.id for m in msg]
                        if msg
                        else "?"
                    )
                else:
                    chat_id = msg.chat.id
            print_response(
                chat_id=chat_id, response=resp
            )
    except asyncio.CancelledError:
        pass
    except Exception as e:
        console.print(
            f"[red]Result consumer error: {e}[/red]"
        )


def _check_targets(targets: list[int | str]) -> bool:
    if not targets:
        console.print(
            "[yellow]No targets set."
            " Use /targets first.[/yellow]"
        )
        return False
    return True


async def run_repl(
    runner: SenderRunner,
    targets: list[int | str],
    config: AppConfig,
) -> None:
    session: PromptSession[str] = PromptSession()
    completer = CombinedCompleter()

    consumer_task = asyncio.create_task(
        _result_consumer(runner=runner)
    )

    console.print(
        "[bold green]REPL ready.[/bold green]"
        " Type a message or /help for commands."
    )

    try:
        while True:
            try:
                prompt_text = (
                    f"[{targets_label(targets=targets)}] > "
                )
                text = await ask(
                    text=prompt_text,
                    default="",
                    prompt_session=session,
                    converter=str,
                    completer=completer,
                )
            except (EOFError, KeyboardInterrupt):
                break

            if not text:
                continue

            # Commands
            if text.startswith("/"):
                parts = text.split(maxsplit=1)
                cmd = parts[0].lower()
                arg = (
                    parts[1].strip()
                    if len(parts) > 1
                    else ""
                )

                if cmd in ("/quit", "/exit"):
                    break

                if cmd == "/targets":
                    if not arg:
                        label = targets_label(
                            targets=targets
                        )
                        console.print(
                            f"Current targets: {label}"
                        )
                        continue
                    new_targets = parse_targets(text=arg)
                    if new_targets:
                        targets.clear()
                        targets.extend(new_targets)
                        label = targets_label(
                            targets=targets
                        )
                        console.print(
                            f"Targets set to: {label}"
                        )
                    else:
                        console.print(
                            "[yellow]No valid targets"
                            " provided[/yellow]"
                        )
                    continue

                if cmd == "/status":
                    label = targets_label(targets=targets)
                    console.print(
                        f"  Targets: {label}"
                    )
                    alive = not runner.task.done()
                    console.print(
                        f"  Runner task alive: {alive}"
                    )
                    continue

                if cmd in MEDIA_COMMANDS:
                    media_cmd = MEDIA_COMMANDS[cmd]
                    if not arg:
                        usage = format_usage(cmd=media_cmd)
                        console.print(
                            f"[yellow]Usage:"
                            f" {usage}[/yellow]"
                        )
                        continue

                    if not _check_targets(targets=targets):
                        continue

                    resolved = os.path.abspath(arg)
                    if not os.path.isfile(resolved):
                        console.print(
                            "[yellow]File not found:"
                            f" {resolved}[/yellow]"
                        )
                        continue

                    assert media_cmd.media_factory is not None
                    media = media_cmd.media_factory(resolved)

                    caption = await ask(
                        text="Caption (empty=none): ",
                        default=None,
                        prompt_session=session,
                        converter=str,
                    )

                    for target in targets:
                        req = MessageRequest(
                            chat_id=target,
                            text=caption,
                            media=media,
                        )
                        await runner.request(req)
                    continue

                if cmd == "/wizard":
                    config, should_save = await run_wizard(
                        config=config
                    )
                    if should_save:
                        save_config(config=config)
                        console.print(
                            "[green]Config saved"
                            " to config.toml[/green]"
                        )
                    targets.clear()
                    targets.extend(
                        config.chat_targets.targets
                    )
                    continue

                if cmd == "/help":
                    console.print(format_help())
                    continue

                console.print(
                    f"[yellow]Unknown command:"
                    f" {cmd}[/yellow]"
                )
                console.print(
                    f"Commands: {' '.join(COMMAND_NAMES)}"
                )
                continue

            # Plain text message
            if not _check_targets(targets=targets):
                continue

            for target in targets:
                req = MessageRequest(
                    chat_id=target, text=text
                )
                await runner.request(req)

    finally:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
