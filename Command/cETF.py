import datetime
import concurrent.futures
import threading
import time
import discord
import pytz
import requests
from lxml import html
from Utils.CheckNasdaqOpen import NasdaqOpenChecker as checker
from Utils.Log import Logger
from Utils.EmbedResponse import Response as er

ETFS = ['SOXL', 'SOXS', 'TQQQ', 'UPRO', 'LABU']

def scrape_stock_info(ticker):
    """Scrape stock information for a given ticker."""
    
    # Define URL based on ticker
    url = f"https://stockanalysis.com/stocks/{ticker}/" if ticker == 'NVDA' else f"https://stockanalysis.com/etf/{ticker}/"
    
    # Fetch content
    response = requests.get(url)
    response.raise_for_status()
    tree = html.fromstring(response.content)
    
    # Define XPaths
    xpaths = {
        'regMarket': '//*[@id="main"]/div[1]/div[2]/div/div[1]',
        'regChangePercent': '//*[@id="main"]/div[1]/div[2]/div/div[2]',
        'closeMarket': '//*[@id="main"]/div[1]/div[2]/div[2]/div[1]',
        'closeChangePercent': '//*[@id="main"]/div[1]/div[2]/div[2]/div[2]',
    }

    return process_scraped_data(tree, xpaths)

def process_scraped_data(tree, xpaths):
    """Process scraped data based on XPaths."""
    
    data = {}
    for field, xpath in xpaths.items():
        value = tree.xpath(xpath)[0].text_content().strip() if tree.xpath(xpath) else None
        
        # Processing change percentages for regular market
        if field == 'regChangePercent':
            regChange, regPercent = value.split()
            data['regSign'] = '+' if regChange.startswith('+') else '-' if regChange.startswith('-') else ''
            data['regChange'] = regChange.lstrip(data['regSign'])
            data['regPercent'] = regPercent.strip('()')
        
        # Processing change percentages for close market
        elif field == 'closeChangePercent':
            closeChange, closePercent = value.split() if value else ('N/A', 'N/A')
            data['closeSign'] = '+' if closeChange.startswith('+') else '-' if closeChange.startswith('-') else ''
            data['closeChange'] = closeChange.lstrip(data['closeSign'])
            data['closePercent'] = closePercent.strip('()')
        
        else:
            data[field] = value

    return data

def add_embed_field(embed, name, data, is_open):
    """Add field to the embed based on stock data."""
    
    if data.get('closeMarket'):
        sign = data['closeSign']
        current = data['closeMarket']
        change = data['closeChange']
        percent = data['closePercent']
    else:
        sign = data['regSign']
        current = data['regMarket']
        change = data['regChange']
        percent = data['regPercent']
    
    updown = get_updown_emoji(sign)
    embed.add_field(name=f'{name}', value=current, inline=True)
    embed.add_field(name='Change', value=change, inline=True)
    embed.add_field(name='Percent', value=f'{percent} {updown}', inline=True)

    return embed

def get_updown_emoji(sign):
    """Return the emoji based on sign."""
    return {
        '+': '<:yangbonghoro:1162456430360662018>',
        '-': '<:sale:1162457546532073623>',
        '': ''
    }.get(sign, '')

def fetch_and_add_to_embed(ticker, embed, is_open, embed_lock):
    """Function to fetch stock info and add to embed."""
    data = scrape_stock_info(ticker)
    with embed_lock:
        return add_embed_field(embed, ticker, data, is_open)

async def handle_specific_ticker(interaction, ticker, now_utc_aware, etfs_rbt, is_open):
    """Handle specific ticker request."""
    
    ticker = ticker.upper()
    if etfs_rbt.search_by_key(ticker):
        embed = create_specific_embed(ticker, now_utc_aware, is_open)
        await interaction.followup.send(embed=embed)
    else:
        error = er.error(f"유효한 ETF 종목 코드가 아닌 것 같습니다 : {ticker}")
        await interaction.followup.send(embed=error)

def create_etf_embed(now_utc_aware, open_close, is_open):
    """Create embed for all ETFs."""
    
    embed = discord.Embed(title='ETF', description=f'**Market : {open_close}**', color=discord.Color.dark_blue(), timestamp=now_utc_aware)
    
    # TEMP
    nvda_data = scrape_stock_info('NVDA')
    embed = add_embed_field(embed, 'NVDA', nvda_data, is_open)

    embed_lock = threading.Lock()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fetch_and_add_to_embed, etf, embed, is_open, embed_lock) for etf in ETFS]
        for future in concurrent.futures.as_completed(futures):
            try:
                embed = future.result()
            except Exception as e:
                Logger.error(f"Exception occurred: {e}")

    embed.set_footer(text="Data provided by Stock Analysis Website")
    return embed

def create_specific_embed(ticker, now_utc_aware, is_open):
    """Create embed for specific ticker."""
    
    embed = discord.Embed(title=ticker, color=discord.Color.dark_blue(), timestamp=now_utc_aware)
    data = scrape_stock_info(ticker)
    embed = add_embed_field(embed, ticker, data, is_open)
    embed.set_footer(text="Data provided by Stock Analysis Website")
    return embed

async def print_etfs(interaction, etfs_rbt, ticker):
    """Print ETF details to Discord."""

    if ticker is None:
        Logger.info(f"Received ETF command from {interaction.user.name}")
    else:
        Logger.info(f"Received ETF command for {ticker.upper()} from {interaction.user.name}")
    
    # Initialize and defer response
    await interaction.response.defer(ephemeral=False)
    
    # Get UTC time
    now_utc_aware = pytz.utc.localize(datetime.datetime.utcnow())
    is_open = checker.is_nasdaq_open()
    open_close = 'Open  :green_circle:' if is_open else 'Close  :red_circle:'

    if ticker is None:
        embed = create_etf_embed(now_utc_aware, open_close, is_open)
        await interaction.followup.send(embed=embed)
    else:
        await handle_specific_ticker(interaction, ticker, now_utc_aware, etfs_rbt, is_open)