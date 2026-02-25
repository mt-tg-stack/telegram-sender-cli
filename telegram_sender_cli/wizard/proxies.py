from typing import cast

from prompt_toolkit import PromptSession
from telegram_sender.client.sender.proxy import Proxy

from telegram_sender_cli.config import ProxyConfig
from telegram_sender_cli.utils.interaction import ask, output_yes
from telegram_sender_cli.wizard.validators import (
    IntValidator,
    ProxyHostValidator,
    ProxySchemeValidator,
)


async def store_proxies(
    prompt_session: PromptSession[str], config: ProxyConfig
) -> None:
    has_proxy = bool(config.proxies)

    use_proxy = await ask(
        text="Configure proxy? (y/n): ",
        default="y" if has_proxy else "n",
        prompt_session=prompt_session,
        converter=str,
    )
    if not output_yes(output=use_proxy):
        return

    proxies_list = [*config.proxies]
    while True:
        scheme = await ask(
            text="Scheme (socks5/https/mtproto): ",
            default=config.default_scheme,
            prompt_session=prompt_session,
            validator=ProxySchemeValidator(),
            converter=str,
        )
        host = await ask(
            text="Host: ",
            default=config.default_host,
            prompt_session=prompt_session,
            validator=ProxyHostValidator(),
            converter=str,
        )
        port = await ask(
            text="Port: ",
            default=config.default_port,
            prompt_session=prompt_session,
            validator=IntValidator(),
            converter=int,
        )

        proxy = {"scheme": scheme, "host": host, "port": port}

        if scheme == "mtproto":
            secret = await ask(
                text="Secret: ",
                default=config.default_secret,
                prompt_session=prompt_session,
                converter=str,
            )
            if secret:
                proxy["secret"] = secret
        else:
            username = await ask(
                text="Username (optional): ",
                default=config.default_username,
                prompt_session=prompt_session,
                converter=str,
            )
            if username:
                proxy["username"] = username
            password = await ask(
                text="Password (optional): ",
                default=config.default_password,
                prompt_session=prompt_session,
                converter=str,
            )
            if password:
                proxy["password"] = password

        if proxy not in proxies_list:
            proxies_list.append(cast(Proxy, proxy))

        add_another = await ask(
            text="Add another proxy? (y/n): ",
            default="y",
            prompt_session=prompt_session,
            converter=str,
        )
        if not output_yes(output=add_another):
            config.proxies = proxies_list
            return
