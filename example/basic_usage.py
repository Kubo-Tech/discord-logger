"""discord-loggerの基本的な使用例."""

import logging

from discord_logger import DiscordLogger

if __name__ == "__main__":

    # 設定
    webhook_urls = ["YOUR_WEBHOOK_URL_HERE"]  # DiscordのWebhook URLを指定
    discord_user_id = "YOUR_DISCORD_USER_ID_HERE"  # メンションしたいユーザーのIDを指定

    # DiscordLoggerのインスタンスを作成
    dlogger = DiscordLogger(webhook_urls, name="example", discord_user_id=discord_user_id)

    # ログレベルを設定
    dlogger.setLevel("DEBUG")

    # ログを出力（コンソール + Discord）
    dlogger.debug("This is a debug message.")
    dlogger.info("This is an info message.")
    dlogger.warning("This is a warning message.")
    dlogger.error("This is an error message.")
    dlogger.critical("This is a critical message.")

    # Discord送信レベルをWARNING以上に変更
    dlogger.set_discord_level(logging.WARNING)

    # INFOはコンソールのみ、WARNING以上はコンソール + Discord
    dlogger.info("これはコンソールのみに出力される")
    dlogger.warning("これはコンソールとDiscordの両方に出力される")
