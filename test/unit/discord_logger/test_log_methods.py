"""DiscordLoggerのログ出力メソッドのテスト."""

import logging

import pytest
import pytest_mock

from discord_logger import DiscordLogger
from discord_logger.exceptions import WebhookError

DUMMY_URL = "https://discord.com/api/webhooks/1234567890/dummytoken"


# 正常系
def test_info_sends_to_discord(mocker: pytest_mock.MockerFixture) -> None:
    """infoがDiscordに送信されること."""
    mock_publish = mocker.patch("discord_logger.discord_logger.DiscordPublisher.publish")
    dlogger = DiscordLogger([DUMMY_URL], name="test_info_discord")
    dlogger.info("テストINFOメッセージ")
    mock_publish.assert_called_once_with("INFO", "テストINFOメッセージ")


def test_debug_sends_to_discord_when_level_debug(mocker: pytest_mock.MockerFixture) -> None:
    """discord_levelがDEBUG時にdebugがDiscordに送信されること."""
    mock_publish = mocker.patch("discord_logger.discord_logger.DiscordPublisher.publish")
    dlogger = DiscordLogger(
        [DUMMY_URL],
        name="test_debug_discord",
        level=logging.DEBUG,
        discord_level=logging.DEBUG,
    )
    dlogger.debug("テストDEBUGメッセージ")
    mock_publish.assert_called_once_with("DEBUG", "テストDEBUGメッセージ")


def test_warning_sends_to_discord(mocker: pytest_mock.MockerFixture) -> None:
    """warningがDiscordに送信されること."""
    mock_publish = mocker.patch("discord_logger.discord_logger.DiscordPublisher.publish")
    dlogger = DiscordLogger([DUMMY_URL], name="test_warning_discord")
    dlogger.warning("テストWARNINGメッセージ")
    mock_publish.assert_called_once_with("WARNING", "テストWARNINGメッセージ")


def test_error_sends_to_discord(mocker: pytest_mock.MockerFixture) -> None:
    """errorがDiscordに送信されること."""
    mock_publish = mocker.patch("discord_logger.discord_logger.DiscordPublisher.publish")
    dlogger = DiscordLogger([DUMMY_URL], name="test_error_discord")
    dlogger.error("テストERRORメッセージ")
    mock_publish.assert_called_once_with("ERROR", "テストERRORメッセージ")


def test_critical_sends_to_discord(mocker: pytest_mock.MockerFixture) -> None:
    """criticalがDiscordに送信されること."""
    mock_publish = mocker.patch("discord_logger.discord_logger.DiscordPublisher.publish")
    dlogger = DiscordLogger([DUMMY_URL], name="test_critical_discord")
    dlogger.critical("テストCRITICALメッセージ")
    mock_publish.assert_called_once_with("CRITICAL", "テストCRITICALメッセージ")


def test_info_not_sent_when_discord_level_warning(mocker: pytest_mock.MockerFixture) -> None:
    """discord_levelがWARNING時にinfoがDiscordに送信されないこと."""
    mock_publish = mocker.patch("discord_logger.discord_logger.DiscordPublisher.publish")
    dlogger = DiscordLogger(
        [DUMMY_URL],
        name="test_info_not_discord",
        discord_level=logging.WARNING,
    )
    dlogger.info("このメッセージはDiscordに送信されない")
    mock_publish.assert_not_called()


def test_warning_sent_when_discord_level_warning(mocker: pytest_mock.MockerFixture) -> None:
    """discord_levelがWARNING時にwarningがDiscordに送信されること."""
    mock_publish = mocker.patch("discord_logger.discord_logger.DiscordPublisher.publish")
    dlogger = DiscordLogger(
        [DUMMY_URL],
        name="test_warning_sent",
        discord_level=logging.WARNING,
    )
    dlogger.warning("このメッセージはDiscordに送信される")
    mock_publish.assert_called_once_with("WARNING", "このメッセージはDiscordに送信される")


def test_info_still_outputs_to_console(
    mocker: pytest_mock.MockerFixture, capfd: pytest.CaptureFixture[str]
) -> None:
    """discord_levelがWARNING時でもinfoはコンソールに出力されること."""
    mocker.patch("discord_logger.discord_logger.DiscordPublisher.publish")
    dlogger = DiscordLogger(
        [DUMMY_URL],
        name="test_console_output",
        discord_level=logging.WARNING,
    )
    dlogger.info("コンソール出力テスト")
    captured = capfd.readouterr()
    assert "コンソール出力テスト" in captured.out


# 異常系
def test_info_does_not_raise_on_webhook_error(mocker: pytest_mock.MockerFixture) -> None:
    """Discord送信でWebhookErrorが発生してもinfoが例外を送出しないこと."""
    mocker.patch(
        "discord_logger.discord_logger.DiscordPublisher.publish",
        side_effect=WebhookError("送信失敗"),
    )
    dlogger = DiscordLogger([DUMMY_URL], name="test_webhook_error")
    dlogger.info("テストメッセージ")


def test_debug_does_not_raise_on_webhook_error(mocker: pytest_mock.MockerFixture) -> None:
    """Discord送信でWebhookErrorが発生してもdebugが例外を送出しないこと."""
    mocker.patch(
        "discord_logger.discord_logger.DiscordPublisher.publish",
        side_effect=WebhookError("送信失敗"),
    )
    dlogger = DiscordLogger(
        [DUMMY_URL], name="test_webhook_error", level=logging.DEBUG, discord_level=logging.DEBUG
    )
    dlogger.debug("テストメッセージ")


def test_warning_does_not_raise_on_webhook_error(mocker: pytest_mock.MockerFixture) -> None:
    """Discord送信でWebhookErrorが発生してもwarningが例外を送出しないこと."""
    mocker.patch(
        "discord_logger.discord_logger.DiscordPublisher.publish",
        side_effect=WebhookError("送信失敗"),
    )
    dlogger = DiscordLogger([DUMMY_URL], name="test_webhook_error")
    dlogger.warning("テストメッセージ")


def test_error_does_not_raise_on_webhook_error(mocker: pytest_mock.MockerFixture) -> None:
    """Discord送信でWebhookErrorが発生してもerrorが例外を送出しないこと."""
    mocker.patch(
        "discord_logger.discord_logger.DiscordPublisher.publish",
        side_effect=WebhookError("送信失敗"),
    )
    dlogger = DiscordLogger([DUMMY_URL], name="test_webhook_error")
    dlogger.error("テストメッセージ")


def test_critical_does_not_raise_on_webhook_error(mocker: pytest_mock.MockerFixture) -> None:
    """Discord送信でWebhookErrorが発生してもcriticalが例外を送出しないこと."""
    mocker.patch(
        "discord_logger.discord_logger.DiscordPublisher.publish",
        side_effect=WebhookError("送信失敗"),
    )
    dlogger = DiscordLogger([DUMMY_URL], name="test_webhook_error")
    dlogger.critical("テストメッセージ")


def test_webhook_error_logs_warning_locally(
    mocker: pytest_mock.MockerFixture, capfd: pytest.CaptureFixture[str]
) -> None:
    """Discord送信失敗時にローカルログに警告が出力されること."""
    mocker.patch(
        "discord_logger.discord_logger.DiscordPublisher.publish",
        side_effect=WebhookError("送信失敗"),
    )
    dlogger = DiscordLogger([DUMMY_URL], name="test_webhook_warning")
    dlogger.info("テストメッセージ")
    captured = capfd.readouterr()
    assert "Discord送信に失敗しました" in captured.out
    assert "テストメッセージ" in captured.out
