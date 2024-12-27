import discord
import datetime
from dotenv import load_dotenv
import os
from discord.ext import tasks
from datetime import time, timezone, timedelta
from create_table import create_table
from app.crud import (
    create_event,
    get_unfinished_events,
    update_event_finished,
    delete_event,
)

# .env ファイルを読み込む
load_dotenv()

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID"))

JST = timezone(timedelta(hours=+9), "JST")

# 配信時刻をリストで設定
TIMES = [time(hour=7, tzinfo=JST)]


# トークンを読み込む関数
def load_token():
    return os.getenv("DISCORD_TOKEN")


# 残り日数を計算する関数
def get_countdown(target_date: datetime.date) -> int:
    today = datetime.datetime.now()
    # 現在日時を7時に設定
    now_7 = today.replace(hour=7, minute=0, second=0, microsecond=0)
    # ターゲット日時を7時に設定
    target_date_7 = datetime.datetime.combine(target_date, datetime.time(7, 0, 0))
    delta = target_date_7 - now_7
    return delta.days


# Discord Botの設定
intents = discord.Intents.default()
intents.message_content = True  # メッセージの内容を取得できるようにする
client = discord.Client(intents=intents)


# 毎日午前7時に実行するタスク
@tasks.loop(time=TIMES)  # 毎日7時に実行
async def send_event_notifications():
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        result = get_unfinished_events()
        if result == "error":
            await channel.send("エラーが発生しました。")
        elif result == []:
            await channel.send("現在通知するイベントはありません。")
        else:
            for row in result:
                event_id = row.id
                event_name = row.event_name
                event_date = row.event_date
                days_left = get_countdown(event_date)
                # イベント日を過ぎた場合は終了フラグを立てる
                if days_left < 0:
                    update_event_finished(event_id)
                else:
                    await channel.send(f"{event_name}まであと{days_left}日")
    else:
        print(f"Error: チャンネルID {CHANNEL_ID} が見つかりませんでした。")


# 起動時の処理
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    # チャンネルIDを指定してメッセージを送信
    channel = client.get_channel(
        ADMIN_CHANNEL_ID
    )  # YOUR_CHANNEL_IDに実際のチャンネルIDを設定
    if channel:
        await channel.send("日付カウントダウンBotが起動しました。")
        send_event_notifications.start()
    else:
        print(f"Error: チャンネルID {CHANNEL_ID} が見つかりませんでした。")


# メッセージ受信時の処理
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # イベント追加コマンド
    if message.content.startswith("!add_event"):
        parts = message.content.split(" ", 2)
        if len(parts) < 3:
            await message.channel.send("Usage: !add_event <event_name> <yyyy-mm-dd>")
            return
        event_name = parts[1]
        event_date = parts[2]
        try:
            # 日付形式を検証（時間は不要）
            event_date = datetime.datetime.strptime(event_date, "%Y-%m-%d")
            result = create_event(event_name, event_date)
            if result == "error":
                await message.channel.send("エラーが発生しました。")
            else:
                await message.channel.send(f"イベント「{event_name}」を追加しました。")
        except ValueError:
            await message.channel.send("日付の形式が正しくありません。")

    # イベント削除コマンド
    if message.content.startswith("!remove_event"):
        parts = message.content.split(" ", 1)
        if len(parts) < 2:
            await message.channel.send("Usage: !remove_event <event_id>")
            return
        event_id = parts[1]
        result = delete_event(event_id)
        if result == "error":
            await message.channel.send("エラーが発生しました。")
        elif result:
            await message.channel.send(f"イベントID「{event_id}」を削除しました。")
        else:
            await message.channel.send(f"イベントID「{event_id}」は存在しません。")

    # イベントリスト表示コマンド
    if message.content.startswith("!list_events"):
        result = get_unfinished_events()
        if result == "error":
            await message.channel.send("エラーが発生しました。")
        else:
            if result == []:
                await message.channel.send("現在通知するイベントはありません。")
            else:
                for row in result:
                    event_id = row.id
                    event_name = row.event_name
                    event_date = row.event_date
                    await message.channel.send(
                        f"ID: {event_id}, イベント名: {event_name}, 日付: {event_date}"
                    )
    # カウントダウン表示コマンド
    if message.content.startswith("!countdown"):
        result = get_unfinished_events()
        if result == "error":
            await message.channel.send("エラーが発生しました。")
        else:
            if result == []:
                await message.channel.send("現在通知するイベントはありません。")
            else:
                for row in result:
                    event_id = row.id
                    event_name = row.event_name
                    event_date = row.event_date
                    days_left = get_countdown(event_date)
                    await message.channel.send(f"{event_name}まであと{days_left}日")


def main():
    # トークンを読み込んでBotを起動
    TOKEN = load_token()
    client.run(TOKEN)


if __name__ == "__main__":
    if not os.path.exists("database.db"):
        create_table()
    main()
