import json
import discord
import datetime
import matplotlib

import yfinance as yf

import pandas_market_calendars as mcal
import pytz

from Utils.Log import Logger
from Utils.Pypp import Scraper
from Utils.EmbedResponse import Response as es
from Utils.CheckNasdaqOpen import NasdaqOpenChecker as checker

import time

matplotlib.use('Agg')

# Set style for the candlestick chart
binance_dark = {
    "base_mpl_style": "dark_background",
    "marketcolors": {
        "candle": {"up": "#3dc985", "down": "#ef4f60"},  
        "edge": {"up": "#3dc985", "down": "#ef4f60"},  
        "wick": {"up": "#3dc985", "down": "#ef4f60"},  
        "ohlc": {"up": "green", "down": "red"},
        "volume": {"up": "#247252", "down": "#82333f"},  
        "vcedge": {"up": "green", "down": "red"},  
        "vcdopcod": False,
        "alpha": 1,
    },
    "mavcolors": ("#ad7739", "#a63ab2", "#62b8ba"),
    "facecolor": "#1b1f24",
    "gridcolor": "#2c2e31",
    "gridstyle": "--",
    "y_on_right": False,
    "rc": {
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.edgecolor": "#474d56",
        "axes.titlecolor": "red",
        "figure.facecolor": "#161a1e",
        "figure.titlesize": "x-large",
        "figure.titleweight": "semibold",
    },
    "base_mpf_style": "binance-dark",
}

def is_nasdaq_stocks(rbt, ticker):
        
    # Check rbt.search_by_key(ticker) is empty
    if not rbt.search_by_key(ticker):
        Logger.debug(f"{ticker} is not NASDAQ stock")
        return False
    
    return True

def is_nasdaq_open():
    return checker.is_nasdaq_open()

def handle_equity(stock_info, data, isOpen, rbt):

    isnaq = is_nasdaq_stocks(rbt, stock_info['symbol'])

    # Create embed message with stock information
    embed = discord.Embed(title=f"{stock_info['longName']} / [{stock_info['symbol']}]",
                          url=f"https://finance.yahoo.com/quote/{stock_info['symbol']}",
                          timestamp=datetime.datetime.utcnow())
    
    # get percentage and price change from openprice and current price
    price_change = stock_info['currentPrice'] - stock_info['regularMarketPreviousClose']
    percent_change = (price_change / stock_info['regularMarketPreviousClose']) * 100
            
    if price_change > 0:
        embed.colour = discord.Colour.green()
        updown = '<:yangbonghoro:1162456430360662018>'
    elif price_change < 0:
        embed.colour = discord.Colour.red()
        updown = '<:sale:1162457546532073623>'
    else:
        embed.colour = discord.Colour.dark_blue()
        updown = ''

    # Current Price
    embed.add_field(name="**Current Price**", value=f"**{stock_info['currentPrice']:,.2f} {stock_info['currency']}** || {(price_change):,.2f} ({(percent_change):,.2f}%) {updown}"
                    if stock_info['currentPrice'] is not None else 'None',
                    inline=False)

    # Post-Market Price
    if not isOpen and isnaq:
        if float(data['marketChange']) > 0:
            embed.colour = discord.Colour.green()
            updown = '<:yangbonghoro:1162456430360662018>'
        elif float(data['marketChange']) < 0:
            embed.colour = discord.Colour.red()
            updown = '<:sale:1162457546532073623>'
        else:
            embed.colour = discord.Colour.dark_blue()
            updown = ''

        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name="**Post/Pre-Market Price**", value=f"**{data['marketPrice']} {stock_info['currency']}** || {data['marketChange']} {data['marketChangePercent']} {updown}"
                        if data is not None else 'None',
                        inline=True)

    # Market Cap / Trading Volume
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name="Market Cap", value=f"{stock_info['marketCap']:,} {stock_info['currency']}" if stock_info['marketCap'] is not None else 'None', inline=True)
    embed.add_field(name="Trading Volume", value=f"{stock_info['volume']:,}" if stock_info['volume'] is not None else 'None', inline=True)

    # 52Week High/Low
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name="52 Week High", value=f"{stock_info.get('fiftyTwoWeekHigh', 'None'):,.2f} {stock_info['currency']}", inline=True)
    embed.add_field(name="52 Week Low", value=f"{stock_info.get('fiftyTwoWeekLow', 'None'):,.2f} {stock_info['currency']}", inline=True)

    # 50Day/200Day Moving Average
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name="PE Ratio", value=f"{stock_info.get('trailingPE', 'None'):,.2f}" if stock_info.get('trailingPE') is not None else 'None', inline=True)
    embed.add_field(name="Forward PE Ratio", value=f"{stock_info.get('forwardPE', 'None'):,.2f}" if stock_info.get('forwardPE') is not None else 'None', inline=True)
    embed.add_field(name="EPS", value=f"{stock_info.get('trailingEps', 'None'):,.2f}" if stock_info.get('trailingEps') is not None else 'None', inline=True)

    embed.set_footer(text="Data provided by Yahoo! Finance API")

    return embed

