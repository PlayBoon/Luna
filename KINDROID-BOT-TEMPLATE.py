import discord
import requests
import json
import time  # Für die Zeitmessung

TOKEN = "XXXXXXXX"  # Dein Discord Bot Token
API_KEY = "XXXXXXXX"  # Dein Kindroid API Key
AI_ID = "XXXXXXXX"  # Deine AI-ID von Kindroid

API_URL = "https://api.kindroid.ai/v1/send-message"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = discord.Client(intents=intents)

# Bot-Antwort-Limitierung
antwort_counter = {}  # Speichert, wie oft KIN_NAME auf Bots geantwortet hat
MAX_ANTWORTEN_PRO_STUNDE = 10
RESET_ZEIT = 3600  # Sekunden (1 Stunde)

@bot.event
async def on_ready():
    print(f"✅ KIN_NAME ist online als {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Eigene Nachrichten ignorieren

    # Antwort-Limit nur für andere Bots
    if message.author.bot:
        bot_id = message.author.id
        aktuelle_zeit = time.time()

        if bot_id not in antwort_counter:
            antwort_counter[bot_id] = {"count": 0, "start_time": aktuelle_zeit}

        if aktuelle_zeit - antwort_counter[bot_id]["start_time"] > RESET_ZEIT:
            antwort_counter[bot_id] = {"count": 0, "start_time": aktuelle_zeit}

        if antwort_counter[bot_id]["count"] >= MAX_ANTWORTEN_PRO_STUNDE:
            print(f"🚫 KIN_NAME hat das Antwortlimit für Bot {message.author} erreicht.")
            return

        antwort_counter[bot_id]["count"] += 1

    # Prüfen, ob KIN_NAME erwähnt wurde, der Name fällt oder es eine Antwort auf ihn ist
    bot_mentioned = bot.user in message.mentions
    is_reply_to_bot = (
        message.reference and
        message.reference.resolved and
        message.reference.resolved.author == bot.user
    )
    name_mentioned = (
        "KIN_NAME" in message.content.lower() or
        "KIN_NAME" in message.content.lower() or
        "KIN_NAME" in message.content.lower()
    )

    if not (bot_mentioned or is_reply_to_bot or name_mentioned):
        return

    # Autor-Name (nur Benutzername, kein Tag)
    user_name = message.author.name

    # Ursprüngliche Nachricht bereinigen
    user_message = message.content.replace(f"<@{bot.user.id}>", "").strip()

    # Erwähnungen ersetzen: <@123456789> → @Benutzername
    for user in message.mentions:
        user_message = user_message.replace(f"<@{user.id}>", f"@{user.name}")

    # Formatierte Nachricht an Kindroid
    formatted_message = f"Discord Message from {user_name}: {user_message}"

    async with message.channel.typing():
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        data = {
            "ai_id": AI_ID,
            "message": formatted_message
        }

        try:
            response = requests.post(API_URL, headers=headers, json=data)
            print("Status Code:", response.status_code)
            print("Antwort-Text:", response.text)

            if response.status_code != 200:
                await message.channel.send(
                    f"⚠️ Fehler bei der Antwort: {response.status_code} - {response.text}"
                )
                return

            bot_response = response.text
            await message.reply(bot_response, mention_author=False)

        except Exception as e:
            await message.channel.send(f"⚠️ Fehler: {e}")
            print(f"Fehler: {e}")

bot.run(TOKEN)
