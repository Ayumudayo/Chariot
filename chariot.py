import discord
import asyncio
import datetime
import random
import time

import json

from discord import app_commands
from Buttons.LineBtn import Entry as ent

from Utils.PapagoLib import Translator
from Utils.Currency import Exchange as ex
from Utils.epoch import Epoch as ep
from Utils.Log import Logger
from Utils.unit import unit
from Utils import checkover as co
from Utils.deepL import deepl_translator as dl
from Utils.MaintParser import Parser as pa
from Utils.EmbedResponse import Response as rs

from Database.dynamo import awsDynamo



with open("./keys.json", 'r') as f:
    cfg = json.load(f)

f.close()

MY_GUILD = discord.Object(id=cfg['GUILD_ID'])


TR_Cliend_Id = cfg['PapagoTranslator']['TR_Cliend_Id']
TR_Cliend_Secret = cfg['PapagoTranslator']['TR_Cliend_Secret']

LD_Cliend_Id = cfg['PapagoLanguageDetector']['LD_Cliend_Id']
LD_Cliend_Secret = cfg['PapagoLanguageDetector']['LD_Cliend_Secret']

Translator(TR_Cliend_Id, TR_Cliend_Secret, LD_Cliend_Id, LD_Cliend_Secret)

#region Bot initialize
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        #self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=None)

client = MyClient()
lg = Logger()

@client.event
async def on_ready():

    # Set Activity
    activity = discord.Game(name="줄 ㅋㅋ")
    await client.change_presence(status=discord.Status.online, activity=activity)

    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

    f.close()
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

    if not Translator.LangDectKD(query):
        lg.error("Inputted string is not Korean.")
        embed = rs.error('입력된 문자열이 한국어가 아닙니다.')
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    output = Translator.getRes(query)
    lg.info(f"kd() output : {output}")
    embed = rs.general('변환 완료!' ,output)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    return
#endregion

