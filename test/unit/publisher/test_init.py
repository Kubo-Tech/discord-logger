"""DiscordPublisher.__init__メソッドのテスト."""

import os

import pytest

from discord_logger import DiscordPublisher
from discord_logger.exceptions import WebhookError

DUMMY_URL = "https://discord.com/api/webhooks/1234567890/dummytoken"


# 正常系
def test_init_with_single_url() -> None:
    """単一のURLでDiscordPublisherが初期化されること."""
    publisher = DiscordPublisher([DUMMY_URL])
    assert publisher.webhook_urls == [DUMMY_URL]


def test_init_with_multiple_urls() -> None:
    """複数のURLでDiscordPublisherが初期化されること."""
    urls = [DUMMY_URL, "https://discord.com/api/webhooks/9876543210/dummytoken2"]
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


def test_init_invalid_url_raises_error() -> None:
    """不正な形式のURLでWebhookErrorが発生すること."""
    with pytest.raises(WebhookError, match="不正なWebhook URLが含まれています"):
        DiscordPublisher(["https://example.com/not-a-webhook"])


def test_init_empty_string_url_raises_error() -> None:
    """空文字列のURLでWebhookErrorが発生すること."""
    with pytest.raises(WebhookError, match="不正なWebhook URLが含まれています"):
        DiscordPublisher([""])


def test_init_malformed_url_raises_error() -> None:
    """不完全なDiscord Webhook URLでWebhookErrorが発生すること."""
    with pytest.raises(WebhookError, match="不正なWebhook URLが含まれています"):
        DiscordPublisher(["https://discord.com/api/webhooks/"])


def test_init_missing_token_url_raises_error() -> None:
    """トークンが欠けたDiscord Webhook URLでWebhookErrorが発生すること."""
    with pytest.raises(WebhookError, match="不正なWebhook URLが含まれています"):
        DiscordPublisher(["https://discord.com/api/webhooks/1234567890"])


def test_init_non_numeric_id_url_raises_error() -> None:
    """IDが数字でないDiscord Webhook URLでWebhookErrorが発生すること."""
    with pytest.raises(WebhookError, match="不正なWebhook URLが含まれています"):
        DiscordPublisher(["https://discord.com/api/webhooks/abc/token"])


def test_init_discordapp_url_is_valid() -> None:
    """discordapp.comドメインのURLが有効であること."""
    publisher = DiscordPublisher(["https://discordapp.com/api/webhooks/1234567890/dummytoken"])
    assert len(publisher.webhook_urls) == 1


def test_init_error_message_contains_invalid_url() -> None:
    """エラーメッセージに不正なURLが含まれること."""
    invalid_url = "https://example.com/invalid"
    with pytest.raises(WebhookError, match=invalid_url):
        DiscordPublisher([invalid_url])
