"""DiscordLogger.set_discord_levelメソッドのテスト."""

import logging

import pytest

from discord_logger import DiscordLogger
from discord_logger.exceptions import ConfigError

DUMMY_URL = "https://discord.com/api/webhooks/dummy"


# 正常系
def test_set_discord_level_with_int() -> None:
    """整数でDiscord送信レベルを設定できること."""
    dlogger = DiscordLogger([DUMMY_URL])
    dlogger.set_discord_level(logging.ERROR)
    assert dlogger.discord_level == logging.ERROR


def test_set_discord_level_with_string() -> None:
    """文字列でDiscord送信レベルを設定できること."""
    dlogger = DiscordLogger([DUMMY_URL])
    dlogger.set_discord_level("CRITICAL")
    assert dlogger.discord_level == logging.CRITICAL


def test_set_discord_level_with_lowercase_string() -> None:
    """小文字の文字列でDiscord送信レベルを設定できること."""
    dlogger = DiscordLogger([DUMMY_URL])
    dlogger.set_discord_level("warning")
    assert dlogger.discord_level == logging.WARNING


def test_set_discord_level_invalid_string_raises_config_error() -> None:
    """不正な文字列ログレベルでConfigErrorが発生すること."""
    dlogger = DiscordLogger([DUMMY_URL])

    with pytest.raises(ConfigError, match="不正なログレベルです"):
        dlogger.set_discord_level("INVALID_LEVEL")
