# Fonction pour mettre à jour les salons avec les prix et les tendances
async def update_channel_names():
    await bot.wait_until_ready()

    guild = bot.get_guild(1416403740721942551)  # Remplace avec l'ID de ton serveur
    if guild:
        prices = await fetch_price()
        
        for crypto, symbol in cryptos.items():
            channel_id = CHANNELS_IDS.get(symbol)
            if channel_id:
                channel = discord.utils.get(guild.voice_channels, id=channel_id)
                if channel:
                    price_raw = prices.get(crypto, {}).get("usd", "N/A")
                    change_percentage = prices.get(crypto, {}).get("usd_24h_change", 0)

                    try:
                        price = float(price_raw)
                    except (ValueError, TypeError):
                        print(f"❌ Prix invalide pour {crypto} : {price_raw}")
                        continue  # Skip si le prix est invalide

                    trend_icon, trend_color = get_trend_icon(change_percentage)

                    if crypto == "pepe":
                        formatted_price = f"{price:,.5f}".replace(",", " ").replace(".", ",")
                    else:
                        formatted_price = f"{price:,.2f}".replace(",", " ").replace(".", ",")

                    updated_name = f"{symbol} {formatted_price} {trend_icon}".replace("-", " ")

                    print(f"✅ Mise à jour du salon {channel.name} : {updated_name}")
                    await channel.edit(name=updated_name)
                else:
                    print(f"❌ Salon introuvable pour {symbol}")
            else:
                print(f"❌ ID de salon introuvable pour {symbol}")
    else:
        print("❌ Serveur introuvable")
