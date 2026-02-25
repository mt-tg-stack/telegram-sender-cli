=========
Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[0.1.0] - 2026-02-25
--------------------

Added
~~~~~
* Initial release of ``telegram-sender-cli``.
* Interactive REPL with command autocompletion and history.
* Support for broadcasting text messages to multiple targets.
* Media commands: ``/photo``, ``/video``, ``/doc``, ``/audio``, ``/sticker``, ``/voice``, ``/animation``.
* Interactive configuration wizard for API credentials and session setup.
*   Support for SOCKS5, HTTPS, and MTProto proxies.
*   Added ``RequeueStrategy`` for re-enqueuing requests (infinite or fixed cycles).
*   Configurable sending strategies: rate limiting, delays, retries, and timeouts.
* TOML-based configuration management.
* Integration with ``telegram-sender`` core library.
