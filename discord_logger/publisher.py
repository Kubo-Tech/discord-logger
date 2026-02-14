"""Discord Webhookへのメッセージ送信モジュール.

DiscordのWebhook URLを利用してメッセージを送信する機能を提供する。
"""

import inspect
import logging
import os

import requests
from dotenv import load_dotenv

from discord_logger.exceptions import WebhookError

load_dotenv()


class DiscordPublisher:
    """Discord Webhookへメッセージを送信するクラス.

    複数のWebhook URLに対して同じメッセージを送信できる。

    Attributes:
        webhook_urls: DiscordのWebhook URLのリスト
        _name: ロガー名
        _discord_user_id: DiscordのユーザーID。指定した場合、ERROR/CRITICALでメンションする
        _formatter: ログフォーマット用のFormatterインスタンス
    """

    # ログフォーマット
    LOG_FORMAT = "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"

    # メンション対象のログレベル
    MENTION_LEVELS = {"ERROR", "CRITICAL"}

    def __init__(
        self,
        webhook_urls: list[str],
        name: str = "",
        discord_user_id: str = "",
    ) -> None:
        """DiscordPublisherを初期化する.

        Args:
            webhook_urls: DiscordのWebhook URLのリスト
            name: ロガー名（フォーマットに使用。空文字列の場合は呼び出し元のディレクトリパスを使用）
            discord_user_id: DiscordのユーザーID。指定した場合、ERROR/CRITICALでメンションする

        Raises:
            WebhookError: webhook_urlsが空の場合
        """
        if not webhook_urls:
            raise WebhookError("webhook_urlsは1つ以上のURLを含む必要があります")
        # nameが空文字列の場合は呼び出し元のディレクトリパスを使用
        if not name:
            caller_frame = inspect.stack()[1]
            caller_file = caller_frame.filename
            name = os.path.dirname(os.path.abspath(caller_file))

        # discord_user_idが空文字列の場合は環境変数から読み込みを試みる
        if not discord_user_id:
            discord_user_id = os.environ.get("DISCORD_LOGGER_USER_ID", "")

        self.webhook_urls = webhook_urls
        self._name = name
        self._discord_user_id = discord_user_id
        self._formatter = logging.Formatter(self.LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

    def _format_message(self, level: str, message: str) -> str:
        """ログフォーマットに従ってメッセージを整形する.

        Args:
            level: ログレベル文字列
            message: ログメッセージ

        Returns:
            str: 整形済みのメッセージ
        """
        record = logging.LogRecord(
            name=self._name,
            level=getattr(logging, level.upper()),
            pathname="",
            lineno=0,
            msg=message,
            args=None,
            exc_info=None,
        )
        return self._formatter.format(record)

    def send(self, message: str) -> None:
        """全てのWebhook URLにメッセージを送信する.

        Args:
            message: 送信するメッセージ（整形済み）

        Raises:
            WebhookError: Webhookへの送信に失敗した場合
        """
        data = {"content": message}
        failed_urls: list[str] = []
        last_error: requests.RequestException | None = None
        for url in self.webhook_urls:
            try:
                response = requests.post(url, json=data, timeout=10)
                response.raise_for_status()
            except requests.RequestException as error:
                failed_urls.append(url)
                last_error = error

        if failed_urls:
            failed_urls_text = ", ".join(failed_urls)
            raise WebhookError(
                f"Webhook送信に失敗したURLがあります: {failed_urls_text}"
            ) from last_error

    def publish(self, level: str, message: str) -> None:
        """ログフォーマットに従ってメッセージを整形し送信する.

        ERROR/CRITICALかつdiscord_user_idが設定されている場合、
        メッセージの先頭にメンションを付与する。

        Args:
            level: ログレベル文字列
            message: ログメッセージ
        """
        formatted = self._format_message(level, message)
        if self._discord_user_id and level.upper() in self.MENTION_LEVELS:
            formatted = f"<@{self._discord_user_id}>\n{formatted}"
        self.send(formatted)
