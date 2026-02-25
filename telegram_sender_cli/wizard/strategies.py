from prompt_toolkit import PromptSession

from telegram_sender_cli.config import StrategiesConfig
from telegram_sender_cli.utils.interaction import ask, output_yes
from telegram_sender_cli.wizard.validators import (
    FloatValidator,
    IntValidator,
)


async def store_strategies(
    prompt_session: PromptSession[str], config: StrategiesConfig
) -> None:

    delay = await ask(
        text="Post-send delay (0=off): ",
        default=config.delay,
        prompt_session=prompt_session,
        validator=FloatValidator(),
        converter=float,
    )

    rate_limit = await ask(
        text="Rate limit (0=off): ",
        default=config.rate_limit,
        prompt_session=prompt_session,
        validator=IntValidator(),
        converter=int,
    )

    rate_period = config.rate_period
    if rate_limit > 0:
        rate_period = await ask(
            text="Rate period (seconds): ",
            default=config.rate_period,
            prompt_session=prompt_session,
            validator=FloatValidator(),
            converter=float,
        )

    timeout = await ask(
        text="Send timeout (0=off): ",
        default=config.timeout,
        prompt_session=prompt_session,
        validator=FloatValidator(),
        converter=float,
    )

    retry_attempts = await ask(
        text="Retry attempts (0=off): ",
        default=config.retry_attempts,
        prompt_session=prompt_session,
        validator=IntValidator(),
        converter=int,
    )

    retry_delay = config.retry_delay
    if retry_attempts > 0:
        retry_delay = await ask(
            text="Retry delay (seconds): ",
            default=config.retry_delay,
            prompt_session=prompt_session,
            validator=FloatValidator(),
            converter=float,
        )

    jitter = await ask(
        text="Jitter ratio (empty=no jitter): ",
        default=config.jitter_ratio,
        prompt_session=prompt_session,
        validator=FloatValidator(),
        converter=float,
    )

    requeue_cycles = await ask(
        text="Requeue cycles (0=off, -1=infinite): ",
        default=config.requeue_cycles,
        prompt_session=prompt_session,
        validator=IntValidator(),
        converter=int,
    )

    requeue_per_request = config.requeue_per_request
    if requeue_cycles != 0:
        requeue_per_request_str = await ask(
            text="Requeue per request? (y/n): ",
            default="y" if config.requeue_per_request else "n",
            prompt_session=prompt_session,
            converter=str,
        )
        requeue_per_request = output_yes(requeue_per_request_str)

    config.delay = delay
    config.rate_limit = rate_limit
    config.rate_period = rate_period
    config.timeout = timeout
    config.retry_attempts = retry_attempts
    config.retry_delay = retry_delay
    config.jitter_ratio = jitter
    config.requeue_cycles = requeue_cycles
    config.requeue_per_request = requeue_per_request
