"""DiscordPublisher.__init__メソッドのテスト."""

import os

import pytest

from discord_logger import DiscordPublisher
from discord_logger.exceptions import WebhookError

DUMMY_URL = "https://discord.com/api/webhooks/dummy"


# 正常系
def test_init_with_single_url() -> None:
    """単一のURLでDiscordPublisherが初期化されること."""
    publisher = DiscordPublisher([DUMMY_URL])
    assert publisher.webhook_urls == [DUMMY_URL]


def test_init_with_multiple_urls() -> None:
    """複数のURLでDiscordPublisherが初期化されること."""
    urls = [DUMMY_URL, "https://discord.com/api/webhooks/dummy2"]
    publisher = DiscordPublisher(urls)
    assert publisher.webhook_urls == urls


def test_init_custom_name() -> None:
    """カスタム名でDiscordPublisherが初期化されること."""
    publisher = DiscordPublisher([DUMMY_URL], name="test_pub")
    assert publisher._name == "test_pub"


def test_init_default_name_uses_caller_directory() -> None:
    """デフォルトのnameで呼び出し元のディレクトリパスが使用されること."""
    publisher = DiscordPublisher([DUMMY_URL])
    expected_dir = os.path.dirname(os.path.abspath(__file__))
    assert publisher._name == expected_dir


def test_init_discord_user_id() -> None:
    """カスタムdiscord_user_idで初期化されること."""
    publisher = DiscordPublisher([DUMMY_URL], discord_user_id="123456789")
    assert publisher._discord_user_id == "123456789"


def test_init_default_discord_user_id_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """デフォルトのdiscord_user_idが空文字列であること."""
    monkeypatch.delenv("DISCORD_LOGGER_USER_ID", raising=False)
    publisher = DiscordPublisher([DUMMY_URL])
    assert publisher._discord_user_id == ""


def test_init_discord_user_id_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """環境変数からdiscord_user_idが読み込まれること."""
    monkeypatch.setenv("DISCORD_LOGGER_USER_ID", "111222333")
    publisher = DiscordPublisher([DUMMY_URL])
    assert publisher._discord_user_id == "111222333"


def test_init_discord_user_id_arg_overrides_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """引数のdiscord_user_idが環境変数より優先されること."""
    monkeypatch.setenv("DISCORD_LOGGER_USER_ID", "111222333")
    publisher = DiscordPublisher([DUMMY_URL], discord_user_id="999888777")
    assert publisher._discord_user_id == "999888777"


# 準正常系
def test_init_empty_urls_raises_error() -> None:
    """空のURLリストでWebhookErrorが発生すること."""
    with pytest.raises(WebhookError, match="webhook_urlsは1つ以上のURLを含む必要があります"):
        DiscordPublisher([])
