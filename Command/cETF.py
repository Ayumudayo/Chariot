import datetime
import time
import discord
import pytz

from Utils.CheckNasdaqOpen import NasdaqOpenChecker as checker
from Utils.Pypp import Scraper
from Utils.Log import Logger

ETFS = [
    'SOXL',
    'SOXS',
    'TQQQ',
    'UPRO',
    'LABU',
    'BNKU'
]

STOCK_INFO = {
    'quoteType': 'ETF'
}

def add_embed_field(embed, name, data, is_open):
    # Remove parentheses from name
    name = name.replace('(', '').replace(')', '')

    if is_open:
        updown = '<:yangbonghoro:1162456430360662018>' if data.get('regularMarketChange') and float(data['regularMarketChange']) > 0 else '<:sale:1162457546532073623>' if data.get('regularMarketChange') and float(data['regularMarketChange']) < 0 else ''
        current = data.get('regularMarketPrice')
        change = data.get('regularMarketChange')
        percent = data.get('regularMarketChangePercent').replace('(', '').replace(')', '')
    else:
        updown = '<:yangbonghoro:1162456430360662018>' if data.get('marketChange') and float(data['marketChange']) > 0 else '<:sale:1162457546532073623>' if data.get('marketChange') and float(data['marketChange']) < 0 else ''
        current = data.get('marketPrice')
        change = data.get('marketChange')
        percent = data.get('marketChangePercent').replace('(', '').replace(')', '')
    
    embed.add_field(name=f'{name}', value=current, inline=True)
    embed.add_field(name='Change', value=change, inline=True)
    embed.add_field(name='Percent', value=f'{percent} {updown}', inline=True)

    return embed

async def print_etfs(interaction, pp_ws_endpoint):
    await interaction.response.defer(ephemeral=False)

    start = time.time()

    is_open = checker.is_nasdaq_open()
    
    # Get the current time in UTC
    now_utc = datetime.datetime.utcnow()
    now_utc_aware = pytz.utc.localize(now_utc)

    embed = discord.Embed(title='ETF', color=discord.Color.dark_blue(), timestamp=now_utc_aware)
    for etf in ETFS:        
        Logger.info(f"Processing {etf}")
        scraper = Scraper()
        await scraper.init_browser(pp_ws_endpoint)
        data = await scraper.scrape(etf, STOCK_INFO, is_open)
        print(data)
        embed = add_embed_field(embed, etf, data, is_open)

    Logger.debug(f"TIME: {pytz.timezone('Asia/Tokyo').localize(datetime.datetime.utcnow())}")
    Logger.debug(f"TIME: {datetime.datetime.now().timestamp()}")

    end = time.time()
    Logger.info(f"Time taken to scrape: {end - start} seconds")
    await interaction.followup.send(embed=embed)
