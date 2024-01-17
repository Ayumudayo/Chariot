from Utils.Log import Logger
from Utils.deepL import deepl_translator as dl
from Utils.EmbedResponse import Response as rs

async def executeDeepL(interaction, query, src, dst):

    # Discord messages cannot contain over 2000 characters.
    # We can send over 5000 characters as input of the command,
    # but we cannot send a result that is over 2000 characters.
    # The following 3000 characters become meaningless.
    # Therefore, we need to slice the input query to 2000 characters.
    if len(query) > 2000:
        embed = rs.error("번역할 내용이 너무 길어요. 2000자 이하로 입력해 주세요.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        Logger.info(f"{interaction.user.display_name} requested deepl() with over 2000 characters.")
        return
    
    # DeepL support Auto-Detect
    if src is None:
        src = 'auto'

    if dst is None:
        dst = 'ko'

    Logger.info(f"{interaction.user.display_name} requested deepl().")

    await interaction.response.defer(ephemeral=True)
    tr_res_temp = await dl.dl_trans(src, dst, query)

    # Slice if over 2000 characters
    if(len(tr_res_temp) > 2000):
        #result = f"결과가 2000자를 초과하여 모든 결과를 표시할 수 없습니다. \n\n{result}"
        result = tr_res_temp[:2000]
        embed = rs.general(title="결과가 2000자를 초과하여 모든 결과를 표시할 수 없습니다.", content=result)
        Logger.info("Result message has exceeded 2000 characters; All of the message cannot be sent.")
        await interaction.followup.send(embed=embed)

        return

    embed = rs.general(title=f"DeepL Translation to ***{dst.upper()}***", content=tr_res_temp)
    Logger.info(f"The translation has completed successfully.")
    await interaction.followup.send(embed=embed)