import discord
import asyncio
import datetime
import random
import time

import json

from discord import app_commands
from Buttons.LineBtn import Entry as ent

from Utils.PapagoLib import Translator
from Utils.PandasCsv import pdCsv as pc
from Utils.Currency import Exchange as ex
from Utils.epoch import Epoch as ep
from Utils.Log import Logger as lg
from Utils import checkover as co

with open("./keys.json", 'r') as f:
    cfg = json.load(f)

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
        await self.tree.sync()

client = MyClient()


@client.event
async def on_ready():

    # Set Activity
    activity = discord.Game(name="줄 ㅋㅋ")
    await client.change_presence(status=discord.Status.idle, activity=activity)

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

    if(not Translator.LangDect(query)):
        lg.writeLog(2, "Inputted string is not Korean.")
        await interaction.response.send_message('입력된 문자열이 한국어가 아닙니다.', ephemeral=True)
    else:
        output = Translator.getRes(query)
        lg.writeLog(1, f"kd() output : {output}")
        await interaction.response.send_message(output, ephemeral=True)

# Get result without random blanks
@client.tree.command()
@app_commands.describe(query='변환할 한국어 문자열')
async def kdnorm(
    interaction: discord.Interaction,
    query: app_commands.Range[str, 0, 30]
):
    """한국어 문자열을 추가적 공백 삽입 없는 번역투 문장으로 변환"""

    if(not Translator.LangDect(query)):
        lg.writeLog(2, "Inputted string is not Korean.")
        await interaction.response.send_message('입력된 문자열이 한국어가 아닙니다.', ephemeral=True)

    output = Translator.getRes(query, False)
    lg.writeLog(1, f"kdnorm() output : {output}")
    await interaction.response.send_message(output, ephemeral=True)
#endregion

#region Line
@client.tree.command()
@app_commands.describe(prize='품목', hour='시간', min='분', sec='초')
async def line(interaction: discord.Interaction, prize: str, hour: app_commands.Range[int, 0, 12], min: app_commands.Range[int, 0, 59], sec: app_commands.Range[int, 6, 59] = None):
    """줄을 세운다...! 마감까지의 시간은 5분 이상으로 설정하세요."""

    if (sec == None):
        sec = 0

    # Get csv
    pc.load_csv(interaction.guild_id)
    lastIdx = pc.load_csv(interaction.guild_id) + 1
    
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
    view = ent(interaction, prize)

    # Initial Embed
    embed = discord.Embed(title=f'"줄 #{lastIdx}"', timestamp=datetime.datetime.now(), colour=discord.Colour.random())
    embed.add_field(name='상품', value=prize, inline=True)
    embed.add_field(name='마감까지 남은 시간', value=f"<t:{ts}:R>", inline=False)
    embed.add_field(name='줄 세운 사람', value=f'<@{interaction.user.id}>')
    
    # Create Thread under channel where command input
    thrd = await interaction.channel.create_thread(name=interaction.user.display_name + '의 ' + prize + '줄', reason='"줄"', type=discord.ChannelType.public_thread)
    thrdMsg = await thrd.send(embed=embed, view=view)

    # Feedback to user
    await interaction.response.send_message('줄 생성 완료! 생성된 스레드를 확인하세요.')
    lg.writeLog(1, f"{interaction.user.display_name}'s {prize} Line has created.")

    # Wait for task ends
    isTaskEnd = await task

    if (isTaskEnd):
        if (len(view.entryList) == 0):

            # Temp Data
            dictTemp = {
                    '#': [lastIdx],
                    '품목': [prize],
                    '시작 시간': [datetime.datetime.fromtimestamp(start_time)],
                    '마감 시간': [datetime.datetime.fromtimestamp(ts)],
                    '줄 세운 사람': [f'({interaction.user.id} / {interaction.user.display_name})'],
                    '주작 결과': ['No Entry']
                }

            pc.save_csv(dictTemp)

            # Feedback to Thread and remove view from embed
            embed.clear_fields()
            
            embed.add_field(name='상품', value=prize, inline=True)
            embed.add_field(name='마감 시간', value=f"<t:{ts}:F>", inline=False)
            embed.add_field(name='줄 세운 사람', value=f'<@{interaction.user.id}>')
            embed.add_field(name='"주작 결과"', value='참가자가 없었어요.', inline=False)
            lg.writeLog(1, f"There was no Entry at {interaction.user.display_name}'s {prize} Line.")
            await thrdMsg.edit(embed=embed, view=None)

            await thrd.send(f'<@{interaction.user.id}> \n 참가자가 없었어요.')


        else:
                        
            # Get winner and edit embed
            winner = random.choice(view.entryList)

            # Temp Data
            dictTemp = {
                    '#': [lastIdx],
                    '품목': [prize],
                    '시작 시간': [datetime.datetime.fromtimestamp(start_time)],
                    '마감 시간': [datetime.datetime.fromtimestamp(ts)],
                    '줄 세운 사람': [f'{interaction.user.id} / {interaction.user.display_name}'],
                    '주작 결과': [f'{winner[1]} / {winner[0]}']
                }

            pc.save_csv(dictTemp)

            # Feedback to Thread and remove view from embed
            embed.clear_fields()
            
            embed.add_field(name='상품', value=prize, inline=True)
            embed.add_field(name='마감 시간', value=f"<t:{ts}:F>", inline=False)
            embed.add_field(name='줄 세운 사람', value=f'<@{interaction.user.id}>')
            embed.add_field(name='"주작 결과"',
                            value=f'<@{winner[1]}>',
                            inline=False)
            lg.writeLog(1, f"{winner[0]} gets {interaction.user.display_name}'s {prize}!")
            await thrdMsg.edit(embed=embed, view=None)

            await thrd.send(f'<@{winner[1]}>, <@{interaction.user.id}> \n 추첨 결과를 확인하세요!')

    else:
        # Temp Data
                dictTemp = {
                        '#': [lastIdx],
                        '품목': [prize],
                        '시작 시간': [datetime.datetime.fromtimestamp(start_time)],
                        '마감 시간': [datetime.datetime.fromtimestamp(ts)],
                        '줄 세운 사람': [f'({interaction.user.id} / {interaction.user.display_name})'],
                        '주작 결과': ['No proper deadline input']
                    }

                pc.save_csv(dictTemp)

                # Feedback to Thread and remove view from embed
                embed.clear_fields()

                embed.add_field(name='상품', value=prize, inline=True)
                embed.add_field(name='마감 시간', value=f"<t:{ts}:F>", inline=False)
                embed.add_field(name='줄 세운 사람', value=f'<@{interaction.user.id}>')
                embed.add_field(name='입력 오류 발생!', inline=False, value='마감시간은 현재 시간보다 빠를 수 없습니다.')
                lg.writeLog(2, "Deadline Input Error.")
                await thrdMsg.edit(embed=embed, view=None)

                await thrd.send(f'<@{interaction.user.id}> \n 마감 시간 입력이 제대로 되었나 확인하세요.')
