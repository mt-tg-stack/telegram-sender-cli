from collections.abc import Callable
from typing import Any, TypeVar

from prompt_toolkit import PromptSession
from prompt_toolkit.validation import Validator

from telegram_sender_cli.wizard.validators import NoValidator

T = TypeVar("T")
DT = TypeVar("DT")


def prompt_default(current: object) -> str:
    if current is None:
        return ""
    return str(current)


async def ask(  # noqa: UP047
    text: str,
    default: DT,
    prompt_session: PromptSession[str],
    validator: Validator = NoValidator(),
    converter: Callable[[str], T] = str,  # type: ignore[assignment]
    **kwargs: Any,
) -> T | DT:
    val_str = await prompt_session.prompt_async(
        message=text,
        default=prompt_default(current=default),
        validator=validator,
        validate_while_typing=False,
        **kwargs,
    )
    if val_str.strip():
        return converter(val_str.strip())
    return default


def str_resolver(output: str) -> str:
    return output.strip()


def output_match(  # noqa: UP047
    output: T,
    *types: T,
    resolver: Callable[[T], T] = str_resolver,  # type: ignore[assignment]
) -> bool:
    return resolver(output) in types


def output_yes(output: str) -> bool:
    return output_match(output, "y", "yes")