def handle_etf(stock_info, data, isOpen):

    # Create embed message with stock information
    embed = discord.Embed(title=f"{stock_info['longName']} / [{stock_info['symbol']}]",
                          url=f"https://finance.yahoo.com/quote/{stock_info['symbol']}",
                          timestamp=datetime.datetime.utcnow())    
    
    if float(data['regularMarketChange']) > 0:
        embed.colour = discord.Colour.green()
        updown = '<:yangbonghoro:1162456430360662018>'
    elif float(data['regularMarketChange']) < 0:
        embed.colour = discord.Colour.red()
        updown = '<:sale:1162457546532073623>'
    else:
        embed.colour = discord.Colour.dark_blue()
        updown = ''

    #embed.set_thumbnail(url=stock_info['logo_url'])
    embed.add_field(name="**Regular Market Price**", value=f"**{data['regularMarketPrice']} {stock_info['currency']}** || {data['regularMarketChange']} {data['regularMarketChangePercent']} {updown}"
                    if data['regularMarketPrice'] is not None else 'None',
                    inline=False)

    if not isOpen:
        if float(data['marketChange']) > 0:
            embed.colour = discord.Colour.green()
            updown = '<:yangbonghoro:1162456430360662018>'
        elif float(data['marketChange']) < 0:
            embed.colour = discord.Colour.red()
            updown = '<:sale:1162457546532073623>'
        else:
            embed.colour = discord.Colour.dark_blue()
            updown = ''

        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name="**Post/Pre-Market Price**", value=f"**{data['marketPrice']} {stock_info['currency']}** || {data['marketChange']} {data['marketChangePercent']} {updown}"
                        if data is not None else 'None',
                        inline=True)

    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name="Net Assets", value=f"{stock_info['totalAssets']:,} {stock_info['currency']}" if stock_info['totalAssets'] is not None else 'None', inline=True)
    embed.add_field(name="Trading Volume", value=f"{stock_info['volume']:,}" if stock_info['volume'] is not None else 'None', inline=True)

    # 52Week High/Low
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name="52 Week High", value=f"{stock_info.get('fiftyTwoWeekHigh', 'None'):,.2f} {stock_info['currency']}", inline=True)
    embed.add_field(name="52 Week Low", value=f"{stock_info.get('fiftyTwoWeekLow', 'None'):,.2f} {stock_info['currency']}", inline=True)

    # Bid / Ask
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name="Bid", value=f"{stock_info['bid']:,.2f} x {stock_info['bidSize']}" if stock_info['bid'] is not None else 'None', inline=True)
    embed.add_field(name="Ask", value=f"{stock_info['ask']:,.2f} x {stock_info['askSize']}" if stock_info['ask'] is not None else 'None', inline=True)

    # Yield / YTD Return
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name="Yield", value=f"{(stock_info['yield'] * 100):,.2f}%" if stock_info['yield'] is not None else 'None', inline=True)
    embed.add_field(name="YTD Return", value=f"{stock_info['ytdReturn']:,.2f}" if stock_info['ytdReturn'] is not None else 'None', inline=True)
    embed.add_field(name="Beta 3Y", value=f"{stock_info['beta3Year']:,.2f}" if stock_info['beta3Year'] is not None else 'None', inline=True)

    embed.set_footer(text="Data provided by Yahoo! Finance API")

    return embed

