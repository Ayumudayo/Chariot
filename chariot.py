import discord
import json
from discord import app_commands

from Utils.Init import RbtInit

with open("./keys.json", 'r') as f:
    cfg = json.load(f)

f.close()

MY_GUILD = discord.Object(id=cfg['GUILD_ID'])
OWNER_ID = cfg['OWNER_ID']

#region Bot initialize
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        #self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=None)

client = MyClient()

# Initialize the Red-Black Tree
eqt_rbt = RbtInit('eqt').init_rbt()
etf_rbt = RbtInit('etf').init_rbt()

@client.event
async def on_ready():

    # Set Activity
    activity = discord.Game(name="줄 ㅋㅋ")
    await client.change_presence(status=discord.Status.online, activity=activity)

    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
#endregion

#region KD
# Get result with random blanks
@client.tree.command()
@app_commands.describe(query='변환할 한국어 문자열')
async def kd(
    interaction: discord.Interaction,
    query: app_commands.Range[str, 0, 30]
):
    """한국어 문자열을 무작위 공백을 포함한 번역투 문장으로 변환"""

    from Command.cKD import executeKd
    await executeKd(interaction, query)
#endregion

#region Line
@client.tree.command()
@app_commands.describe(prize='품목', hour='시간', min='분', sec='초')
async def line(interaction: discord.Interaction, prize: str, hour: app_commands.Range[int, 0, 12], min: app_commands.Range[int, 0, 59], sec: app_commands.Range[int, 0, 59] = None):
    """줄을 세운다...! 마감까지의 시간은 5분 이상으로 설정하세요."""

    from Command.cLine import executeLine
    await executeLine(interaction, prize, hour, min, sec)
#endregion

#region Exchange
@client.tree.command()
@app_commands.describe(twd='신 타이완 달러')
async def tk(interaction: discord.Interaction, twd: app_commands.Range[float, 0, None]):
    """신 타이완 달러를 원화로 표시. 0 이상의 정수를 입력할 것."""

    from Command.cExchange import executeTk
    await executeTk(interaction, twd)

@client.tree.command()
@app_commands.describe(src='변환할 화폐', amount='돈의 양', dst='변환 목적 화폐')
async def exchange(interaction: discord.Interaction, src: str, amount: float, dst: str=None):
    """환율 계산. dst는 미입력시 KRW로 간주합니다."""

    from Command.cExchange import executeExchange
    await executeExchange(interaction, src, amount, dst)
#endregion

#region Exchange_Rate_Table
@client.tree.command()
@app_commands.describe(src='Source Currency. Default : USD', amount='Amount of Source Currency. Default : 1')
async def ratetable(interaction: discord.Interaction, src: str=None, amount: app_commands.Range[float, 0, None]=None):
    """Show the exchange rate table."""

    from Command.cExchange import execetueRateTable
    await execetueRateTable(interaction, src, amount)
#endregion

#region Epoch
@client.tree.command()
@app_commands.describe(year='연도', month='월', day='일', hour='시', min='분', sec='초')
async def cvtime(interaction: discord.Interaction, month: app_commands.Range[int, 1, 12], day: app_commands.Range[int, 1, 31], 
                hour: app_commands.Range[int, 0,23 ], min: app_commands.Range[int, 0, 59],
                year: app_commands.Range[int, 0, 9999]=None, sec: app_commands.Range[int, 0, 59]=None):
    """Datetime을 Timestamp로 변환. 24시간 포맷으로 입력할 것."""

    from Command.cEpoch import executeCvTime
    await executeCvTime(interaction, month, day, hour, min, year, sec)

@client.tree.command()
@app_commands.describe(srcstamp='타임스탬프')
async def cvstamp(interaction: discord.Interaction, srcstamp: int):
    """Timestamp를 Datetime으로 변환."""

    from Command.cEpoch import executeCvStamp
    await executeCvStamp(interaction, srcstamp)
#endregion

#region Metric
@client.tree.command()
@app_commands.describe(value='값', imp='입력 가능 단위: in, ft, yd, mi, gal, oz, lb.' )
async def convertimp(interaction: discord.Interaction, value: float, imp: str):
    """기열 임페리얼을 기합 메트릭으로 변환."""

    from Command.cConvertImp import executeConvertImp
    await executeConvertImp(interaction, value, imp)
#endregion

#region DeepL
# @client.tree.command()
# @app_commands.describe(src='출발 언어. 미입력시 자동으로 언어 감지.', dst='도착 언어. 미입력시 한국어로 간주. DE, EN, ES, FR, IT, JA 등 입력 가능', query='번역할 내용')
# async def deepl(interaction: discord.Interaction, query: str, src: str=None, dst: str=None):
#     """DeepL을 사용해 텍스트 번역. 자동으로 입력 언어를 감지합니다."""

#     from Command.cDeepL import executeDeepL
#     await executeDeepL(interaction, query, src, dst)
#endregion

#region MaintInfo
@client.tree.command()
async def maintinfo(interaction: discord.Interaction):
    """공지 관련 정보를 임베드로 작성"""

    from Command.cMaintInfo import executeMaintinfo
    await executeMaintinfo(interaction)
#endregion

#region Stock
@client.tree.command()
@app_commands.describe(ticker = '주식 종목 코드. 미입력시 NVDA로 간주')
async def stock(interaction: discord.Interaction, ticker: str=None):
    """해당 주식 종목에 대한 그래프를 포함한 정보를 임베드 메세지 형태로 제공"""

    from Command.cStock import executeStock
    await executeStock(interaction, ticker, eqt_rbt)
#endregion

#region Stock
@client.tree.command()
@app_commands.describe(ticker = 'ETF 코드, 미입력시 리스트 출력')
async def etf(interaction: discord.Interaction, ticker: str=None):
    """쏚쓸말좆양봉호로야스출발ㅋㅋ"""

    from Command.cETF import print_etfs
    await print_etfs(interaction, etf_rbt, ticker)
#endregion



# #region Tester
# @client.tree.command()S
# async def test(interaction: discord.Interaction, ticker: str=None):
#     await executeStock(interaction, ticker)
# #endregion

#region sync
@client.tree.command(name='sync', description='Owner only')
async def sync(interaction: discord.Interaction):
    if interaction.user.id == OWNER_ID:
        await interaction.response.defer(ephemeral=True)
        await client.tree.sync()
        await interaction.followup.send('Synced', ephemeral=True)
    else:
        await interaction.followup.send('You have no permission to use this command.', ephemeral=True)
#endregion

client.run(cfg['BotToken'])