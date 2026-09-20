"""DiscordHandler.emitメソッドのテスト."""

import logging
from collections.abc import Iterator

import pytest
import pytest_mock
import requests

from discord_logger import DiscordHandler

DUMMY_URL = "https://discord.com/api/webhooks/1234567890/dummytoken"


@pytest.fixture()
def mock_post(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    """requests.postのモック（送信成功）."""
    mock = mocker.patch("discord_logger.publisher.requests.post")
    mock.return_value = mocker.MagicMock()
    return mock


@pytest.fixture()
def logger() -> Iterator[logging.Logger]:
    """テスト用のロガー。テスト後にハンドラを外す.

    Yields:
        logging.Logger: 伝播を止めたテスト用ロガー
    """
    test_logger = logging.getLogger("discord_handler_test")
    test_logger.setLevel(logging.DEBUG)
    test_logger.propagate = False
    yield test_logger
    for handler in list(test_logger.handlers):
        test_logger.removeHandler(handler)


def _sent_content(mock_post: pytest_mock.MockType) -> str:
    """requests.postへ渡された本文を返す."""
    content = mock_post.call_args.kwargs["json"]["content"]
    assert isinstance(content, str)
    return content


# 正常系
def test_emit_sends_formatted_record(
    mock_post: pytest_mock.MockType, logger: logging.Logger, monkeypatch: pytest.MonkeyPatch
) -> None:
    """レコードがロガー名・レベル付きで整形されて送信されること."""
    monkeypatch.delenv("DISCORD_LOGGER_USER_ID", raising=False)
    logger.addHandler(DiscordHandler([DUMMY_URL]))

    logger.info("テストメッセージ")

    mock_post.assert_called_once()
    content = _sent_content(mock_post)
    assert content.endswith("[discord_handler_test][INFO] テストメッセージ")
    assert content.startswith("[")


def test_emit_mentions_user_on_error(
    mock_post: pytest_mock.MockType, logger: logging.Logger
) -> None:
    """ERRORレコードはユーザーIDのメンション付きで送信されること."""
    logger.addHandler(DiscordHandler([DUMMY_URL], discord_user_id="123456789"))

    logger.error("エラーが発生しました")

    content = _sent_content(mock_post)
    assert content.startswith("<@123456789>\n")
    assert "[ERROR] エラーが発生しました" in content


def test_emit_does_not_mention_below_error(
    mock_post: pytest_mock.MockType, logger: logging.Logger
) -> None:
    """WARNING以下のレコードはメンションを付けないこと."""
    logger.addHandler(DiscordHandler([DUMMY_URL], discord_user_id="123456789"))

    logger.warning("注意")

    assert not _sent_content(mock_post).startswith("<@")


def test_emit_skips_records_below_handler_level(
    mock_post: pytest_mock.MockType, logger: logging.Logger
) -> None:
    """ハンドラのレベル未満のレコードは送信しないこと."""
    logger.addHandler(DiscordHandler([DUMMY_URL], level=logging.ERROR))

    logger.info("送信されない")
    logger.error("送信される")

    mock_post.assert_called_once()
    assert "[ERROR] 送信される" in _sent_content(mock_post)


def test_emit_sends_records_from_child_logger(
    mock_post: pytest_mock.MockType, logger: logging.Logger
) -> None:
    """子ロガー（getChild）から伝播したレコードも送信されること."""
    logger.addHandler(DiscordHandler([DUMMY_URL]))

    logger.getChild("library").error("ライブラリ内部のエラー")

    content = _sent_content(mock_post)
    assert "[discord_handler_test.library][ERROR] ライブラリ内部のエラー" in content


def test_emit_uses_custom_formatter(
    mock_post: pytest_mock.MockType, logger: logging.Logger
) -> None:
    """setFormatterで指定したフォーマットで送信されること."""
    handler = DiscordHandler([DUMMY_URL])
    handler.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
    logger.addHandler(handler)

    logger.info("独自フォーマット")

    assert _sent_content(mock_post) == "INFO:独自フォーマット"


def test_emit_truncates_long_message(
    mock_post: pytest_mock.MockType, logger: logging.Logger
) -> None:
    """2000文字を超えるメッセージは切り詰めて送信されること."""
    logger.addHandler(DiscordHandler([DUMMY_URL]))

    logger.info("あ" * 3000)

    assert len(_sent_content(mock_post)) <= 2000


# 異常系
def test_emit_delegates_send_failure_to_handle_error(
    mocker: pytest_mock.MockerFixture, logger: logging.Logger
) -> None:
    """送信に失敗しても例外を送出せず、handleErrorに委ねること."""
    mock_post = mocker.patch("discord_logger.publisher.requests.post")
    mock_post.side_effect = requests.ConnectionError("接続失敗")
    handler = DiscordHandler([DUMMY_URL])
    handle_error = mocker.patch.object(handler, "handleError")
    logger.addHandler(handler)

    logger.info("送信失敗")

    handle_error.assert_called_once()
    record = handle_error.call_args.args[0]
    assert record.getMessage() == "送信失敗"
