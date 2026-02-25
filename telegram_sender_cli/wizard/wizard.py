from prompt_toolkit import PromptSession

from telegram_sender_cli.config import AppConfig
from telegram_sender_cli.utils.interaction import ask, output_yes
from telegram_sender_cli.utils.print import console, print_config, print_header
from telegram_sender_cli.wizard.chat_target import store_chat_targets
from telegram_sender_cli.wizard.proxies import store_proxies
from telegram_sender_cli.wizard.session_creds import store_session_creds
from telegram_sender_cli.wizard.strategies import store_strategies


async def run_wizard(config: AppConfig) -> tuple[AppConfig, bool]:
    session = PromptSession[str]()
    reconf_answer = await ask(
        text="Reconfigure app? (y/n): ",
        prompt_session=session,
        default="y",
        converter=str,
    )
    if not output_yes(output=reconf_answer):
        return config, False

    print_header(text="Storing session creds")
    await store_session_creds(prompt_session=session, config=config.session)

    print_header(text="Proxy Configuration")
    await store_proxies(prompt_session=session, config=config.proxy)

    print_header(text="Strategies")
    await store_strategies(prompt_session=session, config=config.strategies)

    print_header(text="Chat Targets")
    await store_chat_targets(
        prompt_session=session, config=config.chat_targets
    )

    if not config.chat_targets.targets:
        console.print(
            "[yellow]No targets specified."
            " You can set them later"
            " with /targets[/yellow]"
        )

    # Step 6: Save config
    print_header(text="Summary")
    print_config(config=config)

    save_answer = await ask(
        text="Save config to config.toml? (y/n): ",
        prompt_session=session,
        default="y",
        converter=str,
    )

    return config, output_yes(output=save_answer)
