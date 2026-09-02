"""標準loggingのハンドラとしてDiscordへ送信するモジュール."""

import logging

from discord_logger.publisher import DiscordPublisher


class DiscordHandler(logging.Handler):
    """ログレコードをDiscord Webhookへ送信するハンドラ.

    標準の `logging.Logger` に `addHandler` で付けて使う。付けたロガーの子ロガー
    （`getChild`）から伝播したレコードも送信されるため、ライブラリへ注入したロガーの
    ログをまとめてDiscordへ流せる。

    ERROR/CRITICALのレコードは、ユーザーIDが設定されていればメンションを付ける。
    2000文字を超えるメッセージは切り詰める。送信に失敗しても例外は送出せず、
    `logging.Handler.handleError` に委ねる（標準loggingの規約）。

    Attributes:
        publisher: 送信に使う DiscordPublisher
    """

    def __init__(
        self,
        webhook_urls: list[str],
        level: int = logging.INFO,
        discord_user_id: str = "",
        timeout: int = DiscordPublisher.DEFAULT_TIMEOUT,
    ) -> None:
        """DiscordHandlerを初期化する.

        Args:
            webhook_urls: 送信先のWebhook URLのリスト（1つ以上）
            level: このハンドラが扱う最低ログレベル
            discord_user_id: ERROR/CRITICALでメンションするDiscordのユーザーID。
                空文字列の場合は環境変数 DISCORD_LOGGER_USER_ID を参照する
            timeout: Webhook送信時のタイムアウト秒数

        Raises:
            WebhookError: webhook_urlsが空の場合、またはURLの形式が不正な場合
        """
        super().__init__(level)
        self.publisher = DiscordPublisher(
            webhook_urls=webhook_urls,
            name="discord_logger",
            discord_user_id=discord_user_id,
            timeout=timeout,
        )
        self.setFormatter(
            logging.Formatter(DiscordPublisher.LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        )

    def emit(self, record: logging.LogRecord) -> None:
        """レコードを整形してDiscordへ送信する.

        Args:
            record: ログレコード
        """
        try:
            message = self.format(record)
            self.publisher.send_with_mention(record.levelname, message)
        except Exception:
            self.handleError(record)
