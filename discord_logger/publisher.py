"""Discord Webhookへのメッセージ送信モジュール.

DiscordのWebhook URLを利用してメッセージを送信する機能を提供する。
"""

import inspect
import logging
import os
import re

import requests
from dotenv import load_dotenv

from discord_logger.exceptions import WebhookError
from discord_logger.logger import normalize_log_level

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

    # Discordメッセージの最大文字数
    DISCORD_MAX_LENGTH = 2000

    # 切り詰め時の省略記号
    TRUNCATION_SUFFIX = "\n...(メッセージが長すぎるため省略されました)"

    # Discord Webhook URLの正規表現パターン
    WEBHOOK_URL_PATTERN = re.compile(
        r"^https://(discord\.com|discordapp\.com)/api/webhooks/\d+/.+$"
    )

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
            WebhookError: webhook_urlsが空の場合、またはURLの形式が不正な場合
        """
        if not webhook_urls:
            raise WebhookError("webhook_urlsは1つ以上のURLを含む必要があります")
        self._validate_webhook_urls(webhook_urls)
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

    @classmethod
    def _validate_webhook_urls(cls, webhook_urls: list[str]) -> None:
        """各Webhook URLの形式を検証する.

        Args:
            webhook_urls: 検証対象のURLリスト

        Raises:
            WebhookError: URLの形式が不正な場合
        """
        invalid_urls = [url for url in webhook_urls if not cls.WEBHOOK_URL_PATTERN.match(url)]
        if invalid_urls:
            invalid_urls_text = ", ".join(invalid_urls)
            raise WebhookError(f"不正なWebhook URLが含まれています: {invalid_urls_text}")

    def send(self, message: str) -> None:
        """全てのWebhook URLにメッセージを送信する.

        メッセージがDiscordの文字数制限（2000文字）を超える場合、自動的に切り詰められる。

        Args:
            message: 送信するメッセージ（整形済み）

        Raises:
            WebhookError: Webhookへの送信に失敗した場合
        """
        truncated = self._truncate_message(message)
        data = {"content": truncated}
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

    def _format_message(self, level: str, message: str) -> str:
        """ログフォーマットに従ってメッセージを整形する.

        Args:
            level: ログレベル文字列（DEBUG, INFO, WARNING, ERROR, CRITICALのいずれか）
            message: ログメッセージ

        Returns:
            str: 整形済みのメッセージ

        Raises:
            ConfigError: 無効なログレベルが指定された場合
        """
        numeric_level = normalize_log_level(level)
        record = logging.LogRecord(
            name=self._name,
            level=numeric_level,
            pathname="",
            lineno=0,
            msg=message,
            args=None,
            exc_info=None,
        )
        return self._formatter.format(record)

    def _truncate_message(self, message: str) -> str:
        """メッセージがDiscordの文字数制限を超える場合に切り詰める.

        Args:
            message: 元のメッセージ

        Returns:
            str: 文字数制限内に収まるメッセージ
        """
        if len(message) <= self.DISCORD_MAX_LENGTH:
            return message
        truncated_length = self.DISCORD_MAX_LENGTH - len(self.TRUNCATION_SUFFIX)
        return message[:truncated_length] + self.TRUNCATION_SUFFIX
