import re
import socket

from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError, Validator

INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1

USERNAME_RE = re.compile(r"^@[a-zA-Z0-9_]{5,32}$")


def validate_chat_id(value: int | str) -> int | str:
    if isinstance(value, int):
        if not (INT64_MIN <= value <= INT64_MAX):
            raise ValueError("chat_id out of int64 range")
        return value

    if isinstance(value, str):
        value = value.strip()

        if USERNAME_RE.fullmatch(value):
            return value

        try:
            ivalue = int(value)
            if not (INT64_MIN <= ivalue <= INT64_MAX):
                raise ValueError("chat_id out of int64 range")
            return ivalue
        except ValueError:
            if value.lower() == "me":
                return value
            raise ValueError(
                f"Invalid chat_id: {value!r}"
                " (use @username, numeric ID,"
                " 'me', or 'self')"
            )
    raise ValueError("chat_id must be int or str")


class IntValidator(Validator):
    def validate(self, document: Document) -> None:
        text = document.text.strip()
        if text:
            try:
                int(text)
            except ValueError:
                raise ValidationError(
                    message="Please enter a valid integer"
                )


class ApiIdValidator(IntValidator):
    def validate(self, document: Document) -> None:
        super().validate(document)
        text = document.text.strip()
        if not text:
            return
        api_id = int(text)
        if 1 <= api_id <= 2147483647:
            return
        raise ValidationError(
            message="API ID must be between 1 and 2147483647"
        )


class FloatValidator(Validator):
    def validate(self, document: Document) -> None:
        text = document.text.strip()
        if text:
            try:
                float(text)
            except ValueError:
                raise ValidationError(
                    message="Please enter a valid number"
                )


class ApiHashValidator(Validator):
    def validate(self, document: Document) -> None:
        text = document.text.strip()
        if text:
            if len(text) != 32:
                raise ValidationError(
                    message="API Hash must be 32 characters long"
                )

            try:
                int(text, 16)
            except ValueError:
                raise ValidationError(
                    message="API Hash must be a valid hex number"
                )


class ProxySchemeValidator(Validator):
    def validate(self, document: Document) -> None:
        text = document.text.strip().lower()
        if text and text not in ("socks5", "https", "mtproto"):
            raise ValidationError(
                message="Invalid proxy scheme"
            )


HOSTNAME_RE = re.compile(
    r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?"
    r"(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$"
)


class ProxyHostValidator(Validator):
    def validate(self, document: Document) -> None:
        text = document.text.strip()
        if text:
            try:
                socket.inet_pton(socket.AF_INET, text)
                return
            except OSError:
                pass
            try:
                socket.inet_pton(socket.AF_INET6, text)
                return
            except OSError:
                pass
            if HOSTNAME_RE.fullmatch(text):
                return
            raise ValidationError(
                message="Invalid proxy host"
            )


class ChatTargetValidator(Validator):
    def validate(self, document: Document) -> None:
        chat_targets = document.text.split(",")
        for raw_target in chat_targets:
            stripped = raw_target.strip()
            if not stripped:
                continue
            target: int | str
            try:
                target = int(stripped)
            except ValueError:
                target = stripped
            try:
                validate_chat_id(value=target)
            except ValueError as e:
                raise ValidationError(message=str(e))


class YesValidator(Validator):
    def validate(self, document: Document) -> None:
        text = document.text.strip().lower()
        if text not in ("y", "yes"):
            raise ValidationError(
                message="Please enter 'y' or 'yes'"
            )


class NoValidator(Validator):
    def validate(self, document: Document) -> None:
        pass
