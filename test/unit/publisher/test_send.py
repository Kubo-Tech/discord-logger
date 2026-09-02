"""DiscordPublisher.sendおよびpublishメソッドのテスト."""

import pytest
import pytest_mock
import requests

from discord_logger import DiscordPublisher
from discord_logger.exceptions import ConfigError, WebhookError

DUMMY_URL = "https://discord.com/api/webhooks/1234567890/dummytoken"


# 正常系
def test_send_calls_requests_post(mocker: pytest_mock.MockerFixture) -> None:
    """sendがrequests.postを呼び出すこと."""
    mock_post = mocker.patch("discord_logger.publisher.requests.post")
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_post.return_value = mock_response

    publisher = DiscordPublisher([DUMMY_URL])
    publisher.send("テストメッセージ")

    mock_post.assert_called_once_with(DUMMY_URL, json={"content": "テストメッセージ"}, timeout=10)


def test_send_calls_all_urls(mocker: pytest_mock.MockerFixture) -> None:
    """sendが全てのURLに対してPOSTリクエストを送信すること."""
    mock_post = mocker.patch("discord_logger.publisher.requests.post")
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_post.return_value = mock_response

    urls = [DUMMY_URL, "https://discord.com/api/webhooks/9876543210/dummytoken2"]
    publisher = DiscordPublisher(urls)
    publisher.send("テストメッセージ")

    assert mock_post.call_count == 2


def test_publish_formats_and_sends(mocker: pytest_mock.MockerFixture) -> None:
    """publishがフォーマットしてから送信すること."""
    mock_post = mocker.patch("discord_logger.publisher.requests.post")
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_post.return_value = mock_response

    publisher = DiscordPublisher([DUMMY_URL])
    publisher.publish("INFO", "テスト公開メッセージ")

    call_args = mock_post.call_args
    content = call_args[1]["json"]["content"]
    assert "INFO" in content
    assert "テスト公開メッセージ" in content


def test_format_message_contains_level() -> None:
    """_format_messageがログレベルを含むこと."""
    publisher = DiscordPublisher([DUMMY_URL])
    formatted = publisher._format_message("WARNING", "テスト")
    assert "WARNING" in formatted


def test_format_message_contains_name() -> None:
    """_format_messageがロガー名を含むこと."""
    publisher = DiscordPublisher([DUMMY_URL], name="my_publisher")
    formatted = publisher._format_message("INFO", "テスト")
    assert "my_publisher" in formatted


def test_format_message_contains_message() -> None:
    """_format_messageがメッセージ本文を含むこと."""
    publisher = DiscordPublisher([DUMMY_URL])
    formatted = publisher._format_message("INFO", "テストメッセージ本文")
    assert "テストメッセージ本文" in formatted


def test_publish_error_with_user_id_adds_mention(mocker: pytest_mock.MockerFixture) -> None:
    """ERRORレベルでdiscord_user_idがある場合メンションが付与されること."""
    mock_post = mocker.patch("discord_logger.publisher.requests.post")
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_post.return_value = mock_response

    publisher = DiscordPublisher([DUMMY_URL], discord_user_id="123456789")
    publisher.publish("ERROR", "エラーメッセージ")

    call_args = mock_post.call_args
    content = call_args[1]["json"]["content"]
    assert content.startswith("<@123456789>")
    assert "エラーメッセージ" in content


def test_publish_critical_with_user_id_adds_mention(mocker: pytest_mock.MockerFixture) -> None:
    """CRITICALレベルでdiscord_user_idがある場合メンションが付与されること."""
    mock_post = mocker.patch("discord_logger.publisher.requests.post")
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_post.return_value = mock_response

    publisher = DiscordPublisher([DUMMY_URL], discord_user_id="123456789")
    publisher.publish("CRITICAL", "致命的エラー")

    call_args = mock_post.call_args
    content = call_args[1]["json"]["content"]
    assert content.startswith("<@123456789>")


def test_publish_info_with_user_id_no_mention(mocker: pytest_mock.MockerFixture) -> None:
    """INFOレベルではメンションが付与されないこと."""
    mock_post = mocker.patch("discord_logger.publisher.requests.post")
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_post.return_value = mock_response

    publisher = DiscordPublisher([DUMMY_URL], discord_user_id="123456789")
    publisher.publish("INFO", "通常メッセージ")

    call_args = mock_post.call_args
    content = call_args[1]["json"]["content"]
    assert not content.startswith("<@")


def test_publish_error_without_user_id_no_mention(mocker: pytest_mock.MockerFixture) -> None:
    """discord_user_idが空の場合メンションが付与されないこと."""
    mock_post = mocker.patch("discord_logger.publisher.requests.post")
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_post.return_value = mock_response

    publisher = DiscordPublisher([DUMMY_URL])
    publisher.publish("ERROR", "エラーメッセージ")

    call_args = mock_post.call_args
    content = call_args[1]["json"]["content"]
    assert not content.startswith("<@")