#region Line
@client.tree.command()
@app_commands.describe(prize='품목', hour='시간', min='분', sec='초')
async def line(interaction: discord.Interaction, prize: str, hour: app_commands.Range[int, 0, 12], min: app_commands.Range[int, 0, 59], sec: app_commands.Range[int, 0, 59] = None):
    """줄을 세운다...! 마감까지의 시간은 5분 이상으로 설정하세요."""

    if (sec == None):
        sec = 0

    # Get DB class
    ad = awsDynamo()
    lastIdx = ad.getLineNumber() + 1
    
    # Get deadline from user
    total_time = 3600 * hour + 60 * min + sec

    if(total_time < 300):
        await interaction.response.send_message('시간이 너무 짧습니다. 5분 이상의 시간으로 설정하세요.', ephemeral=True)
        return

    start_time = int(time.time())
    ts = start_time + total_time
    
    # Create countdown Task
    task = asyncio.create_task(co.checkOver(ts))

    # Create button View
    view = ent(interaction, prize, lastIdx)

    # Initial Embed
    embed = discord.Embed(title=f'"줄 #{lastIdx}"', timestamp=datetime.datetime.now(), colour=discord.Colour.random())
    embed.add_field(name='상품', value=prize, inline=True)
    embed.add_field(name='마감까지 남은 시간', value=f"<t:{ts}:R>", inline=False)
    embed.add_field(name='줄 세운 사람', value=f'<@{interaction.user.id}>')

    # Data before end
    itemTemp = {
        "LinePK": 'Joul',
        "linenumber": lastIdx,
        "createtime": f'{datetime.datetime.fromtimestamp(start_time)}',
        "creatorID": f'{interaction.user.id}',
        "creatorName": f'{interaction.user.display_name}',
        "endtime": f'{datetime.datetime.fromtimestamp(ts)}',
        "isEntryEnd": 0,
        "prize": prize,
        "winnerID": 0,
        "winnerName": 'None'
    }
    
    # Push item to Table
    ad.push(itemTemp, 'linelists')
    
    # Create Thread under channel where command input
    thrd = await interaction.channel.create_thread(name=interaction.user.display_name + '의 ' + prize + '줄', reason='"줄"', type=discord.ChannelType.public_thread)
    thrdMsg = await thrd.send(embed=embed, view=view)

    # Feedback to user
    await interaction.response.send_message('줄 생성 완료! 생성된 스레드를 확인하세요.')
    lg.info(f"{interaction.user.display_name}'s {prize} Line has created.")

    # Wait for task ends
    isTaskEnd = await task

    if (isTaskEnd):
        if (len(ad.getEntryUsers(lastIdx)) == 0):

            # Update result
            ad.update(1, 0, 'No Entry', lastIdx)

            # Feedback to Thread and remove view from embed
            embed.clear_fields()
            
            embed.add_field(name='상품', value=prize, inline=True)
            embed.add_field(name='마감 시간', value=f"<t:{ts}:F>", inline=False)
            embed.add_field(name='줄 세운 사람', value=f'<@{interaction.user.id}>')
            embed.add_field(name='"주작 결과"', value='참가자가 없었어요.', inline=False)
            lg.info(f"There was no Entry at {interaction.user.display_name}'s {prize} Line.")
            await thrdMsg.edit(embed=embed, view=None)

            await thrd.send(f'<@{interaction.user.id}> \n 참가자가 없었어요.')


        else:                        
            # Get winner and edit embed=
            winner = random.choice(ad.getEntryUsers(lastIdx))
            winnerID = winner['entryuserID']
            winnerName = winner['entryuserName']

            # Update data
            ad.update(1, f'{winnerID}', f'{winnerName}', lastIdx)

            # Feedback to Thread and remove view from embed
            embed.clear_fields()
            
            embed.add_field(name='상품', value=prize, inline=True)
            embed.add_field(name='마감 시간', value=f"<t:{ts}:F>", inline=False)
            embed.add_field(name='줄 세운 사람', value=f'<@{interaction.user.id}>')
            embed.add_field(name='"주작 결과"',
                            value=f'<@{winnerID}>',
                            inline=False)
            lg.info(f"{winnerName} gets {interaction.user.display_name}'s {prize}!")
            await thrdMsg.edit(embed=embed, view=None)

            await thrd.send(f'<@{winnerID}>, <@{interaction.user.id}> \n 추첨 결과를 확인하세요!')

    else:

        # Update status
        ad.update(1, 0, 'Input Error', lastIdx)

        # Feedback to Thread and remove view from embed
        embed.clear_fields()
        embed.add_field(name='상품', value=prize, inline=True)
        embed.add_field(name='마감 시간', value=f"<t:{ts}:F>", inline=False)
        embed.add_field(name='줄 세운 사람', value=f'<@{interaction.user.id}>')
        embed.add_field(name='입력 오류 발생!', inline=False, value='마감시간은 현재 시간보다 빠를 수 없습니다.')
        lg.error("Deadline Input Error.")

        await thrdMsg.edit(embed=embed, view=None)
        await thrd.send(f'<@{interaction.user.id}> \n 마감 시간 입력이 제대로 되었나 확인하세요.')
#endregion

#region Exchange
@client.tree.command()
@app_commands.describe(twd='신 타이완 달러')
async def tk(interaction: discord.Interaction, twd: app_commands.Range[float, 0, None]):
    """신 타이완 달러를 원화로 표시. 0 이상의 정수를 입력할 것."""

    lg.info(f"{interaction.user.display_name} request tk().")

    result = ex.exchCur('twd', twd, 'krw')

    if(result != 0):
        twd = format(twd, ',')

        lg.info(f"NT$ {twd} to KRW / {result}")
        await interaction.response.send_message(f"NT$ {twd} to KRW\n{result}", ephemeral=True)

