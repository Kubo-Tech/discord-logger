"""ログフォーマットを提供するモジュール."""

import logging

# ログフォーマット
LOG_FORMAT = "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"

# 日時のフォーマット
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ColoredFormatter(logging.Formatter):
    """ログレベルに応じてコンソール出力に色を付けるフォーマッタ.

    `logging.StreamHandler` の `setFormatter` に設定して使う。ANSIエスケープを付けるため、
    ファイル出力やDiscordへの送信には使わない。

    Attributes:
        COLORS: ログレベル名からANSIカラーコードへの対応
        RESET: 色を解除するANSIコード
    """

    COLORS = {
        "DEBUG": "",  # デフォルト（白）
        "INFO": "\033[32m",  # 緑
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 赤
        "CRITICAL": "\033[31m",  # 赤
    }
    RESET = "\033[0m"

    def __init__(self, fmt: str = LOG_FORMAT, datefmt: str = DATE_FORMAT) -> None:
        """ColoredFormatterを初期化する.

        Args:
            fmt: ログフォーマット
            datefmt: 日時のフォーマット
        """
        super().__init__(fmt, datefmt=datefmt)

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
