# discord-logger

## 概要

`discord-logger`は、DiscordのWebhookを利用したロギングライブラリです。
標準の`logging`に組み込むハンドラ`DiscordHandler`と、Webhookへの送信そのものを行う`DiscordPublisher`を提供します。
ハンドラは`logging.Logger`に`addHandler`で付けるだけで使え、子ロガー（`getChild`）から伝播したログも送信されるため、ライブラリへ注入したロガーのログをまとめてDiscordへ流せます。


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
2. 作成したURLをリストで`DiscordHandler`に渡します
3. 必要に応じて環境変数を設定してください（`.env.example`を参照）


## 環境変数

| 環境変数 | 説明 | デフォルト |
|---|---|---|
| `DISCORD_LOGGER_USER_ID` | DiscordのユーザーID。ERROR/CRITICALレベルのログ送信時にメンションする | なし |

## ログフォーマット

ハンドラの既定フォーマットは以下の通りです。`setFormatter`で変更できます。

```
[%(asctime)s][%(name)s][%(levelname)s] %(message)s
```

出力例：

```
[2026-02-14 12:00:00][example][INFO] This is an info message.
```

## 使い方

### 基本的な使い方

```python
import logging

from discord_logger import DiscordHandler

logger = logging.getLogger("my_app")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.addHandler(DiscordHandler(["https://discord.com/api/webhooks/your_webhook_url"]))

logger.info("コンソールとDiscordの両方に出力される")
logger.error("ERROR/CRITICALはユーザーIDが設定されていればメンション付きで送信される")
```

### ライブラリへ注入したロガーのログを送る

ハンドラを付けたロガーの子ロガーは、伝播によって同じハンドラへ届きます。
各ライブラリへ`logger.getChild(...)`で子ロガーを渡すと、ライブラリ内部のERRORもDiscordに届きます。

```python
logger = logging.getLogger("my_app")
logger.addHandler(DiscordHandler(webhook_urls, level=logging.ERROR))

component = SomeLibrary(logger=logger.getChild("some_library"))  # 内部のERRORがDiscordへ届く
```

### 用途ごとにチャンネルを分ける

専用のロガーに別のWebhookのハンドラを付け、`propagate = False`にすると、そのロガーのログだけを別チャンネルへ流せます。

```python
publish_logger = logging.getLogger("my_app.publish")
publish_logger.propagate = False
publish_logger.addHandler(DiscordHandler(publish_webhook_urls))

publish_logger.info("配信用チャンネルにだけ送信される")
```

### ERROR/CRITICALでメンションする

`discord_user_id`を指定すると、ERROR/CRITICALレベルのログ送信時に指定ユーザーにメンションします。
環境変数`DISCORD_LOGGER_USER_ID`でも設定可能です。

```python
handler = DiscordHandler(webhook_urls, discord_user_id="123456789012345678")
```

### DiscordPublisherのみ使用する場合

```python
from discord_logger import DiscordPublisher

publisher = DiscordPublisher(
    webhook_urls=["https://discord.com/api/webhooks/your_webhook_url"],
    name="my_app",
)
publisher.publish("INFO", "Discordにのみ送信")
```


## パラメータ一覧

### DiscordHandler

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| `webhook_urls` | `list[str]` | （必須） | DiscordのWebhook URLのリスト |
| `level` | `int` | `logging.INFO` | このハンドラが扱う最低ログレベル |
| `discord_user_id` | `str` | `""` | DiscordのユーザーID。空文字列の場合は環境変数を参照 |
| `timeout` | `int` | 10 | Webhook送信時のタイムアウト秒数 |

### DiscordPublisher

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| `webhook_urls` | `list[str]` | （必須） | DiscordのWebhook URLのリスト |
| `name` | `str` | `""` | ロガー名。空文字列の場合は呼び出し元のディレクトリパスを使用 |
| `discord_user_id` | `str` | `""` | DiscordのユーザーID。空文字列の場合は環境変数を参照 |
| `timeout` | `int` | 10 | Webhook送信時のタイムアウト秒数 |

## エラーハンドリング

本ライブラリが送出する例外は全て`DiscordLoggerError`を基底クラスとしています：

| 例外クラス | 説明 |
|---|---|
| `DiscordLoggerError` | 基底例外クラス |
| `WebhookError` | Webhook URLが空・不正な場合、または送信に失敗した場合 |
| `ConfigError` | ログレベルの文字列が不正な場合 |

`DiscordHandler`はハンドラ生成時のURL検証で`WebhookError`を送出します。
送信時の失敗はハンドラから例外を送出せず、`logging.Handler.handleError`に委ねます（標準loggingの規約）。
