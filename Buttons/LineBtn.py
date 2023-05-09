import datetime
import time
import discord

from Utils.Log import Logger as lg
from Database.dynamo import awsDynamo as ad

# Button class
class Entry(discord.ui.View):
    def __init__(self, ebdInteraction, prize, lNum):
        super().__init__(timeout=None)
        self.value = None
        self.ebdIntr = ebdInteraction
        self.entryList = []
        self.prize = prize
        self.lNum = lNum
        self.ad = ad()
    
    # Entry a draw
    @discord.ui.button(label="줄 서기", style=discord.ButtonStyle.green, custom_id='entry')
    async def doEntry(self, btnInteraction: discord.Interaction, button: discord.ui.Button):
        if(self.ebdIntr.user.id != btnInteraction.user.id):
            # Append user info to entryList in Tuple
            if(not self.ad.checkExist(self.lNum, btnInteraction.user.id)):

                start_time = int(time.time())

                data = {
                     "linenumber": self.lNum,
                     "entryuserID": btnInteraction.user.id,
                     "entryuserName": btnInteraction.user.display_name,
                     "entrytime": f'{datetime.datetime.fromtimestamp(start_time)}'
                }

                self.ad.push(data, 'entrylist')
                lg.info(f"{btnInteraction.user.display_name} Entry at {self.ebdIntr.user.display_name}'s {self.prize} Line.")
                await btnInteraction.response.send_message("줄 서기 완료!", ephemeral=True)

            else:
                await btnInteraction.response.send_message("이미 줄 스신거 같은데...", ephemeral=True)
        else:
            await btnInteraction.response.send_message("줄 세운 사람이 줄 스면 어쩌나?", ephemeral=True)


    # 1. 줄에 이미 있는지 확인
    # 2. 없다면 알림
    # 3. 있다면 피드백 해 주며 빼기
    # Exit from draw
    @discord.ui.button(label="줄 나가기", style=discord.ButtonStyle.red, custom_id='exit')
    async def exitEntry(self, btnInteraction: discord.Interaction, button: discord.ui.Button):
        if(self.ebdIntr.user.id != btnInteraction.user.id):
            # Append user info to entryList in Tuple
            if(self.ad.checkExist(self.lNum, btnInteraction.user.id)):
                self.ad.delete(self.lNum, btnInteraction.user.id)
                lg.info(f"{btnInteraction.user.display_name} Exit from {self.ebdIntr.user.display_name}'s {self.prize} Line.")
                await btnInteraction.response.send_message("줄 나가기 완료!", ephemeral=True)

            else:
                await btnInteraction.response.send_message("줄을 안섰는데 빠질 수 있을까...", ephemeral=True)
        else:
            await btnInteraction.response.send_message("줄 세운 사람이 줄에서 빠지는게 가능할까?", ephemeral=True)


    # Print entryList
    @discord.ui.button(label="참가자 확인", style=discord.ButtonStyle.grey, custom_id='checkEntry')
    async def printEntry(self, btnInteraction: discord.Interaction, button: discord.ui.Button):
        tmpList = []
        tmpStr = '참가자 목록' + '\n'

        lg.info(f"{btnInteraction.user.display_name} request List Print.")
        
        res = self.ad.getEntryUsers(self.lNum)

        if(len(res) != 0):
            for tmp in res:
                # Get each user's display name
                tmp = tmp['entryuserID']
                tmpList.append(f'<@{tmp}>')

            tmpStr = '\n'.join(tmpList)

            # Print users' display name by tagging
            await btnInteraction.response.send_message(tmpStr, ephemeral=True)
        else:
            await btnInteraction.response.send_message("참가자가 없어요.", ephemeral=True)
      
        lg.info("List printed.")