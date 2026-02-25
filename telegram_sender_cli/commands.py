from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from telegram_sender.types import (
    Animation,
    Audio,
    Document,
    Media,
    Photo,
    Sticker,
    Video,
    Voice,
)


@dataclass(frozen=True, slots=True)
class Command:
    name: str
    description: str
    args: str | None = None
    media_factory: Callable[[str], Media] | None = None


COMMAND_LIST: list[Command] = [
    Command(
        name="/photo",
        args="<file_path>",
        description="Send a photo",
        media_factory=lambda path: Photo(photo=path),
    ),
    Command(
        name="/video",
        args="<file_path>",
        description="Send a video",
        media_factory=lambda path: Video(video=path),
    ),
    Command(
        name="/doc",
        args="<file_path>",
        description="Send a document",
        media_factory=lambda path: Document(document=path),
    ),
    Command(
        name="/audio",
        args="<file_path>",
        description="Send an audio file",
        media_factory=lambda path: Audio(audio=path),
    ),
    Command(
        name="/sticker",
        args="<file_path>",
        description="Send a sticker",
        media_factory=lambda path: Sticker(sticker=path),
    ),
    Command(
        name="/voice",
        args="<file_path>",
        description="Send a voice message",
        media_factory=lambda path: Voice(voice=path),
    ),
    Command(
        name="/animation",
        args="<file_path>",
        description="Send an animation (GIF)",
        media_factory=lambda path: Animation(animation=path),
    ),
    Command(
        name="/targets",
        args="<id,@user,...>",
        description="Show or set targets",
    ),
    Command(
        name="/status",
        description="Show runner status",
    ),
    Command(
        name="/wizard",
        description="Start configuration wizard",
    ),
    Command(
        name="/help",
        description="Show available commands",
    ),
    Command(
        name="/quit",
        description="Exit the REPL",
    ),
    Command(
        name="/exit",
        description="Exit the REPL",
    ),
]

COMMAND_MAP: dict[str, Command] = {cmd.name: cmd for cmd in COMMAND_LIST}

MEDIA_COMMANDS: dict[str, Command] = {
    cmd.name: cmd for cmd in COMMAND_LIST if cmd.media_factory is not None
}

COMMAND_NAMES: list[str] = [cmd.name for cmd in COMMAND_LIST]


def format_usage(cmd: Command) -> str:
    if cmd.args:
        return f"{cmd.name} {cmd.args}"
    return cmd.name


def format_help() -> str:
    lines = ["[bold]Commands:[/bold]"]
    for cmd in COMMAND_LIST:
        usage = format_usage(cmd=cmd)
        lines.append(f"  {usage:<28} {cmd.description}")
    return "\n".join(lines)
