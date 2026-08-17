"""例外クラスのテスト."""

from discord_logger.exceptions import ConfigError, DiscordLoggerError, WebhookError


# 正常系
def test_discord_logger_error_is_exception() -> None:
    """DiscordLoggerErrorがExceptionを継承していること."""
    assert issubclass(DiscordLoggerError, Exception)


def test_webhook_error_is_discord_logger_error() -> None:
    """WebhookErrorがDiscordLoggerErrorを継承していること."""
    assert issubclass(WebhookError, DiscordLoggerError)


def test_config_error_is_discord_logger_error() -> None:
    """ConfigErrorがDiscordLoggerErrorを継承していること."""
    assert issubclass(ConfigError, DiscordLoggerError)


def test_discord_logger_error_can_be_raised() -> None:
    """DiscordLoggerErrorが送出できること."""  # noqa: DOC501
    try:
        raise DiscordLoggerError("テストエラー")
    except DiscordLoggerError as error:
        assert str(error) == "テストエラー"


def test_webhook_error_can_be_caught_as_base() -> None:
    """WebhookErrorがDiscordLoggerErrorとしてキャッチできること."""  # noqa: DOC501
    try:
        raise WebhookError("Webhookエラー")
    except DiscordLoggerError as error:
        assert str(error) == "Webhookエラー"


def test_config_error_can_be_caught_as_base() -> None:
    """ConfigErrorがDiscordLoggerErrorとしてキャッチできること."""  # noqa: DOC501
    try:
        raise ConfigError("設定エラー")
    except DiscordLoggerError as error:
        assert str(error) == "設定エラー"