async def executeStock(interaction, ticker, rbt, ppWsEndpoint):

    start_total = time.time()
       
    await interaction.response.defer(ephemeral=False)

    # Set default value
    if ticker is None:
        ticker = 'NVDA'
    else:
        ticker = ticker.upper()
    
    # Get stock information from Yahoo Finance API
    start_ticker = time.time()
    try:
        stock_info = yf.Ticker(ticker).info
        with open('stock_info.json', 'w') as f:
            json.dump(stock_info, f, indent=4)
    except Exception as e:
        Logger.error(f"An error occurred while getting ticker: {ticker}")
        err_ebd = es.error(f"정보를 가져오지 못했습니다: {ticker}\n티커를 잘못 입력했거나 API 서버가 응답하지 않습니다.")
        await interaction.followup.send(embed = err_ebd, ephemeral=False)
        return
    end_ticker = time.time()
    Logger.debug(f"Time taken to get ticker: {end_ticker - start_ticker} seconds")

    # Check if the market is open
    start_isOpen = time.time()
    isOpen = is_nasdaq_open()
    Logger.debug(f"isOpen: {isOpen}")
    end_isOpen = time.time()
    Logger.debug(f"Time taken to check isOpen: {end_isOpen - start_isOpen} seconds")
    
    start_first_log = time.time()
    Logger.info(f'{interaction.user.display_name} Executing stock command with ticker: {ticker}')
    end_first_log = time.time()
    Logger.debug(f"Time taken to first log: {end_first_log - start_first_log} seconds")    
    
    data = {}    
    if stock_info['quoteType'] == 'ETF' or (is_nasdaq_stocks(rbt, ticker) and not isOpen):
        start_scrape = time.time()

        pp = Scraper()
        await pp.init_browser(ppWsEndpoint)
        data = await pp.scrape(ticker, stock_info, isOpen)

        end_scrape = time.time()
        Logger.debug(f"Time taken to scrape: {end_scrape - start_scrape} seconds")

    #save stock_info in json format
    start_save = time.time()
    with open('stock_info.json', 'w') as f:
        json.dump(stock_info, f, indent=4)
    end_save = time.time()
    Logger.debug(f"Time taken to save: {end_save - start_save} seconds")

    # Check if the stock is an Equity or ETF
    if stock_info['quoteType'] == 'EQUITY':
        stock_type = 'Equity'

    elif stock_info['quoteType'] == 'ETF':
        stock_type = 'ETF'
    else:
        stock_type = 'Unknown'

    # Handle the stock based on its type
    start_branch = time.time()
    if stock_type == 'Equity':
        embed = handle_equity(stock_info, data, isOpen, rbt)
    elif stock_type == 'ETF':
        embed = handle_etf(stock_info, data, isOpen)
    else:
        embed = discord.Embed(title=f"{stock_info['longName']} / [{stock_info['symbol']}]", 
                              url=f"https://finance.yahoo.com/quote/{stock_info['symbol']}", 
                              colour=discord.Colour.dark_blue(), 
                              timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Error", value="Unknown stock type", inline=False)

    end_branch = time.time()
    Logger.debug(f"Time taken to branch: {end_branch - start_branch} seconds")

    end_total = time.time()
    Logger.debug(f"Total time taken: {end_total - start_total} seconds")
    await interaction.followup.send(embed=embed)

    return