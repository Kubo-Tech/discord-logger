"""ColoredFormatterの単体テスト."""

import logging

import pytest

from discord_logger.formatter import DATE_FORMAT, LOG_FORMAT, ColoredFormatter


def _record(level: int, message: str = "テストメッセージ") -> logging.LogRecord:
    """テスト用のログレコードを作成する."""
    return logging.LogRecord(
        name="test", level=level, pathname=__file__, lineno=1, msg=message, args=(), exc_info=None
    )


# 正常系
@pytest.mark.parametrize(
    ("level", "color"),
    [
        (logging.INFO, "\033[32m"),
        (logging.WARNING, "\033[33m"),
        (logging.ERROR, "\033[31m"),
        (logging.CRITICAL, "\033[31m"),
    ],
)
def test_wraps_message_with_level_color(level: int, color: str) -> None:
    """ログレベルに応じた色で囲むこと."""
    result = ColoredFormatter().format(_record(level))

    assert result.startswith(color)
    assert result.endswith(ColoredFormatter.RESET)
    assert "テストメッセージ" in result


def test_debug_is_not_colored() -> None:
    """DEBUGは色を付けないこと."""
    result = ColoredFormatter().format(_record(logging.DEBUG))

    assert "\033[" not in result


def test_uses_default_format() -> None:
    """既定のフォーマットと日時フォーマットを使うこと."""
    formatter = ColoredFormatter()

    assert formatter._fmt == LOG_FORMAT
    assert formatter.datefmt == DATE_FORMAT


def test_accepts_custom_format() -> None:
    """フォーマットを指定できること."""
    result = ColoredFormatter(fmt="%(levelname)s: %(message)s").format(_record(logging.INFO))

    assert "INFO: テストメッセージ" in result