@client.tree.command()
@app_commands.describe(src='변환할 화폐', amount='돈의 양', dst='변환 목적 화폐')
async def exchange(interaction: discord.Interaction, src: str, amount: float, dst: str=None):
    """환율 계산. dst는 미입력시 KRW로 간주합니다."""

    lg.info(f"{interaction.user.display_name} request exchange().")

    if (dst == None):
        dst = 'krw'

    result = ex.exchCur(src, amount, dst)

    if(result != 0):
        src = src.upper()
        dst = dst.upper()

        amount = format(amount, ',')

        lg.info(f"{src} {amount} to {dst} / {result}")
        await interaction.response.send_message(f"{src} {amount} to {dst}\n{result}", ephemeral=True)
    else:
        await interaction.response.send_message("처리 중 오류가 발생했습니다. USD, KRW, JPY와 같은 제대로 된 통화코드를 입력했나요?", ephemeral=True)
#endregion

#region Exchange_Rate_Table
@client.tree.command()
@app_commands.describe(src='Source Currency. Default : USD', amount='Amount of Source Currency. Default : 1')
async def ratetable(interaction: discord.Interaction, src: str=None, amount: app_commands.Range[float, 0, None]=None):
    """Show the exchange rate table."""

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
        lg.error("Something went wrong while processing ratetable()")
        embed = rs.error("처리 중 오류가 발생했습니다. USD, KRW, JPY와 같은 제대로 된 통화코드를 입력했는지 확인하세요.")
        await interaction.followup.send(embed=embed, ephemeral=True)
#endregion

#region Epoch
@client.tree.command()
@app_commands.describe(year='연도', month='월', day='일', hour='시', min='분', sec='초')
async def cvtime(interaction: discord.Interaction, month: app_commands.Range[int, 1, 12], day: app_commands.Range[int, 1, 31], 
                hour: app_commands.Range[int, 0,23 ], min: app_commands.Range[int, 0, 59],
                year: app_commands.Range[int, 0, 9999]=None, sec: app_commands.Range[int, 0, 59]=None):
    """Datetime을 Timestamp로 변환. 24시간 포맷으로 입력할 것."""

    lg.info(f"{interaction.user.display_name} request cvtime()")

    # As default, using current year
    year = year or datetime.datetime.today().year

    # 0 Second is default argument
    if(sec == None):
        sec = 0

    detStamp = ep.ConvertTime(year, month, day, hour, min, sec)

    # Exception Handling
    if(detStamp == 0):
        lg.error("Something went wrong while processing cvtime()")
        embed = rs.error("처리 중 문제가 생겼어요. 날짜 및 시간을 제대로 확인해 주세요.")
        await interaction.response.send_message("처리 중 문제가 생겼어요. 날짜 및 시간을 제대로 확인해 주세요.", ephemeral=True)

    else:
        srcTime = ep.ConvertStamp(detStamp)
        lg.info(f'Convert Datetime {srcTime} (GMT+9) to Timestamp / {detStamp}')
        embed = rs.general(title=f'Datetime "{srcTime} (GMT+9)" to Timestamp', content=f'{detStamp}')
        await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command()
@app_commands.describe(srcstamp='타임스탬프')
async def cvstamp(interaction: discord.Interaction, srcstamp: int):
    """Timestamp를 Datetime으로 변환."""

    lg.info(f"{interaction.user.display_name} request cvstamp()")

    detTime = ep.ConvertStamp(srcstamp)

    # Exception Handling
    if(detTime == 0):
        lg.error("Something went wrong while processing cvstamp()")
        embed = rs.error("처리 중 문제가 생겼어요. 스탬프를 제대로 확인해 주세요.")
        await interaction.response.send_message("처리 중 문제가 생겼어요. 제대로 된 스탬프를 입력했나요?", ephemeral=True)

    else:
        lg.info(f"Convert Timestamp {srcstamp} to Datetime / {detTime} (GMT+9)")
        embed = rs.general(title=f'"Timestamp "{srcstamp}" to Datetime"', content=f'{detTime} (GMT+9)')
        await interaction.response.send_message(embed=embed, ephemeral=True)
#endregion

