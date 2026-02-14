"""DiscordLogger.__init__メソッドのテスト."""

import logging
import os

import pytest

from discord_logger import DiscordLogger
from discord_logger.exceptions import WebhookError

DUMMY_URL = "https://discord.com/api/webhooks/1234567890/dummytoken"


# 正常系
def test_init_default_parameters() -> None:
    """デフォルトパラメータでDiscordLoggerが初期化されること."""
    dlogger = DiscordLogger([DUMMY_URL])
    # nameが空文字列の場合は呼び出し元のディレクトリパスが設定される
    expected_dir = os.path.dirname(os.path.abspath(__file__))
    assert dlogger.name == expected_dir
    assert dlogger.discord_level == logging.INFO


def test_init_custom_name() -> None:
    """カスタム名でDiscordLoggerが初期化されること."""
    dlogger = DiscordLogger([DUMMY_URL], name="my_dlogger")
    assert dlogger.name == "my_dlogger"


def test_init_custom_discord_level() -> None:
    """カスタムdiscord_levelで初期化されること."""
    dlogger = DiscordLogger([DUMMY_URL], discord_level=logging.WARNING)
    assert dlogger.discord_level == logging.WARNING


def test_init_has_discord_publisher() -> None:
    """discord_publisherが設定されること."""
    dlogger = DiscordLogger([DUMMY_URL])
    assert dlogger.discord_publisher is not None
    assert dlogger.discord_publisher.webhook_urls == [DUMMY_URL]


def test_init_discord_user_id_passed_to_publisher() -> None:
    """discord_user_idがDiscordPublisherに渡されること."""
    dlogger = DiscordLogger([DUMMY_URL], discord_user_id="987654321")
    assert dlogger.discord_publisher._discord_user_id == "987654321"


def test_init_default_discord_user_id_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """デフォルトのdiscord_user_idが空文字列であること."""
    monkeypatch.delenv("DISCORD_LOGGER_USER_ID", raising=False)
    dlogger = DiscordLogger([DUMMY_URL])
    assert dlogger.discord_publisher._discord_user_id == ""


def test_init_discord_user_id_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """環境変数からdiscord_user_idが読み込まれること."""
    monkeypatch.setenv("DISCORD_LOGGER_USER_ID", "444555666")
    dlogger = DiscordLogger([DUMMY_URL])
    assert dlogger.discord_publisher._discord_user_id == "444555666"


def test_init_discord_user_id_arg_overrides_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """引数のdiscord_user_idが環境変数より優先されること."""
    monkeypatch.setenv("DISCORD_LOGGER_USER_ID", "444555666")
    dlogger = DiscordLogger([DUMMY_URL], discord_user_id="777888999")
    assert dlogger.discord_publisher._discord_user_id == "777888999"


# 準正常系
def test_init_empty_urls_raises_error() -> None:
    """空のURLリストでWebhookErrorが発生すること."""
    with pytest.raises(WebhookError):
        DiscordLogger([])
