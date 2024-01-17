import datetime
from Utils.epoch import Epoch as ep
from Utils.Log import Logger
from Utils.EmbedResponse import Response as rs

async def executeCvTime(interaction, month, day, hour, min, year, sec):
    Logger.info(f"{interaction.user.display_name} request cvtime()")

    # As default, using current year
    year = year or datetime.datetime.today().year

    # 0 Second is default argument
    if(sec == None):
        sec = 0

    detStamp = ep.ConvertTime(year, month, day, hour, min, sec)

    # Exception Handling
    if(detStamp == 0):
        Logger.error("Something went wrong while processing cvtime()")
        embed = rs.error("처리 중 문제가 생겼어요. 날짜 및 시간을 제대로 확인해 주세요.")
        await interaction.response.send_message("처리 중 문제가 생겼어요. 날짜 및 시간을 제대로 확인해 주세요.", ephemeral=True)

    # Success
    else:
        srcTime = ep.ConvertStamp(detStamp)
        Logger.info(f'Convert Datetime {srcTime} (GMT+9) to Timestamp / {detStamp}')
        embed = rs.general(title=f'Datetime "{srcTime} (GMT+9)" to Timestamp', content=f'{detStamp}')
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def executeCvStamp(interaction, srcstamp):

    Logger.info(f"{interaction.user.display_name} request cvstamp()")

    detTime = ep.ConvertStamp(srcstamp)

    Logger.info(f"Convert Timestamp {srcstamp} to Datetime / {detTime} (GMT+9)")
    embed = rs.general(title=f'"Timestamp "{srcstamp}" to Datetime"', content=f'<t:{srcstamp}:F>')
    await interaction.response.send_message(embed=embed, ephemeral=True)