#region Metric
@client.tree.command()
@app_commands.describe(value='값', imp='입력 가능 단위: in, ft, yd, mi, gal, oz, lb.' )
async def convertimp(interaction: discord.Interaction, value: float, imp: str):
    """기열 임페리얼을 기합 메트릭으로 변환."""

    lg.info(f"{interaction.user.display_name} request convertImp().")

    resVal, resMet = unit.imperial_to_metric(value, imp)

    if (resMet == 'ERROR'):
        lg.error("An error occured while processing convertImp()")
        embed = rs.error("처리 중 문제가 생겼어요. 단위와 값을 확인해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    lg.info(f"{value} {imp} to Metric is {resVal:.2f} {resMet}")
    embed = rs.general(title=f'{value} {imp} **IN METRIC**', content=f'**{resVal:.2f} {resMet}**')
    await interaction.response.send_message(embed=embed, ephemeral=True)
#endregion

#region DeepL
@client.tree.command()
@app_commands.describe(src='출발 언어. 미입력시 자동으로 언어 감지.', dst='도착 언어. 미입력시 한국어로 간주. DE, EN, ES, FR, IT, JA 등 입력 가능', query='번역할 내용')
async def deepl(interaction: discord.Interaction, query: str, src: str=None, dst: str=None):
    """DeepL을 사용해 텍스트 번역. 자동으로 입력 언어를 감지합니다."""

    # Discord message cannot contain over 2000 characters.
    # We can send over 5000 characters as input of command,
    # But cannot send result which is over 2000 characters.
    # The following 3000 characters become meaningless.
    # So, we need to slice the input query to 2000 characters.
    if len(query) > 2000:
        embed = rs.error("번역할 내용이 너무 길어요. 2000자 이하로 입력해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        lg.info(f"{interaction.user.display_name} requested deepl() with over 2000 characters.")
        return
    
    # DeepL support Auto-Detect
    if src is None:
        src = 'auto'

    if dst is None:
        dst = 'ko'

    lg.info(f"{interaction.user.display_name} requested deepl().")

    await interaction.response.defer(ephemeral=True)
    tr_res_temp = await dl.dl_trans(src, dst, query)

    # Slice if over 2000 characters
    if(len(tr_res_temp) > 2000):
        #result = f"결과가 2000자를 초과하여 모든 결과를 표시할 수 없습니다. \n\n{result}"
        result = tr_res_temp[:2000]
        embed = rs.general(title="결과가 2000자를 초과하여 모든 결과를 표시할 수 없습니다.", content=result)
        lg.info("Result message has exceeded 2000 characters; All of the message cannot be sent.")
        await interaction.followup.send(embed=embed)

        return

    embed = rs.general(title=f"DeepL Translation to ***{dst.upper()}***", content=tr_res_temp)
    lg.info(f"The translation has completed successfully.")
    await interaction.followup.send(embed=embed)
#endregion

#region MaintInfo
@client.tree.command()
async def maintinfo(interaction: discord.Interaction):
    """공지 관련 정보를 임베드로 작성"""

    await interaction.response.defer(ephemeral=False)

    lg.info(f"{interaction.user.display_name} request maintinfo()")
    
    # 0 = Start, 1 = End, 2 = Title, 3 = Link
    time_info = pa.GetMaintTimeStamp()

    if not time_info:
        embed = discord.Embed(title="점검 일정이 없습니다!", 
                              colour=discord.Colour.dark_red(), 
                              timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1138398345065414657/1138398369929244713/0001061.png")
        embed.add_field(name="", value="현재 확인할 수 있는 점검 공지가 없습니다.\n무언가 문제가 있다면 공식 로드스톤을 참고해 주세요.")
        await interaction.followup.send(embed=embed)
        return

    output = Translator.Translate(time_info[2])

    embed = discord.Embed(title=time_info[2], 
                          url=time_info[3], 
                          description=output, 
                          colour=discord.Colour.dark_blue(), 
                          timestamp=datetime.datetime.utcnow())
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1138398345065414657/1138398369929244713/0001061.png")
    embed.add_field(name="일정", value=f'시작 : <t:{time_info[0]}:F> \n종료 : <t:{time_info[1]}:F> \n\n<t:{time_info[1]}:R>', inline=False)
    await interaction.followup.send(embed=embed)

    lg.info(f'공지 링크 : {time_info[3]}')
#endregion

client.run(cfg['BotToken'])