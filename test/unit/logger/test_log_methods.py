"""Loggerのログ出力メソッドのテスト."""

import logging

import pytest

from discord_logger import Logger


# 正常系
def test_info_outputs_message(capfd: pytest.CaptureFixture[str]) -> None:
    """infoメソッドでメッセージが出力されること."""
    logger = Logger(name="test_info_output")
    logger.info("テストINFOメッセージ")
    captured = capfd.readouterr()
    assert "テストINFOメッセージ" in captured.out


def test_debug_outputs_message(capfd: pytest.CaptureFixture[str]) -> None:
    """debugメソッドでメッセージが出力されること."""
    logger = Logger(name="test_debug_output", level=logging.DEBUG)
    logger.debug("テストDEBUGメッセージ")
    captured = capfd.readouterr()
    assert "テストDEBUGメッセージ" in captured.out


def test_warning_outputs_message(capfd: pytest.CaptureFixture[str]) -> None:
    """warningメソッドでメッセージが出力されること."""
    logger = Logger(name="test_warning_output")
    logger.warning("テストWARNINGメッセージ")
    captured = capfd.readouterr()
    assert "テストWARNINGメッセージ" in captured.out


def test_error_outputs_message(capfd: pytest.CaptureFixture[str]) -> None:
    """errorメソッドでメッセージが出力されること."""
    logger = Logger(name="test_error_output")
    logger.error("テストERRORメッセージ")
    captured = capfd.readouterr()
    assert "テストERRORメッセージ" in captured.out


def test_critical_outputs_message(capfd: pytest.CaptureFixture[str]) -> None:
    """criticalメソッドでメッセージが出力されること."""
    logger = Logger(name="test_critical_output")
    logger.critical("テストCRITICALメッセージ")
    captured = capfd.readouterr()
    assert "テストCRITICALメッセージ" in captured.out


def test_log_format_contains_name(capfd: pytest.CaptureFixture[str]) -> None:
    """ログフォーマットにロガー名が含まれること."""
    logger = Logger(name="my_test_logger")
    logger.info("フォーマットテスト")
    captured = capfd.readouterr()
    assert "my_test_logger" in captured.out


def test_log_format_contains_level(capfd: pytest.CaptureFixture[str]) -> None:
    """ログフォーマットにログレベルが含まれること."""
    logger = Logger(name="test_format_level")
    logger.warning("レベルテスト")
    captured = capfd.readouterr()
    assert "WARNING" in captured.out


def test_debug_not_shown_at_info_level(capfd: pytest.CaptureFixture[str]) -> None:
    """INFOレベル設定時にDEBUGメッセージが出力されないこと."""
    logger = Logger(name="test_debug_hidden", level=logging.INFO)
    logger.debug("表示されないメッセージ")
    captured = capfd.readouterr()
    assert "表示されないメッセージ" not in captured.out
