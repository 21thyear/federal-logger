import nextcord
import mysql.connector
from nextcord.ext import commands
from datetime import datetime

from config import BOT_TOKEN, BOT_ACTIVITY_TEXT

mydb = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
)
mycursor = mydb.cursor()

intents = nextcord.Intents.all()
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)
now = datetime.now()

def format_log_entry(action, user, details):
    return f"{action}: {user}/{user.id} {details} в {now.strftime('%d/%m/%Y, %H:%M:%S')}."

async def send_log_message(channel_id: int, log_text: str):
    channel = client.get_channel(channel_id)
    await channel.send(log_text)

@client.event
async def on_ready():
    print("Logger Bot successfully started!")
    activity = nextcord.Activity(name=BOT_ACTIVITY_TEXT, type=nextcord.ActivityType.watching)
    await client.change_presence(activity=activity)

@client.event
async def log_event(channel_id: int, action: str, user: nextcord.User, details: str):
    log_text = format_log_entry(action, user, details)
    await send_log_message(channel_id, log_text)
    await upload_new_logs(user.id, log_text)

@client.event
async def on_message_edit(before, after):
    if before.content != after.content:
        await log_event(-639163163895660564, "Редактирование сообщения", before.author, f"Текст: ДО: {before.content} ПОСЛЕ: {after.content} В канале: {before.channel}")

# Остальные события (on_message_delete, on_member_remove, и так далее) обрабатываются аналогично

@client.event
async def on_voice_state_update(member, before, after):
    if member.voice and member.voice.channel:
        details = f"зашел в голосовой канал {member.voice.channel}."
    else:
        details = f"вышел с голосового канала {before.channel.name}."
    
    await log_event(-639163184896409600, "Изменение голосового состояния", member, details)

# Остальные события (on_guild_channel_create, on_guild_channel_delete, и так далее) обрабатываются аналогично

async def upload_new_logs(id, text):
    log_date = now.strftime('%d/%m/%Y, %H:%M:%S')
    
    mycursor.execute(f"INSERT INTO logs_discord (date, text) VALUES ('{log_date}', '{text}')")
    mydb.commit()
    
    if id:
        mycursor.execute(f"UPDATE accounts SET `online-date` = '{log_date}' WHERE discord_id = '{id}'")
        mydb.commit()

client.run(BOT_TOKEN)
