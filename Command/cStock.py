import json
import discord
import datetime
import io
import matplotlib

import yfinance as yf
import mplfinance as mpf
import matplotlib.pyplot as plt

import pandas_market_calendars as mcal
import pytz

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Utils.Log import Logger
from Utils.nasdaqRtb import RedBlackTree

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

rbt = RedBlackTree()
csvPath = "./Data/Stock/nasdaq_screener.csv"
jsonPath = "./Data/Stock/rbt.json"

# Function to create Red-Black Tree from CSV file and save it to a JSON file
def create_rbt_from_csv_and_save(rbtree, csvPath, jsonPath):
    rbtree.insert_from_csv(csvPath)
    rbtree.save_to_json(jsonPath)

def check_file_exist():
    try:
        with open(jsonPath, "r") as json_file:
            Logger.debug("rbt.json exist")
            return True
    except FileNotFoundError:
        Logger.debug("rbt.json not exist")
        return False

def is_nasdaq_stocks(ticker):
        
    # Check rbt.search_by_key(ticker) is empty
    if not rbt.search_by_key(ticker):
        Logger.debug(f"{ticker} is not NASDAQ stock")
        return False
    
    return True

def is_nasdaq_open():
    # Get the NASDAQ market calendar
    nasdaq = mcal.get_calendar('NASDAQ')

    # Get the current date and time in Eastern Time (since NASDAQ operates in ET)
    now = datetime.datetime.now(pytz.timezone('US/Eastern'))

    # Get today's market schedule
    schedule = nasdaq.schedule(start_date=now.date(), end_date=now.date())

    # Check if the schedule is empty (i.e., the market is closed today)
    if schedule.empty:
        return False

    # Check if the current time is within today's market open hours
    return schedule.iloc[0].market_open <= now <= schedule.iloc[0].market_close

def handle_equity(stock_info, data, isOpen):

    isnaq = is_nasdaq_stocks(stock_info['symbol'])

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
        if float(data['postMarketChange']) > 0:
            embed.colour = discord.Colour.green()
            updown = '<:yangbonghoro:1162456430360662018>'
        elif float(data['postMarketChange']) < 0:
            embed.colour = discord.Colour.red()
            updown = '<:sale:1162457546532073623>'
        else:
            embed.colour = discord.Colour.dark_blue()
            updown = ''

        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name="**Post-Market Price**", value=f"**{data['postMarketPrice']} {stock_info['currency']}** || {data['postMarketChange']} {data['postMarketChangePercent']} {updown}"
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

    # Dividend Yield
    # Convert exDividendDate timestamp to readable date format
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name="Dividend Yield", value=f"{stock_info.get('dividendYield', 'None'):,.2f}%" if stock_info.get('dividendYield') is not None else 'None', inline=True)
    ex_dividend_date = datetime.datetime.fromtimestamp(stock_info['exDividendDate']).strftime('%Y-%m-%d' if stock_info['exDividendDate'] is not None else 'None')
    embed.add_field(name="Ex-Dividend Date", value=ex_dividend_date if ex_dividend_date is not None else 'None', inline=True)

    # 60Day Graph
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name="60 Day Graph", value=" ", inline=False)

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
        if float(data['postMarketChange']) > 0:
            embed.colour = discord.Colour.green()
            updown = '<:yangbonghoro:1162456430360662018>'
        elif float(data['postMarketChange']) < 0:
            embed.colour = discord.Colour.red()
            updown = '<:sale:1162457546532073623>'
        else:
            embed.colour = discord.Colour.dark_blue()
            updown = ''

        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name="**Post-Market Price**", value=f"**{data['postMarketPrice']} {stock_info['currency']}** || {data['postMarketChange']} {data['postMarketChangePercent']} {updown}"
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

    # 60Day Graph
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name="60 Day Graph", value=" ", inline=False)

    embed.set_footer(text="Data provided by Yahoo! Finance API")

    return embed
    