# 準正常系
def test_send_raises_webhook_error_on_request_exception(mocker: pytest_mock.MockerFixture) -> None:
    """リクエストが失敗した場合WebhookErrorが発生すること."""
    mocker.patch(
        "discord_logger.publisher.requests.post",
        side_effect=requests.RequestException("接続エラー"),
    )
    publisher = DiscordPublisher([DUMMY_URL])

    with pytest.raises(WebhookError, match="Webhook送信に失敗したURLがあります"):
        publisher.send("テストメッセージ")


def test_send_raises_webhook_error_on_http_error(mocker: pytest_mock.MockerFixture) -> None:
    """HTTPエラーが発生した場合WebhookErrorが発生すること."""
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    mocker.patch("discord_logger.publisher.requests.post", return_value=mock_response)

    publisher = DiscordPublisher([DUMMY_URL])

    with pytest.raises(WebhookError, match="Webhook送信に失敗したURLがあります"):
        publisher.send("テストメッセージ")


def test_send_tries_all_urls_and_aggregates_failures(mocker: pytest_mock.MockerFixture) -> None:
    """一部URLが失敗しても全URLを試行し、最後に失敗を集約して送出すること."""
    url_ok = "https://discord.com/api/webhooks/1111111111/oktoken"
    url_fail = "https://discord.com/api/webhooks/2222222222/failtoken"

    mock_success_response = mocker.MagicMock()
    mock_success_response.raise_for_status = mocker.MagicMock()

    def side_effect(url: str, json: dict[str, str], timeout: int) -> object:
        _ = json
        _ = timeout
        if url == url_fail:
            raise requests.RequestException("送信失敗")
        return mock_success_response

    mock_post = mocker.patch("discord_logger.publisher.requests.post", side_effect=side_effect)

    publisher = DiscordPublisher([url_fail, url_ok])

    with pytest.raises(WebhookError, match=r"2222222222/\*\*\*") as exc_info:
        publisher.send("テストメッセージ")

    assert mock_post.call_count == 2
    assert "failtoken" not in str(exc_info.value)
    assert "oktoken" not in str(exc_info.value)


def test_send_failure_does_not_expose_webhook_token(
    mocker: pytest_mock.MockerFixture,
) -> None:
    """送信失敗の例外メッセージと原因例外にWebhookのトークンを含めないこと."""
    mocker.patch(
        "discord_logger.publisher.requests.post",
        side_effect=requests.ConnectionError(f"failed: {DUMMY_URL}"),
    )
    publisher = DiscordPublisher([DUMMY_URL])

    with pytest.raises(WebhookError) as exc_info:
        publisher.send("テストメッセージ")

    assert "dummytoken" not in str(exc_info.value)
    assert "ConnectionError" in str(exc_info.value)
    assert exc_info.value.__cause__ is None


def test_send_truncates_long_message(mocker: pytest_mock.MockerFixture) -> None:
    """2000文字を超えるメッセージが切り詰められて送信されること."""
    mock_post = mocker.patch("discord_logger.publisher.requests.post")
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_post.return_value = mock_response

    publisher = DiscordPublisher([DUMMY_URL])
    long_message = "あ" * 2500
    publisher.send(long_message)

    call_args = mock_post.call_args
    content = call_args[1]["json"]["content"]
    assert len(content) == DiscordPublisher.DISCORD_MAX_LENGTH
    assert content.endswith(DiscordPublisher.TRUNCATION_SUFFIX)


def test_send_does_not_truncate_exact_limit_message(mocker: pytest_mock.MockerFixture) -> None:
    """ちょうど2000文字のメッセージは切り詰められないこと."""
    mock_post = mocker.patch("discord_logger.publisher.requests.post")
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_post.return_value = mock_response

    publisher = DiscordPublisher([DUMMY_URL])
    exact_message = "あ" * DiscordPublisher.DISCORD_MAX_LENGTH
    publisher.send(exact_message)

    call_args = mock_post.call_args
    content = call_args[1]["json"]["content"]
    assert content == exact_message


def test_send_does_not_truncate_short_message(mocker: pytest_mock.MockerFixture) -> None:
    """2000文字未満のメッセージは切り詰められないこと."""
    mock_post = mocker.patch("discord_logger.publisher.requests.post")
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_post.return_value = mock_response

    publisher = DiscordPublisher([DUMMY_URL])
    short_message = "テストメッセージ"
    publisher.send(short_message)

    call_args = mock_post.call_args
    content = call_args[1]["json"]["content"]
    assert content == short_message


def test_publish_raises_config_error_on_invalid_level() -> None:
    """無効なログレベルを指定した場合ConfigErrorが発生すること."""
    publisher = DiscordPublisher([DUMMY_URL])

    with pytest.raises(ConfigError, match="不正なログレベルです"):
        publisher.publish("INVALID_LEVEL", "テストメッセージ")


def test_publish_raises_config_error_message_contains_invalid_level() -> None:
    """エラーメッセージに指定された無効なレベル名が含まれること."""
    publisher = DiscordPublisher([DUMMY_URL])

    with pytest.raises(ConfigError, match="INVALID_LEVEL"):
        publisher.publish("INVALID_LEVEL", "テストメッセージ")
