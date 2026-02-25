from prompt_toolkit import PromptSession

from telegram_sender_cli.config import SessionConfig
from telegram_sender_cli.utils.interaction import ask
from telegram_sender_cli.utils.print import print_header
from telegram_sender_cli.wizard.validators import (
    ApiHashValidator,
    ApiIdValidator,
)


async def store_session_creds(
    prompt_session: PromptSession[str], config: SessionConfig
) -> None:
    print_header(text="Step 1 \u2014 Session Name")

    name = await ask(
        text="Session name: ",
        default=config.name,
        prompt_session=prompt_session,
        converter=str,
    )

    print_header(text="Step 2 \u2014 API Credentials")

    api_id = await ask(
        text="API ID: ",
        default=config.api_id,
        prompt_session=prompt_session,
        validator=ApiIdValidator(),
        converter=int,
    )

    api_hash = await ask(
        text="API Hash: ",
        default=config.api_hash,
        prompt_session=prompt_session,
        validator=ApiHashValidator(),
        converter=str,
    )

    config.name = name
    config.api_id = api_id
    config.api_hash = api_hash
