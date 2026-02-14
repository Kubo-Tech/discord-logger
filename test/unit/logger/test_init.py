"""Logger.__init__メソッドのテスト."""

import logging
import os
import tempfile

import pytest

from discord_logger import Logger


# 正常系
def test_init_default_parameters() -> None:
    """デフォルトパラメータでLoggerが初期化されること."""
    logger = Logger()
    # nameが空文字列の場合は呼び出し元のディレクトリパスが設定される
    expected_dir = os.path.dirname(os.path.abspath(__file__))
    assert logger.name == expected_dir
    assert logger.log_dir is None


def test_init_custom_name() -> None:
    """カスタム名でLoggerが初期化されること."""
    logger = Logger(name="test_app")
    assert logger.name == "test_app"


def test_init_with_log_dir() -> None:
    """log_dirを指定するとファイルハンドラが設定されること."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = Logger(name="test_file_logger", log_dir=tmpdir)
        assert logger.log_dir == tmpdir
        # ログファイルが作成されていること
        log_file = os.path.join(tmpdir, "discord_logger.log")
        assert os.path.exists(log_file)


def test_init_custom_level() -> None:
    """カスタムログレベルでLoggerが初期化されること."""
    logger = Logger(name="test_level_logger", level=logging.DEBUG)
    assert logger._logger.level == logging.DEBUG


def test_init_creates_log_directory() -> None:
    """存在しないディレクトリが自動的に作成されること."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = os.path.join(tmpdir, "nested", "dir")
        logger = Logger(name="test_nested_dir", log_dir=log_dir)
        assert os.path.isdir(log_dir)
        assert logger.log_dir == log_dir


def test_init_has_console_handler() -> None:
    """コンソールハンドラが設定されること."""
    logger = Logger(name="test_console_handler")
    handler_types = [type(h) for h in logger._logger.handlers]
    assert logging.StreamHandler in handler_types


def test_init_has_file_handler_when_log_dir() -> None:
    """log_dir指定時にファイルハンドラが設定されること."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = Logger(name="test_file_handler", log_dir=tmpdir)
        handler_types = [type(h).__name__ for h in logger._logger.handlers]
        assert "TimedRotatingFileHandler" in handler_types


def test_init_log_dir_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """環境変数からlog_dirが読み込まれること."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("DISCORD_LOGGER_LOG_DIR", tmpdir)
        logger = Logger(name="test_env_log_dir")
        assert logger.log_dir == tmpdir


def test_init_log_dir_arg_overrides_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """引数のlog_dirが環境変数より優先されること."""
    with tempfile.TemporaryDirectory() as tmpdir_env:
        with tempfile.TemporaryDirectory() as tmpdir_arg:
            monkeypatch.setenv("DISCORD_LOGGER_LOG_DIR", tmpdir_env)
            logger = Logger(name="test_arg_override", log_dir=tmpdir_arg)
            assert logger.log_dir == tmpdir_arg


def test_init_log_dir_none_without_env() -> None:
    """環境変数が未設定の場合log_dirがNoneのままであること."""
    logger = Logger(name="test_no_env")
    assert logger.log_dir is None


def test_init_same_name_reconfigures_handlers() -> None:
    """同じ名前で再初期化したときにハンドラ構成が更新されること."""
    logger_name = "test_reconfigure_logger"

    _ = Logger(name=logger_name, log_dir=None)
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = Logger(name=logger_name, log_dir=tmpdir)

        handler_types = [type(h).__name__ for h in logger._logger.handlers]
        assert "TimedRotatingFileHandler" in handler_types
        assert logger.log_dir == tmpdir
