
# 日付カウントダウンBot

このリポジトリは、Discord上で指定したイベントのカウントダウンを管理・通知するBotのコードを提供します。指定した時間にイベントまでの日数を通知したり、イベントの追加や削除を行ったりできます。

## 必要要件

以下のソフトウェアとパッケージが必要です：

- Python 3.8以上
- 必須パッケージ（`requirements.txt`で管理）
  - `discord.py`
  - `python-dotenv`

## インストール方法と実行

1. リポジトリをクローンします。

   ```bash
   git clone https://github.com/kuwaharu-git/date-countdown-bot.git
   cd date-countdown-bot
   ```

2. 必要なPythonパッケージをインストールします。

   ```bash
   pip install -r requirements.txt
   ```

3. `.env` ファイルを作成して以下の内容を記載します：

   ```env
   DISCORD_TOKEN=あなたのDiscordボットのトークン
   CHANNEL_ID=通知を送信するチャンネルのID
   ADMIN_CHANNEL_ID=起動時の通知を送信する管理者用チャンネルのID(CHANEL_IDと同じも可)
   ```

4. Botを起動します：

   ```bash
   python date_countdown_bot.py
   ```

5. Botが起動すると、指定されたチャンネルに「日付カウントダウンBotが起動しました。」と通知されます。

## Botの使用方法

Botで利用可能なコマンドとその例は以下の通りです。

```
1. イベントを追加するコマンド
   !add_event <イベント名> <yyyy-mm-dd>
   例: !add_event 新年 2025-01-01

2. イベントを削除するコマンド
   !remove_event <イベントID>
   例: !remove_event event1

3. 登録されたイベントの一覧表示コマンド
   !list_events

4. イベントのカウントダウン表示コマンド
   !countdown
```

毎日午前7時（日本標準時）に、登録されたイベントまでの日数を指定のチャンネルに自動的に通知します。

イベントまでの日数は当日が０日になるようになっています。

イベントまでの残り日数の計算の際、当日の時間も、イベントの時間も７時に設定しています。(計算がやりやすいようにするため)。もし、残り日数の配信時間を変更する場合は**TIMES**のリストの中身の変更と、**add_event**関数の時間を設定するところの変更が必要です。

## ファイル構成

```
.
├── date_countdown_bot.py    # メインスクリプト
├── events.json              # イベントデータ（自動生成・保存）
├── requirements.txt         # 必須パッケージ
├── .env                     # トークン, チャンネルID(作成の必要あり)
```

## 注意事項

- `CHANNEL_ID` は通知を送りたいチャンネルのIDを設定してください。
- 初回実行時に `events.json` が存在しない場合、自動で空のファイルが生成されます。

## トラブルシューティング

- 起動時にエラーが発生する場合、`.env` ファイルに正しいトークンとチャンネルIDが設定されていることを確認してください。
- `events.json` が保存されない場合は、ファイルの書き込み権限を確認してください。

## 貢献

バグ報告や機能追加のリクエストは、Issueとして提出してください。また、Pull Requestも歓迎します！