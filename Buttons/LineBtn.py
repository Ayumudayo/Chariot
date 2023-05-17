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

        if self.ebdIntr.user.id == btnInteraction.user.id:
            await btnInteraction.response.send_message("줄 세운 사람이 줄 스면 어쩌나?", ephemeral=True)
            return

        if self.ad.checkExist(self.lNum, btnInteraction.user.id):
            await btnInteraction.response.send_message("이미 줄 스신거 같은데...", ephemeral=True)
            return

        start_time = int(time.time())

        data = {
             "linenumber": self.lNum,
             "entryuserID": btnInteraction.user.id,
             "entryuserName": btnInteraction.user.display_name,
             "entrytime": f'{datetime.datetime.fromtimestamp(start_time)}'
        }

        self.ad.push(data, 'entrylist')
        lg.info(f"{btnInteraction.user.display_name} joined {self.ebdIntr.user.display_name}'s {self.prize} line.")
        await btnInteraction.response.send_message("줄 서기 완료!", ephemeral=True)


    # Exit from draw
    @discord.ui.button(label="줄 나가기", style=discord.ButtonStyle.red, custom_id='exit')
    async def exitEntry(self, btnInteraction: discord.Interaction, button: discord.ui.Button):

        if self.ebdIntr.user.id == btnInteraction.user.id:
            await btnInteraction.response.send_message("줄 세운 사람이 줄에서 빠지는게 가능할까?", ephemeral=True)
            return

        if not self.ad.checkExist(self.lNum, btnInteraction.user.id):
            await btnInteraction.response.send_message("줄을 안섰는데 빠질 수 있을까...", ephemeral=True)
            return

        self.ad.delete(self.lNum, btnInteraction.user.id)
        lg.info(f"{btnInteraction.user.display_name} left {self.ebdIntr.user.display_name}'s {self.prize} line.")
        await btnInteraction.response.send_message("줄 나가기 완료!", ephemeral=True)


    # Print entryList
    @discord.ui.button(label="참가자 확인", style=discord.ButtonStyle.grey, custom_id='checkEntry')
    async def printEntry(self, btnInteraction: discord.Interaction, button: discord.ui.Button):

        res = self.ad.getEntryUsers(self.lNum)

        if not res:
            await btnInteraction.response.send_message("참가자가 없어요.", ephemeral=True)
            return

        participants = [f'<@{entry["entryuserID"]}>' for entry in res]
        participant_list = '\n'.join(participants)

        await btnInteraction.response.send_message(f"{self.ebdIntr.user.display_name}의 {self.prize} 줄의 참가자:\n{participant_list}", ephemeral=True)
        lg.info(f"{btnInteraction.user.display_name} requested to see the list of participants in {self.ebdIntr.user.display_name}'s {self.prize} line.")