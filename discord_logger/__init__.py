"""discord-logger: DiscordのWebhookを利用したロギングライブラリ.

このライブラリは、Pythonの標準loggingインターフェースに準拠したロガーに加え、
DiscordのWebhookを通じてログメッセージを送信する機能を提供します。
"""

try:
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version("discord-logger")
except (PackageNotFoundError, ImportError):
    __version__ = "unknown"

from discord_logger.discord_logger import DiscordLogger
from discord_logger.exceptions import ConfigError, DiscordLoggerError, WebhookError
from discord_logger.logger import Logger
from discord_logger.publisher import DiscordPublisher

__all__ = [
    "ConfigError",
    "DiscordLogger",
    "DiscordLoggerError",
    "DiscordPublisher",
    "Logger",
    "WebhookError",
]
