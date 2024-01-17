from Utils.Log import Logger
from Utils.unit import unit
from Utils.EmbedResponse import Response as rs

async def executeConvertImp(interaction, value, imp):

    Logger.info(f"{interaction.user.display_name} request convertImp().")

    resVal, resMet = unit.imperial_to_metric(value, imp)

    if (resMet == 'ERROR'):
        Logger.error("An error occured while processing convertImp()")
        embed = rs.error("처리 중 문제가 생겼어요. 단위와 값을 확인해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    Logger.info(f"{value} {imp} to Metric is {resVal:.2f} {resMet}")
    embed = rs.general(title=f'{value} {imp} **IN METRIC**', content=f'**{resVal:.2f} {resMet}**  ||  1{imp} = {unit.imperial_to_metric(1, imp)[0]:.2f} {resMet}')
    await interaction.response.send_message(embed=embed, ephemeral=True)