import discord
import datetime
from Utils.Currency import Exchange as ex
from Utils.Log import Logger
from Utils.EmbedResponse import Response as rs

async def executeTk(interaction, twd):

    Logger.info(f"{interaction.user.display_name} request tk().")

    result = ex.exchCur('twd', twd, 'krw')

    if(result != 0):
        twd = format(twd, ',')

        Logger.info(f"NT$ {twd} to KRW / {result}")
        await interaction.response.send_message(f"NT$ {twd} to KRW\n{result}", ephemeral=True)

async def executeExchange(interaction, src, amount, dst):

    Logger.info(f"{interaction.user.display_name} request exchange().")

    if (dst == None):
        dst = 'krw'

    result = ex.exchCur(src, amount, dst)

    if(result != 0):
        src = src.upper()
        dst = dst.upper()

        amount = format(amount, ',')

        Logger.info(f"{src} {amount} to {dst} / {result}")
        res = rs.general(f"{src} {amount} to {dst}", f'{result} {dst}')
        await interaction.response.send_message(embed=res, ephemeral=True)
    else:
        await interaction.response.send_message("처리 중 오류가 발생했습니다. USD, KRW, JPY와 같은 제대로 된 통화코드를 입력했나요?", ephemeral=True)


async def execetueRateTable(interaction, src, amount):

    await interaction.response.defer()

    # Set default values if not provided
    src = src.lower() if src else 'usd'
    amount = amount if amount else 1

    try:
        # Get exchange rates
        result = ex.exchCurList(src, amount)
        if result is None:
            raise ValueError("No exchange rates found for the given source and amount.")
        exchange_rates = list(result.values())

        # Create an embed message with the exchange rates
        embed = discord.Embed(title="**Exchange Rate**", colour=discord.Colour.dark_green())
        embed.description = f'Exchange rates for **[ {amount} {src.upper()} ]**'
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1138398345065414657/1138816034049105940/gil.png")
        embed.add_field(name="", value="", inline=False)  # Padding

        # Add fields for each currency
        currencies = ['USD', 'KRW', 'JPY', 'EUR', 'GBP', 'CNY', 'TRY', 'ARS', 'TWD', 'MNT']
        flags = [':flag_us:', ':flag_kr:', ':flag_jp:', ':flag_eu:', ':flag_gb:', ':flag_cn:', ':flag_tr:', ':flag_ar:', ':flag_tw:', ':flag_mn:']
        for flag, currency, rate in zip(flags, currencies, exchange_rates):
            embed.add_field(name=f'{flag} {currency}', value=rate, inline=True)

        embed.add_field(name="", value="", inline=False)  # Padding
        embed.add_field(name="", value="Powered by [fawazahmed0/currency-api](https://github.com/fawazahmed0/currency-api)", inline=False)
        embed.set_footer(text=f'{datetime.datetime.now().strftime("%Y-%m-%d")} 기준')

        # Send embed message
        await interaction.followup.send(embed=embed)

    except:
        Logger.error("Something went wrong while processing ratetable()")
        embed = rs.error("처리 중 오류가 발생했습니다. USD, KRW, JPY와 같은 제대로 된 통화코드를 입력했는지 확인하세요.")
        await interaction.followup.send(embed=embed, ephemeral=True)