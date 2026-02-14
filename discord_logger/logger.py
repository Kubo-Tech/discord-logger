"""ロガーモジュール.

Pythonの標準loggingインターフェースに準拠したロガーを提供する。
コンソール出力と日付ごとのローテーションファイル出力をサポートする。
"""

import inspect
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from dotenv import load_dotenv

from discord_logger.exceptions import ConfigError

load_dotenv()


class Logger:
    """ロガークラス.

    Pythonの標準loggingインターフェースに準拠したロガー。
    コンソール出力と日付ごとのファイルローテーションをサポートする。

    Attributes:
        name: ロガーの名前
        log_dir: ログファイルを保存するディレクトリパス
    """

    # ログフォーマット
    LOG_FORMAT = "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"

    def __init__(
        self,
        name: str = "",
        log_dir: str | None = None,
        level: int = logging.INFO,
    ) -> None:
        """ロガーを初期化する.

        Args:
            name: ロガーの名前（空文字列の場合は呼び出し元のディレクトリパスを使用）
            log_dir: ログファイルを保存するディレクトリパス。Noneの場合は環境変数を参照する
            level: ログレベル
        """
        # nameが空文字列の場合は呼び出し元のディレクトリパスを使用
        if not name:
            caller_frame = inspect.stack()[1]
            caller_file = caller_frame.filename
            name = os.path.dirname(os.path.abspath(caller_file))

        # log_dirがNoneの場合は環境変数から読み込みを試みる
        if log_dir is None:
            env_log_dir = os.environ.get("DISCORD_LOGGER_LOG_DIR")
            if env_log_dir:
                log_dir = env_log_dir

        self.name = name
        self.log_dir = log_dir
        self._logger = logging.getLogger(name)
        normalized_level = normalize_log_level(level)
        self._logger.setLevel(normalized_level)
        self._logger.propagate = False

        self._clear_managed_handlers()
        self._setup_console_handler()
        if log_dir is not None:
            self._setup_file_handler(log_dir)

    def setLevel(self, level: int | str) -> None:  # noqa: N802
        """ログレベルを設定する.

        Args:
            level: ログレベル（logging.INFO等の整数、または"INFO"等の文字列）
        """
        numeric_level = normalize_log_level(level)
        self._logger.setLevel(numeric_level)
        for handler in self._logger.handlers:
            handler.setLevel(numeric_level)

    def info(self, message: str) -> None:
        """INFOレベルのログを出力する.

        Args:
            message: ログメッセージ
        """
        self._logger.info(message)

    def debug(self, message: str) -> None:
        """DEBUGレベルのログを出力する.

        Args:
            message: ログメッセージ
        """
        self._logger.debug(message)

    def warning(self, message: str) -> None:
        """WARNINGレベルのログを出力する.

        Args:
            message: ログメッセージ
        """
        self._logger.warning(message)

    def error(self, message: str) -> None:
        """ERRORレベルのログを出力する.

        Args:
            message: ログメッセージ
        """
        self._logger.error(message)

    def critical(self, message: str) -> None:
        """CRITICALレベルのログを出力する.

        Args:
            message: ログメッセージ
        """
        self._logger.critical(message)

    def _setup_console_handler(self) -> None:
        """コンソール出力用ハンドラを設定する."""
        console_handler = logging.StreamHandler(sys.stdout)
        setattr(console_handler, "_discord_logger_managed", True)
        console_handler.setLevel(self._logger.level)
        formatter = ColoredFormatter(self.LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

    def _setup_file_handler(self, log_dir: str) -> None:
        """ファイル出力用ハンドラを設定する.

        日付ごとにログファイルをローテーションする。

        Args:
            log_dir: ログファイルを保存するディレクトリパス
        """
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "discord_logger.log")

        file_handler = TimedRotatingFileHandler(
            log_file,
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8",
        )
        setattr(file_handler, "_discord_logger_managed", True)
        file_handler.suffix = "%Y%m%d"
        file_handler.setLevel(self._logger.level)
        formatter = logging.Formatter(self.LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

    def _clear_managed_handlers(self) -> None:
        """discord-loggerが設定した既存ハンドラを除去する."""
        for handler in list(self._logger.handlers):
            if getattr(handler, "_discord_logger_managed", False):
                self._logger.removeHandler(handler)
                handler.close()


class ColoredFormatter(logging.Formatter):
    """コンソール出力用の色付きフォーマッタ.

    ログレベルに応じて出力に色を付ける。
    """

    # ANSIカラーコード
    COLORS = {
        "DEBUG": "",  # デフォルト（白）
        "INFO": "\033[32m",  # 緑
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 赤
        "CRITICAL": "\033[31m",  # 赤
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """ログレコードをフォーマットして色を付ける.

        Args:
            record: ログレコード

        Returns:
            str: フォーマット済みのログメッセージ
        """
        log_color = self.COLORS.get(record.levelname, "")
        formatted = super().format(record)
        if log_color:
            return f"{log_color}{formatted}{self.RESET}"
        return formatted


def normalize_log_level(level: int | str) -> int:
    """ログレベルを整数値に正規化する.

    Args:
        level: ログレベル（整数または文字列）

    Returns:
        int: loggingモジュールで扱える整数ログレベル

    Raises:
        ConfigError: 文字列ログレベルが不正な場合
    """
    if isinstance(level, int):
        return level

    level_name = level.upper()
    level_mapping = logging.getLevelNamesMapping()
    if level_name not in level_mapping:
        raise ConfigError(f"不正なログレベルです: {level}")
    return level_mapping[level_name]
