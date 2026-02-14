"""DiscordLoggerモジュール.

LoggerとDiscordPublisherを統合し、ログレベルに応じてDiscordへの送信を制御する。
"""

import inspect
import logging
import os

from discord_logger.logger import Logger, normalize_log_level
from discord_logger.publisher import DiscordPublisher


class DiscordLogger(Logger):
    """LoggerとDiscordPublisherを統合したロガークラス.

    ローカルのログ出力に加え、ログレベルに応じてDiscordのWebhookにも
    メッセージを送信する。

    Attributes:
        name: ロガーの名前
        discord_publisher: DiscordPublisherインスタンス
        discord_level: Discord送信のしきい値ログレベル
    """

    def __init__(
        self,
        webhook_urls: list[str],
        name: str = "",
        log_dir: str | None = None,
        level: int = logging.INFO,
        discord_level: int = logging.INFO,
        discord_user_id: str = "",
    ) -> None:
        """DiscordLoggerを初期化する.

        Args:
            webhook_urls: DiscordのWebhook URLのリスト
            name: ロガーの名前（空文字列の場合は呼び出し元のディレクトリパスを使用）
            log_dir: ログファイルを保存するディレクトリパス。Noneの場合はファイル出力しない
            level: ログレベル
            discord_level: Discord送信のしきい値ログレベル。このレベル以上のログをDiscordに送信する
            discord_user_id: DiscordのユーザーID。指定した場合、ERROR/CRITICALでメンションする
        """
        # nameが空文字列の場合は呼び出し元のディレクトリパスを使用
        if not name:
            caller_frame = inspect.stack()[1]
            caller_file = caller_frame.filename
            name = os.path.dirname(os.path.abspath(caller_file))

        # discord_user_idが空文字列の場合は環境変数から読み込みを試みる
        if not discord_user_id:
            discord_user_id = os.environ.get("DISCORD_LOGGER_USER_ID", "")

        super().__init__(name=name, log_dir=log_dir, level=level)
        self.discord_publisher = DiscordPublisher(
            webhook_urls=webhook_urls, name=name, discord_user_id=discord_user_id
        )
        self.discord_level = discord_level

    def set_discord_level(self, level: int | str) -> None:
        """Discord送信のしきい値ログレベルを設定する.

        Args:
            level: ログレベル（logging.INFO等の整数、または"INFO"等の文字列）
        """
        self.discord_level = normalize_log_level(level)

    def info(self, message: str) -> None:
        """INFOレベルのログを出力する.

        Args:
            message: ログメッセージ
        """
        super().info(message)
        if self._should_send_to_discord(logging.INFO):
            self.discord_publisher.publish("INFO", message)

    def debug(self, message: str) -> None:
        """DEBUGレベルのログを出力する.

        Args:
            message: ログメッセージ
        """
        super().debug(message)
        if self._should_send_to_discord(logging.DEBUG):
            self.discord_publisher.publish("DEBUG", message)

    def warning(self, message: str) -> None:
        """WARNINGレベルのログを出力する.

        Args:
            message: ログメッセージ
        """
        super().warning(message)
        if self._should_send_to_discord(logging.WARNING):
            self.discord_publisher.publish("WARNING", message)

    def error(self, message: str) -> None:
        """ERRORレベルのログを出力する.

        Args:
            message: ログメッセージ
        """
        super().error(message)
        if self._should_send_to_discord(logging.ERROR):
            self.discord_publisher.publish("ERROR", message)

    def critical(self, message: str) -> None:
        """CRITICALレベルのログを出力する.

        Args:
            message: ログメッセージ
        """
        super().critical(message)
        if self._should_send_to_discord(logging.CRITICAL):
            self.discord_publisher.publish("CRITICAL", message)

    def _should_send_to_discord(self, level: int) -> bool:
        """指定されたログレベルがDiscord送信対象かどうかを判定する.

        Args:
            level: ログレベル

        Returns:
            bool: Discord送信対象であればTrue
        """
        return level >= self.discord_level
