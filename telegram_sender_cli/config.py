from __future__ import annotations

import tomllib
from pathlib import Path

import tomli_w
from pydantic import BaseModel, ValidationError
from rich.console import Console
from telegram_sender.client.runner import SenderRunner
from telegram_sender.client.sender import MessageSender
from telegram_sender.client.sender.proxy import Proxy
from telegram_sender.client.strategies import (
    DelayStrategy,
    JitterStrategy,
    RateLimiterStrategy,
    RequeueStrategy,
    RetryStrategy,
    TimeoutStrategy,
)
from telegram_sender.client.strategies.protocols import (
    BasePostSendStrategy,
    BasePreSendStrategy,
    BaseSendStrategy,
)

_console = Console()

DEFAULT_CONFIG_PATH = Path("config.toml")


class SessionConfig(BaseModel):
    name: str = "my_session"
    api_id: int | None = None
    api_hash: str | None = None


class ProxyConfig(BaseModel):
    proxies: list[Proxy] = []
    default_scheme: str = "socks5"
    default_host: str = "127.0.0.1"
    default_port: int = 1080
    default_username: str | None = None
    default_password: str | None = None
    default_secret: str | None = None


class StrategiesConfig(BaseModel):
    delay: float = 1.0
    rate_limit: int = 20
    rate_period: float = 60.0
    timeout: float = 5.0
    retry_attempts: int = 3
    retry_delay: float = 2.0
    jitter_ratio: float | None = None
    requeue_cycles: int = 0
    requeue_per_request: bool = False


class ChatTargetsConfig(BaseModel):
    targets: list[str | int] = []


class AppConfig(BaseModel):
    session: SessionConfig = SessionConfig()
    proxy: ProxyConfig = ProxyConfig()
    strategies: StrategiesConfig = StrategiesConfig()
    chat_targets: ChatTargetsConfig = ChatTargetsConfig()


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> AppConfig | None:
    if not path.exists():
        return None
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return AppConfig.model_validate(data)
    except tomllib.TOMLDecodeError as e:
        _console.print(f"[red]Failed to parse config.toml: {e}[/red]")
        return None
    except ValidationError as e:
        _console.print(f"[red]Invalid config.toml: {e}[/red]")
        return None


def save_config(config: AppConfig, path: Path = DEFAULT_CONFIG_PATH) -> None:
    data = config.model_dump(exclude_none=True)
    try:
        with open(path, "wb") as f:
            tomli_w.dump(data, f)
    except OSError as e:
        _console.print(f"[red]Failed to save config: {e}[/red]")


from typing import TypeAlias  # noqa: E402

Strategy: TypeAlias = (  # noqa: UP040
    BasePreSendStrategy
    | BaseSendStrategy
    | BasePostSendStrategy
)


def build_strategies(cfg: StrategiesConfig) -> list[Strategy]:
    strategies: list[Strategy] = []

    if cfg.rate_limit > 0:
        strategies.append(
            RateLimiterStrategy(rate=cfg.rate_limit, period=cfg.rate_period)
        )

    if cfg.timeout > 0:
        strategies.append(TimeoutStrategy(timeout=cfg.timeout))

    if cfg.retry_attempts > 0:
        if cfg.jitter_ratio is not None:
            strategies.append(
                JitterStrategy(
                    attempts=cfg.retry_attempts,
                    delay=cfg.retry_delay,
                    jitter_ratio=cfg.jitter_ratio,
                )
            )
        else:
            strategies.append(
                RetryStrategy(
                    attempts=cfg.retry_attempts, delay=cfg.retry_delay
                )
            )

    if cfg.delay > 0:
        strategies.append(DelayStrategy(delay=cfg.delay))

    if cfg.requeue_cycles != 0:
        strategies.append(
            RequeueStrategy(
                cycles=cfg.requeue_cycles,
                per_request=cfg.requeue_per_request,
            )
        )

    return strategies


def build_sender(cfg: AppConfig) -> MessageSender:
    return MessageSender(
        session=cfg.session.name,
        api_id=cfg.session.api_id,
        api_hash=cfg.session.api_hash,
        proxies=cfg.proxy.proxies if cfg.proxy.proxies else None,
    )


def build_runner(
    sender: MessageSender, strategies: list[Strategy]
) -> SenderRunner:
    return SenderRunner(sender, *strategies)
