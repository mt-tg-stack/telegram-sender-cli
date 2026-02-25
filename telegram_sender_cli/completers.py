from __future__ import annotations

from collections.abc import Iterator

from prompt_toolkit.completion import (
    CompleteEvent,
    Completer,
    Completion,
    PathCompleter,
)
from prompt_toolkit.document import Document

from telegram_sender_cli.commands import COMMAND_NAMES, MEDIA_COMMANDS


class CommandCompleter(Completer):
    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterator[Completion]:
        text = document.text_before_cursor
        if " " not in text and text.startswith("/"):
            for name in COMMAND_NAMES:
                if name.startswith(text):
                    yield Completion(
                        text=name,
                        start_position=-len(text),
                    )


class MediaPathCompleter(Completer):
    def __init__(self) -> None:
        self._path_completer = PathCompleter(expanduser=True)

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterator[Completion]:
        text = document.text_before_cursor
        parts = text.split(maxsplit=1)
        if len(parts) == 2 and parts[0] in MEDIA_COMMANDS:
            path_text = parts[1]
            sub_doc = Document(
                text=path_text,
                cursor_position=len(path_text),
            )
            yield from self._path_completer.get_completions(
                sub_doc, complete_event
            )


class CombinedCompleter(Completer):
    def __init__(self) -> None:
        self._command = CommandCompleter()
        self._media_path = MediaPathCompleter()

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterator[Completion]:
        text = document.text_before_cursor
        if " " not in text:
            yield from self._command.get_completions(
                document, complete_event
            )
        else:
            yield from self._media_path.get_completions(
                document, complete_event
            )
