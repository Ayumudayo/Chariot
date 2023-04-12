import discord

from Utils.Log import Logger as lg

# Button class
class Entry(discord.ui.View):
    def __init__(self, ebdInteraction):
        super().__init__(timeout=None)
        self.value = None
        self.ebdIntr = ebdInteraction
        self.entryList = []
    
    # Entry a draw
    @discord.ui.button(label="줄 서기", style=discord.ButtonStyle.green, custom_id='entry')
    async def doEntry(self, btnInteraction: discord.Interaction, button: discord.ui.Button):
        if(self.ebdIntr.user.id != btnInteraction.user.id):
            # Append user info to entryList in Tuple
            if((btnInteraction.user.display_name, btnInteraction.user.id) not in self.entryList):
                self.entryList.append((btnInteraction.user.display_name, btnInteraction.user.id))
                lg.writeLog(1, f"{btnInteraction.user.display_name} Entry at {self.ebdIntr.user.display_name}'s Line.")
                await btnInteraction.response.send_message("줄 서기 완료!", ephemeral=True)
            else:
                await btnInteraction.response.send_message("이미 줄 스신거 같은데...", ephemeral=True)
        else:
            await btnInteraction.response.send_message("줄 세운 사람이 줄 스면 어쩌나?", ephemeral=True)


    # Print entryList
    @discord.ui.button(label="참가자 확인", style=discord.ButtonStyle.grey, custom_id='checkEntry')
    async def printEntry(self, btnInteraction: discord.Interaction, button: discord.ui.Button):
        tmpList = []

        lg.writeLog(1, f"{btnInteraction.user.display_name} request List Print.")

        if(len(self.entryList) != 0):
            for tmp in self.entryList:
                # Get each user's display name
                tmpList.append(tmp[0])

            tmpStr = '\n'.join(tmpList)

            # Print users' display name
            await btnInteraction.response.send_message(tmpStr, ephemeral=True)
        else:
            await btnInteraction.response.send_message("참가자가 없어요.", ephemeral=True)
      
        lg.writeLog(1, "List printed.")