#endregion

#region exchange
@client.tree.command()
@app_commands.describe(twd='신 타이완 달러')
async def tk(interaction: discord.Interaction, twd: app_commands.Range[float, 0, None]):
    """신 타이완 달러를 원화로 표시. 0 이상의 정수를 입력할 것."""

    lg.writeLog(1, f"{interaction.user.display_name} request tk().")

    result = ex.exchCur('twd', twd, 'krw')

    if(result != 0):
        twd = format(twd, ',')

        lg.writeLog(1, f"NT$ {twd} to KRW / {result}")
        await interaction.response.send_message(f"NT$ {twd} to KRW\n{result}", ephemeral=True)

@client.tree.command()
@app_commands.describe(src='변환할 화폐', amount='돈의 양', dst='변환 목적 화폐')
async def exchange(interaction: discord.Interaction, src: str, amount: float, dst: str=None):
    """환율 계산. dst는 미입력시 KRW로 간주합니다."""

    lg.writeLog(1, f"{interaction.user.display_name} request exchange.")

    if (dst == None):
        dst = 'krw'

    result = ex.exchCur(src, amount, dst)

    if(result != 0):
        src = src.upper()
        dst = dst.upper()

        amount = format(amount, ',')

        lg.writeLog(1, f"{src} {amount} to {dst} / {result}")
        await interaction.response.send_message(f"{src} {amount} to {dst}\n{result}", ephemeral=True)
    else:
        await interaction.response.send_message("처리 중 오류가 발생했습니다. USD, KRW, JPY와 같은 제대로 된 통화코드를 입력했나요?", ephemeral=True)
#endregion

#region Epoch
@client.tree.command()
@app_commands.describe(year='연도', month='월', day='일', hour='시', min='분', sec='초')
async def cvtime(interaction: discord.Interaction, month: app_commands.Range[int, 1, 12], day: app_commands.Range[int, 1, 31], 
                hour: app_commands.Range[int, 0,23 ], min: app_commands.Range[int, 0, 59],
                year: app_commands.Range[int, 0, 9999]=None, sec: app_commands.Range[int, 0, 59]=None):
    """Datetime을 Timestamp로 변환. 24시간 포맷으로 입력할 것."""

    lg.writeLog(1, f"{interaction.user.display_name} request cvtime()")

    # As default, using current year
    if(year == None):
        year = datetime.datetime.today().year

    # 0 Second is default argument
    if(sec == None):
        sec = 0

    detStamp = ep.ConvertTime(year, month, day, hour, min, sec)

    # Exception Handling
    if(detStamp == 0):
        lg.writeLog(2, "Something went wrong while processing cvtime()")
        await interaction.response.send_message("처리 중 문제가 생겼어요. 날짜 및 시간을 제대로 확인해 주세요.", ephemeral=True)

    else:
        srcTime = ep.ConvertStamp(detStamp)
        lg.writeLog(1, f'Convert Datetime {srcTime} (GMT+9) to Timestamp / {detStamp}')
        await interaction.response.send_message(f'Convert Datetime "{srcTime} (GMT+9)" to Timestamp\n{detStamp}', ephemeral=True)

@client.tree.command()
@app_commands.describe(srcstamp='타임스탬프')
async def cvstamp(interaction: discord.Interaction, srcstamp: int):
    """Timestamp를 Datetime으로 변환."""

    lg.writeLog(1, f"{interaction.user.display_name} request cvstamp()")

    detTime = ep.ConvertStamp(srcstamp)

    # Exception Handling
    if(detTime == 0):
        lg.writeLog(2, "Something went wrong while processing cvstamp()")
        await interaction.response.send_message("처리 중 문제가 생겼어요. 제대로 된 스탬프를 입력했나요?", ephemeral=True)

    else:
        lg.writeLog(1, f"Convert Timestamp {srcstamp} to Datetime / {detTime} (GMT+9)")
        await interaction.response.send_message(f'Convert Timestamp "{srcstamp}" to Datetime\n{detTime} (GMT+9)', ephemeral=True)
#endregion

client.run(cfg['BotToken'])