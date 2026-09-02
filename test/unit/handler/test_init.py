"""DiscordHandler.__init__メソッドのテスト."""

import logging

import pytest

from discord_logger import DiscordHandler, DiscordPublisher
from discord_logger.exceptions import WebhookError

DUMMY_URL = "https://discord.com/api/webhooks/1234567890/dummytoken"


# 正常系
def test_init_default_level_is_info() -> None:
    """既定のログレベルがINFOであること."""
    handler = DiscordHandler([DUMMY_URL])
    assert handler.level == logging.INFO


def test_init_custom_level() -> None:
    """指定したログレベルが設定されること."""
    handler = DiscordHandler([DUMMY_URL], level=logging.ERROR)
    assert handler.level == logging.ERROR


def test_init_sets_default_formatter() -> None:
    """既定のフォーマッタがDiscordPublisher.LOG_FORMATであること."""
    handler = DiscordHandler([DUMMY_URL])
    assert handler.formatter is not None
    assert handler.formatter._fmt == DiscordPublisher.LOG_FORMAT


def test_init_passes_settings_to_publisher(monkeypatch: pytest.MonkeyPatch) -> None:
    """Webhook URL・ユーザーID・タイムアウトがDiscordPublisherへ渡ること."""
    monkeypatch.delenv("DISCORD_LOGGER_USER_ID", raising=False)
    handler = DiscordHandler([DUMMY_URL], discord_user_id="123", timeout=3)
    assert handler.publisher.webhook_urls == [DUMMY_URL]
    assert handler.publisher._discord_user_id == "123"
    assert handler.publisher._timeout == 3


# 準正常系
def test_init_with_empty_urls_raises_error() -> None:
    """空のURLリストでWebhookErrorが送出されること."""
    with pytest.raises(WebhookError):
        DiscordHandler([])


def test_init_with_invalid_url_raises_error() -> None:
    """不正な形式のURLでWebhookErrorが送出されること."""
    with pytest.raises(WebhookError):
        DiscordHandler(["https://example.com/not-a-webhook"])
