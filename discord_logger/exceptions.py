"""例外クラス定義.

このモジュールは、discord-loggerライブラリで使用される例外クラスを定義する。
"""


class DiscordLoggerError(Exception):
    """discord-logger基底例外.

    discord-loggerライブラリの全ての例外の基底クラス。
    """

    pass


class WebhookError(DiscordLoggerError):
    """Webhook送信エラー.

    DiscordのWebhookへの送信に失敗した場合に送出される例外。
    """

    pass


class ConfigError(DiscordLoggerError):
    """設定エラー.

    設定値が不正な場合に送出される例外。
    """

    pass