async def executeStock(interaction, ticker, driver):
       
    await interaction.response.defer(ephemeral=False)

    # Set default value
    if ticker is None:
        ticker = 'NVDA'
    else:
        ticker = ticker.upper()

    if check_file_exist():
        rbt.load_from_json(jsonPath)
    else:
        create_rbt_from_csv_and_save(rbt, csvPath, jsonPath)
    
    # Get stock information from Yahoo Finance API
    stock_info = yf.Ticker(ticker).info

    # Check if the market is open
    isOpen = is_nasdaq_open()
        
    Logger.info(f'{interaction.user.display_name} Executing stock command with ticker: {ticker}')    

    # Initialize a dictionary to store the scraped data
    data = {}    
    driver.get(f"https://finance.yahoo.com/quote/{ticker}")

    # Define the XPaths for the elements both in regular and post market
    xpaths = {
        'regularMarketPrice': f'//fin-streamer[@data-field="regularMarketPrice" and @data-symbol="{ticker.upper()}"]' if stock_info['quoteType'] == 'ETF' else None,
        'regularMarketChange': f'//fin-streamer[@data-field="regularMarketChange" and @data-symbol="{ticker.upper()}"]/span' if stock_info['quoteType'] == 'ETF' else None,
        'regularMarketChangePercent': f'//fin-streamer[@data-field="regularMarketChangePercent" and @data-symbol="{ticker.upper()}"]/span' if stock_info['quoteType'] == 'ETF' else None,
        'postMarketPrice': '//fin-streamer[@data-field="postMarketPrice"]' if not isOpen else None,
        'postMarketChange': '//fin-streamer[@data-field="postMarketChange"]/span' if not isOpen else None,
        'postMarketChangePercent': '//fin-streamer[@data-field="postMarketChangePercent"]/span' if not isOpen else None
    }

    # Remove None values from the dictionary
    xpaths = {k: v for k, v in xpaths.items() if v is not None}    

    if stock_info['quoteType'] == 'ETF' or is_nasdaq_stocks(ticker):
    # Loop over the XPaths and scrape the data
        for field, xpath in xpaths.items():
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, xpath))
                )
                data[field] = element.text.strip()
            except Exception as e:
                Logger.error(f"Element {field} not found:", e)
    
    #save stock_info in json format
    # with open('stock_full_info.json', 'w') as f:
    #     json.dump(stock.financials, f, indent=4)

    #save stock_info in json format
    with open('stock_info.json', 'w') as f:
        json.dump(stock_info, f, indent=4)

    # Check if the stock is an Equity or ETF
    if stock_info['quoteType'] == 'EQUITY':
        stock_type = 'Equity'

    elif stock_info['quoteType'] == 'ETF':
        stock_type = 'ETF'
    else:
        stock_type = 'Unknown'

    # Handle the stock based on its type
    if stock_type == 'Equity':
        embed = handle_equity(stock_info, data, isOpen)
    elif stock_type == 'ETF':
        embed = handle_etf(stock_info, data, isOpen)
    else:
        embed = discord.Embed(title=f"{stock_info['longName']} / [{stock_info['symbol']}]", 
                              url=f"https://finance.yahoo.com/quote/{stock_info['symbol']}", 
                              colour=discord.Colour.dark_blue(), 
                              timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Error", value="Unknown stock type", inline=False)

    # Get historical data for the past week
    hist_data = yf.download(stock_info['symbol'], period="60d", interval="1d")

    # Create a candlestick chart with volume bars and a moving average line
    mpf.plot(hist_data,
             type='candle',
             mav=(2, 4, 6),
             volume=True,
             style=binance_dark,
             ylabel=f'Price ({stock_info["currency"]})',
             ylabel_lower='Volume',
             tight_layout=True)

    # Save the plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Add the plot to the embed message
    file = discord.File(buf, filename='plot.png')
    embed.set_image(url='attachment://plot.png')

    # Close the figure to prevent it from being displayed
    plt.close()

    await interaction.followup.send(embed=embed, file=file)