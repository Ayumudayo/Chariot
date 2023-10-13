import discord
import datetime
import io

import yfinance as yf
import mplfinance as mpf
import matplotlib.pyplot as plt

from Utils.Log import Logger

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

async def executeStock(interaction, ticker):
       
    await interaction.response.defer(ephemeral=False)

    Logger.info(f'{interaction.user.display_name} Executing stock command with ticker: {ticker}')

    # Set default value
    if ticker is None:
        ticker = 'NVDA'

    # Get stock information from Yahoo Finance API
    stock_info = yf.Ticker(ticker).info

    # Create embed message with stock information
    embed = discord.Embed(title=f"{stock_info['longName']} / [{stock_info['symbol']}]", 
                          url=f"https://finance.yahoo.com/quote/{stock_info['symbol']}", 
                          colour=discord.Colour.dark_blue(), 
                          timestamp=datetime.datetime.utcnow())
    
    #embed.set_thumbnail(url=stock_info['logo_url'])
    embed.add_field(name="Current Price", value=f"{stock_info['currentPrice']:,.2f} {stock_info['currency']}" if stock_info['currentPrice'] is not None else 'None', inline=False)
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
    ex_dividend_date = datetime.datetime.fromtimestamp(stock_info['exDividendDate']).strftime('%Y-%m-%d')
    embed.add_field(name="Ex-Dividend Date", value=ex_dividend_date, inline=True)

    # 21Day Graph
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name="21 Day Graph", value=" ", inline=False)

    embed.set_footer(text="Data provided by Yahoo! Finance API")

    # Get historical data for the past week
    hist_data = yf.download(stock_info['symbol'], period="21d", interval="1d")

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
