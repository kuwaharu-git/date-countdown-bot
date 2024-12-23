import discord
import json
import datetime
from dotenv import load_dotenv
import os
from discord.ext import tasks
from datetime import time, timezone, timedelta

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


# イベント情報の読み込み
def load_events():
    try:
        with open("events.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}  # ファイルがない場合は空の辞書を返す


# イベント情報を保存する関数
def save_events(events):
    with open("events.json", "w") as file:
        json.dump(events, file, indent=4)


# 残り日数を計算する関数
def get_countdown(target_date: datetime.datetime):
    today = datetime.datetime.now()
    now_7 = today.replace(hour=7, minute=0, second=0, microsecond=0)
    delta = target_date - now_7
    return delta.days


# イベントの追加
def add_event(event_name, event_date):
    events = load_events()
    event_id = f"event{len(events) + 1}"

    # 時間を7時に固定
    event_date = datetime.datetime.strptime(event_date, "%Y-%m-%d")
    # 毎朝7時に通知するため、時間を7時に設定(配信時間を変更する場合はここを変更)
    event_date = event_date.replace(hour=7, minute=0, second=0, microsecond=0)

    events[event_id] = {
        "name": event_name,
        "date": event_date.strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_events(events)


# イベントの削除
def remove_event(event_id):
    events = load_events()
    if event_id in events:
        del events[event_id]
        save_events(events)
    else:
        return False
    return True


# イベントリストを表示
def list_events():
    events = load_events()
    if not events:
        return "現在登録されているイベントはありません。"

    event_list = "登録されたイベント:\n"
    for event_id, event in events.items():
        event_name = event["name"]
        event_date = datetime.datetime.strptime(event["date"], "%Y-%m-%d %H:%M:%S")
        event_list += f"{event_id}: {event_name} - {event_date.strftime('%Y-%m-%d')}\n"
    return event_list


# Discord Botの設定
intents = discord.Intents.default()
intents.message_content = True  # メッセージの内容を取得できるようにする
client = discord.Client(intents=intents)


# 毎日午前7時に実行するタスク
@tasks.loop(time=TIMES)  # 毎日7時に実行
async def send_event_notifications():
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        events = load_events()
        if not events:
            await channel.send("現在通知するイベントはありません。")
        else:
            for event_id, event in events.items():
                event_name = event["name"]
                event_date = datetime.datetime.strptime(
                    event["date"], "%Y-%m-%d %H:%M:%S"
                )
                days_left = get_countdown(event_date)
                await channel.send(f"{event_name}まであと{days_left}日")
    else:
        print(f"Error: チャンネルID {CHANNEL_ID} が見つかりませんでした。")


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
            datetime.datetime.strptime(event_date, "%Y-%m-%d")
            add_event(event_name, event_date)
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
        if remove_event(event_id):
            await message.channel.send(f"イベントID「{event_id}」を削除しました。")
        else:
            await message.channel.send(f"イベントID「{event_id}」は存在しません。")

    # イベントリスト表示コマンド
    if message.content.startswith("!list_events"):
        event_list = list_events()
        await message.channel.send(event_list)
    # カウントダウン表示コマンド
    if message.content.startswith("!countdown"):
        events = load_events()
        for event_id, event in events.items():
            event_name = event["name"]
            event_date = datetime.datetime.strptime(event["date"], "%Y-%m-%d %H:%M:%S")
            await message.channel.send(
                f"{event_name}まであと{get_countdown(event_date)}日"
            )


# トークンを読み込んでBotを起動
TOKEN = load_token()
client.run(TOKEN)
