"""Logger.setLevelメソッドのテスト."""

import logging

import pytest

from discord_logger import Logger
from discord_logger.exceptions import ConfigError


# 正常系
def test_set_level_with_int() -> None:
    """整数でログレベルを設定できること."""
    logger = Logger(name="test_setlevel_int")
    logger.setLevel(logging.DEBUG)
    assert logger._logger.level == logging.DEBUG


def test_set_level_with_string() -> None:
    """文字列でログレベルを設定できること."""
    logger = Logger(name="test_setlevel_str")
    logger.setLevel("WARNING")
    assert logger._logger.level == logging.WARNING


def test_set_level_with_lowercase_string() -> None:
    """小文字の文字列でログレベルを設定できること."""
    logger = Logger(name="test_setlevel_lower")
    logger.setLevel("debug")
    assert logger._logger.level == logging.DEBUG


def test_set_level_updates_handlers() -> None:
    """setLevelが全てのハンドラのレベルも更新すること."""
    logger = Logger(name="test_setlevel_handlers")
    logger.setLevel(logging.ERROR)
    for handler in logger._logger.handlers:
        assert handler.level == logging.ERROR


def test_set_level_invalid_string_raises_config_error() -> None:
    """不正な文字列ログレベルでConfigErrorが発生すること."""
    logger = Logger(name="test_setlevel_invalid")

    with pytest.raises(ConfigError, match="不正なログレベルです"):
        logger.setLevel("INVALID_LEVEL")
