import discord
import datetime
import pytz

from Utils.Log import Logger
from Utils.PapagoLib import Translator
from Utils.MaintParser import Parser as pa

async def executeMaintinfo(interaction):
    """공지 관련 정보를 임베드로 작성"""

    await interaction.response.defer(ephemeral=False)

    Logger.info(f"{interaction.user.display_name} request maintinfo()")
    
    # 0 = Start, 1 = End, 2 = Title, 3 = Link
    time_info = pa.GetMaintTimeStamp()

    if not time_info:
        embed = discord.Embed(title="점검 일정이 없습니다!", 
                              colour=discord.Colour.dark_red(), 
                              timestamp=pytz.utc.localize(datetime.datetime.utcnow()))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1138398345065414657/1138398369929244713/0001061.png")
        embed.add_field(name="", value="현재 확인할 수 있는 점검 공지가 없습니다.\n무언가 문제가 있다면 공식 로드스톤을 참고해 주세요.")
        await interaction.followup.send(embed=embed)
        return

    output = Translator.Translate(time_info[2])

    embed = discord.Embed(title=time_info[2], 
                          url=time_info[3], 
                          description=output, 
                          colour=discord.Colour.dark_blue(), 
                          timestamp=pytz.utc.localize(datetime.datetime.utcnow()))
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1138398345065414657/1138398369929244713/0001061.png")
    embed.add_field(name="일정", value=f'시작 : <t:{time_info[0]}:F> \n종료 : <t:{time_info[1]}:F> \n\n<t:{time_info[1]}:R>', inline=False)
    await interaction.followup.send(embed=embed)

    Logger.info(f'공지 링크 : {time_info[3]}')