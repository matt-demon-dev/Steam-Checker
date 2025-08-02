import os
import discord
import requests
from discord.ext import commands, tasks
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

STEAM_URL = "https://store.steampowered.com"

def is_steam_up():
    """Check if Steam store is reachable."""
    try:
        response = requests.head(STEAM_URL, timeout=5)
        return response.status_code < 400
    except requests.RequestException:
        return False

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")
    update_channel_name.start()

@tasks.loop(seconds=60)
async def update_channel_name():
    """Update channel name based on Steam status."""
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        status_up = is_steam_up()
        new_name = "✅ Steam Online" if status_up else "❌ Steam Down"
        if channel.name != new_name:
            try:
                await channel.edit(name=new_name)
                print(f"Channel updated to: {new_name}")
            except discord.Forbidden:
                print("❌ Missing Manage Channels permission.")
            except discord.HTTPException as e:
                print(f"Error updating channel name: {e}")

@bot.tree.command(name="steamstatus", description="Check if Steam is up or down")
async def steamstatus(interaction: discord.Interaction):
    status_up = is_steam_up()
    message = "✅ Steam is ONLINE" if status_up else "❌ Steam is DOWN"
    await interaction.response.send_message(message)

bot.run(TOKEN)
