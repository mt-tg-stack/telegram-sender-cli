from prompt_toolkit import PromptSession

from telegram_sender_cli.config import ChatTargetsConfig
from telegram_sender_cli.utils.interaction import ask
from telegram_sender_cli.utils.parse import parse_targets
from telegram_sender_cli.wizard.validators import (
    ChatTargetValidator,
)


async def store_chat_targets(
    prompt_session: PromptSession[str], config: ChatTargetsConfig
) -> None:
    targets_input = await ask(
        text="Chat targets (comma-separated IDs or @usernames): ",
        default="",
        prompt_session=prompt_session,
        validator=ChatTargetValidator(),
        converter=str,
    )
    new_targets = parse_targets(text=targets_input)
    targets: list[int | str] = [*config.targets]
    for target in new_targets:
        if target not in targets:
            targets.append(target)

    if targets:
        config.targets = targets
