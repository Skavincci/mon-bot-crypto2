import logging
import os
import aiohttp
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNELS_IDS = {
    "BTC": int(os.getenv("CHANNELS_ID_BTC")),
    "ETH": int(os.getenv("CHANNELS_ID_ETH")),
    "SOL": int(os.getenv("CHANNELS_ID_SOL")),
    "XRP": int(os.getenv("CHANNELS_ID_XRP")),
    "DOGE": int(os.getenv("CHANNELS_ID_DOGE")),
    "PEPE": int(os.getenv("CHANNELS_ID_PEPE"))
}
UPDATE_SECONDS = int(os.getenv("UPDATE_SECONDS") or 30)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Liste des cryptos et leurs symboles
cryptos = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "ripple": "XRP",
    "dogecoin": "DOGE",
    "pepe": "PEPE"
}

# Fonction pour récupérer les prix des cryptos
async def fetch_price():
    async with aiohttp.ClientSession() as session:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,ripple,dogecoin,pepe&vs_currencies=usd,eur&include_24hr_change=true"
        async with session.get(url) as resp:
            return await resp.json()

# Fonction pour générer l'icône et la flèche de tendance
def get_trend_icon(change_percentage):
    # Si la variation est positive (haussier)
    if change_percentage > 0:
        return "🟢↗️", "green"  # Flèche montante
    # Si la variation est négative (baissier)
    elif change_percentage < 0:
        return "🔴↘️", "red"  # Flèche descendante
    # Si la variation est nulle (stable)
    else:
        return "⚪️➡️", "white"  # Flèche droite (stable)

# Fonction pour mettre à jour les salons avec les prix et les tendances
async def update_channel_names():
    await bot.wait_until_ready()

    # Récupérer le serveur
    guild = bot.get_guild(1416403740721942551)  # Remplace avec l'ID de ton serveur
    if guild:
        prices = await fetch_price()
        
        # Pour chaque crypto dans la liste, mettre à jour le salon
        for crypto, symbol in cryptos.items():
            channel_id = CHANNELS_IDS.get(symbol)  # Récupérer l'ID du salon à partir du dict
            if channel_id:
                # Chercher le salon vocal par son ID
                channel = discord.utils.get(guild.voice_channels, id=channel_id)  # Cherche le salon vocal par son ID
                if channel:
                    price = prices.get(crypto, {}).get("usd", "N/A")
                    change_percentage = prices.get(crypto, {}).get("usd_24h_change", 0)

                    trend_icon, trend_color = get_trend_icon(change_percentage)

                    # Formatage spécifique pour Pepe (5 décimales)
                    if crypto == "pepe":
                        formatted_price = f"{price:,.5f}".replace(",", " ").replace(".", ",")
                    else:
                        # Formatage standard pour les autres cryptos (2 décimales)
                        formatted_price = f"{price:,.2f}".replace(",", " ").replace(".", ",")

                    # Remplacer les tirets par des espaces
                    updated_name = f"{symbol} {formatted_price} {trend_icon}".replace("-", " ")

                    print(f"✅ Mise à jour du salon {channel.name} : {updated_name}")  # Log pour vérifier ce qui est mis à jour
                    
                    # Mettre à jour le nom du salon vocal
                    await channel.edit(name=updated_name)
                else:
                    print(f"❌ Salon introuvable pour {symbol}")
            else:
                print(f"❌ ID de salon introuvable pour {symbol}")
    else:
        print("❌ Serveur introuvable")

@tasks.loop(seconds=UPDATE_SECONDS)
async def update_prices():
    await update_channel_names()

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")
    update_prices.start()

bot.run(TOKEN)
