"""discord-logger: DiscordのWebhookを利用したロギングライブラリ.

標準のloggingに組み込むハンドラ（DiscordHandler）、Webhookへの送信そのものを行う
DiscordPublisher、コンソール出力に色を付けるColoredFormatterを提供する。
"""

try:
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version("discord-logger")
except (PackageNotFoundError, ImportError):
    __version__ = "unknown"

from discord_logger.exceptions import ConfigError, DiscordLoggerError, WebhookError
from discord_logger.formatter import DATE_FORMAT, LOG_FORMAT, ColoredFormatter
from discord_logger.handler import DiscordHandler
from discord_logger.publisher import DiscordPublisher

__all__ = [
    "DATE_FORMAT",
    "LOG_FORMAT",
    "ColoredFormatter",
    "ConfigError",
    "DiscordHandler",
    "DiscordLoggerError",
    "DiscordPublisher",
    "WebhookError",
]
