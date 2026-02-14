# discord-logger

## 概要

`discord-logger`は、DiscordのWebhookを利用したロギングライブラリです。
Pythonの標準loggingインターフェースに準拠し、ローカルログとDiscordへのメッセージ送信を統合的に扱えます。


## 動作要件

- Python 3.12以上


## 依存パッケージ

- requests
- python-dotenv


## インストール

```bash
pip install -e /path/to/discord-logger
```


## セットアップ

1. DiscordでWebhook URLを作成してください
2. 作成したURLをリストでDiscordLoggerに渡します
3. 必要に応じて環境変数を設定してください（`.env.example`を参照）


## 環境変数

| 環境変数 | 説明 | デフォルト |
|---|---|---|
| `DISCORD_LOGGER_LOG_DIR` | ログファイルの出力先ディレクトリ。省略時はファイル出力なし | なし |
| `DISCORD_LOGGER_USER_ID` | DiscordのユーザーID。ERROR/CRITICALレベルのログ送信時にメンションする | なし |

## ログフォーマット

出力されるログのフォーマットは以下の通りです：

```
[%(asctime)s][%(name)s][%(levelname)s] %(message)s
```

出力例：

```
[2026-02-14 12:00:00][example][INFO] This is an info message.
```

コンソール出力ではログレベルに応じて色が付きます：

| ログレベル | 色 |
|---|---|
| DEBUG | デフォルト（白） |
| INFO | 緑 |
| WARNING | 黄色 |
| ERROR | 赤 |
| CRITICAL | 赤 |

## 使い方

### 基本的な使い方

```python
from discord_logger import DiscordLogger

# DiscordのWebhook URLを指定
webhook_urls = ["https://discord.com/api/webhooks/your_webhook_url"]

# DiscordLoggerのインスタンスを作成
dlogger = DiscordLogger(webhook_urls, name="example")

# ログレベルを設定
dlogger.setLevel("DEBUG")

# ログを出力（コンソール + Discord）
dlogger.debug("This is a debug message.")
dlogger.info("This is an info message.")
dlogger.warning("This is a warning message.")
dlogger.error("This is an error message.")
dlogger.critical("This is a critical message.")
```

### Loggerのみ使用する場合

```python
from discord_logger import Logger

# ファイル出力つきのロガーを作成
# log_dir省略時は環境変数DISCORD_LOGGER_LOG_DIRを参照する
logger = Logger(name="my_app", log_dir="/var/log/my_app")
logger.info("ローカルログのみ出力")
```

### DiscordPublisherのみ使用する場合

```python
from discord_logger import DiscordPublisher

# Discord送信専用
publisher = DiscordPublisher(
    webhook_urls=["https://discord.com/api/webhooks/your_webhook_url"],
    name="my_app",
)
publisher.publish("INFO", "Discordにのみ送信")
```

### Discord送信のログレベルを制御する

```python
import logging
from discord_logger import DiscordLogger

dlogger = DiscordLogger(
    webhook_urls=["https://discord.com/api/webhooks/your_webhook_url"],
    discord_level=logging.WARNING,  # WARNING以上のみDiscordに送信
)

dlogger.info("これはコンソールのみに出力される")
dlogger.warning("これはコンソールとDiscordの両方に出力される")

# 後からDiscord送信ログレベルを変更することもできる
dlogger.set_discord_level(logging.ERROR)
```

### ERROR/CRITICALでメンションする

`discord_user_id`を指定すると、ERROR/CRITICALレベルのログ送信時に指定ユーザーにメンションします。
環境変数`DISCORD_LOGGER_USER_ID`でも設定可能です。

```python
from discord_logger import DiscordLogger

dlogger = DiscordLogger(
    webhook_urls=["https://discord.com/api/webhooks/your_webhook_url"],
    discord_user_id="123456789012345678",  # DiscordのユーザーID
)

dlogger.info("メンションなし")
dlogger.error("メンション付きでDiscordに送信される")
```


## パラメータ一覧

### DiscordLogger

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| `webhook_urls` | `list[str]` | （必須） | DiscordのWebhook URLのリスト |
| `name` | `str` | `""` | ロガーの名前。空文字列の場合は呼び出し元のディレクトリパスを使用 |
| `log_dir` | `str \| None` | `None` | ログファイルを保存するディレクトリパス。Noneの場合は環境変数を参照 |
| `level` | `int` | `logging.INFO` | ログレベル |
| `discord_level` | `int` | `logging.INFO` | Discord送信のしきい値ログレベル |
| `discord_user_id` | `str` | `""` | DiscordのユーザーID。空文字列の場合は環境変数を参照 |

### Logger

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| `name` | `str` | `""` | ロガーの名前。空文字列の場合は呼び出し元のディレクトリパスを使用 |
| `log_dir` | `str \| None` | `None` | ログファイルを保存するディレクトリパス。Noneの場合は環境変数を参照 |
| `level` | `int` | `logging.INFO` | ログレベル |

### DiscordPublisher

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| `webhook_urls` | `list[str]` | （必須） | DiscordのWebhook URLのリスト |
| `name` | `str` | `""` | ロガー名。空文字列の場合は呼び出し元のディレクトリパスを使用 |
| `discord_user_id` | `str` | `""` | DiscordのユーザーID。空文字列の場合は環境変数を参照 |

## エラーハンドリング

本ライブラリが送出する例外は全て`DiscordLoggerError`を基底クラスとしています：

| 例外クラス | 説明 |
|---|---|
| `DiscordLoggerError` | 基底例外クラス |
| `WebhookError` | Webhook送信に失敗した場合 |
| `ConfigError` | 設定値が不正な場合 |
