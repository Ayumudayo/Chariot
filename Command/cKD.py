from Utils.PapagoLib import Translator
from Utils.Log import Logger
from Utils.EmbedResponse import Response as rs

tr = Translator()

async def executeKd(interaction, query):

    if not tr.lang_dectKD(query):
        Logger.error("Inputted string is not Korean.")
        embed = rs.error('입력된 문자열이 한국어가 아닙니다.')
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    output = tr.get_res(query)
    Logger.info(f"kd() output : {output}")
    embed = rs.general('변환 완료!' ,output)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    return