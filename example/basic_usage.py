"""discord-loggerの基本的な使用例.

標準のloggingにDiscordHandlerを付け、運用ログ用と配信用でチャンネルを分ける構成を示す。
"""

import logging

from discord_logger import DiscordHandler

if __name__ == "__main__":
    # 設定
    log_webhook_urls = ["YOUR_LOG_WEBHOOK_URL_HERE"]  # 運用ログ用チャンネルのWebhook URL
    publish_webhook_urls = ["YOUR_PUBLISH_WEBHOOK_URL_HERE"]  # 配信用チャンネルのWebhook URL
    discord_user_id = "YOUR_DISCORD_USER_ID_HERE"  # ERROR以上でメンションするユーザーのID

    # 運用ログ: アプリのロガーにハンドラを付ける。子ロガーのログも伝播して送信される
    logger = logging.getLogger("example")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(DiscordHandler(log_webhook_urls, discord_user_id=discord_user_id))

    logger.info("処理を開始します")
    logger.getChild("library").warning("ライブラリ内部の警告も送信される")
    logger.error("エラーはメンション付きで送信される")

    # 配信: 専用のロガーに別チャンネルのハンドラを付け、上位へ伝播させない
    publish_logger = logging.getLogger("example.publish")
    publish_logger.setLevel(logging.INFO)
    publish_logger.propagate = False
    publish_logger.addHandler(DiscordHandler(publish_webhook_urls))

    publish_logger.info("配信用チャンネルにだけ送信される")
