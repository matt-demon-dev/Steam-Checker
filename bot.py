import os
import asyncio
import discord
from discord.ext import tasks
import requests
from dotenv import load_dotenv, find_dotenv

# ——— Load .env ———
print("🔍 CWD:", os.getcwd())
env_path = find_dotenv()
if not env_path:
    print("⚠️  .env file not found!")
else:
    print(f"📄 Found .env at: {env_path}")
load_dotenv(env_path, verbose=True)

# ——— Config ———
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
try:
    CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
except (TypeError, ValueError):
    print("⚠️  DISCORD_CHANNEL_ID is missing or not an integer!")
    CHANNEL_ID = None

if not DISCORD_TOKEN or not CHANNEL_ID:
    print("❌ Missing DISCORD_TOKEN or DISCORD_CHANNEL_ID!")
    exit(1)
else:
    print("✅ Environment variables loaded.")

# ——— Bot Setup ———
intents = discord.Intents(guilds=True)
bot = discord.Client(intents=intents)

# ——— New Steam Status Checker ———
def get_steam_status():
    """
    Queries steamstat.us for live Steam API status.
    Returns: "online", "offline", or "error"
    """
    try:
        r = requests.get("https://steamstat.us/api/v2/status.json", timeout=10)
        r.raise_for_status()
        data = r.json()
        # steamstat.us categorizes under "services" → "Steam API"
        svc = data.get("services", {}).get("Steam API", {})
        status = svc.get("status", "").lower()  # usually "online" or "offline"
        if status == "online":
            return "online"
        elif status == "offline":
            return "offline"
        else:
            return "error"
    except Exception as e:
        print("Error fetching Steam status:", e)
        return "error"

# ——— Events & Loop ———
@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user} (ID {bot.user.id})")
    # small delay in case we need it
    await asyncio.sleep(2)
    update_channel_name.start()

@tasks.loop(minutes=5)
async def update_channel_name():
    try:
        channel = await bot.fetch_channel(CHANNEL_ID)
    except discord.NotFound:
        print(f"⚠️  Channel {CHANNEL_ID} not found.")
        return
    except Exception as e:
        print("❌ Error fetching channel:", e)
        return

    status = get_steam_status()
    if   status == "online":  new_name = "Steam is Online ✅"
    elif status == "offline": new_name = "Steam is Offline 🔴"
    else:                      new_name = "Steam Status Unknown ❓"

    if channel.name != new_name:
        try:
            await channel.edit(name=new_name)
            print(f"🔄 Updated channel name to “{new_name}”")
        except discord.Forbidden:
            print("❌ Missing Manage Channels permission.")
        except Exception as e:
            print("❌ Error editing channel name:", e)

# ——— Run ———
bot.run(DISCORD_TOKEN)

