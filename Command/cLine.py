import discord
import asyncio
import datetime
import random
import time

from Buttons.LineBtn import Entry as ent
from Utils.Log import Logger
from Utils import checkover as co

from Database.dynamo import awsDynamo

async def executeLine(interaction, prize: str, hour, min, sec):

    # Initialize DB class
    database = awsDynamo()
    line_number = database.getLineNumber() + 1
    
    # Calculate total time from user input
    total_time = 3600 * hour + 60 * min + sec

    # if total_time < 300:
    #     await interaction.response.send_message('The time is too short. Please set the time to be at least 5 minutes.', ephemeral=True)
    #     return

    start_time = int(time.time())
    deadline = start_time + total_time
    
    # Create countdown Task
    countdown_task = asyncio.create_task(co.checkOver(deadline))

    # Create button View
    button_view = ent(interaction, prize, line_number)

    # Create initial Embed
    embed = discord.Embed(title=f'Line #{line_number}', timestamp=datetime.datetime.now(), colour=discord.Colour.random())
    embed.add_field(name='상품', value=prize, inline=True)
    embed.add_field(name='마감 까지 남은 시간', value=f"<t:{deadline}:R>", inline=False)
    embed.add_field(name='줄 세운 사람', value=f'<@{interaction.user.id}>')

    # Prepare data before end
    line_data = {
        "LinePK": 'Joul',
        "linenumber": line_number,
        "createtime": f'{datetime.datetime.fromtimestamp(start_time)}',
        "creatorID": f'{interaction.user.id}',
        "creatorName": f'{interaction.user.display_name}',
        "endtime": f'{datetime.datetime.fromtimestamp(deadline)}',
        "isEntryEnd": 0,
        "prize": prize,
        "winnerID": 0,
        "winnerName": 'None'
    }
    
    # Push item to Table
    database.push(line_data, 'linelists')
    
    # Create Thread under channel where command input
    thread = await interaction.channel.create_thread(name=f"{interaction.user.display_name}'s {prize} line", reason='Line', type=discord.ChannelType.public_thread)
    thread_message = await thread.send(embed=embed, view=button_view)

    # Send feedback to user
    await interaction.response.send_message('줄 생성 완료! 생성된 스레드를 확인하세요.')
    Logger.info(f"{interaction.user.display_name}'s {prize} Line has been created.")

    # Wait for task to end
    is_task_end = await countdown_task

    if is_task_end:
        await handle_task_end(database, interaction, thread, thread_message, embed, prize, deadline, line_number)
    else:
        await handle_input_error(database, interaction, thread, thread_message, embed, prize, deadline, line_number)

async def handle_task_end(database, interaction, thread, thread_message, embed, prize, deadline, line_number):
    participants = database.getEntryUsers(line_number)
    if not participants:
        await handle_no_participants(database, interaction, thread, thread_message, embed, prize, deadline, line_number)
    else:                        
        await handle_winner(database, interaction, thread, thread_message, embed, prize, deadline, line_number, participants)

async def handle_no_participants(database, interaction, thread, thread_message, embed, prize, deadline, line_number):
    # Update result
    database.update(1, 0, 'No Entry', line_number)

    # Feedback to Thread and remove view from embed
    update_embed(embed, prize, deadline, interaction.user.id, '주작 결과', '참가자가 없었어요.')
    Logger.info(f"There were no participants in {interaction.user.display_name}'s {prize} Line.")
    await thread_message.edit(embed=embed, view=None)

    await thread.send(f'<@{interaction.user.id}> \n 참가자가 없었어요.')

async def handle_winner(database, interaction, thread, thread_message, embed, prize, deadline, line_number, participants):
    # Get winner and edit embed
    winner = random.choice(participants)
    winner_id = winner['entryuserID']
    winner_name = winner['entryuserName']

    # Update data
    database.update(1, f'{winner_id}', f'{winner_name}', line_number)

    # Feedback to Thread and remove view from embed
    update_embed(embed, prize, deadline, interaction.user.id, '주작 결과', f'<@{winner_id}>')
    Logger.info(f"{winner_name} gets {interaction.user.display_name}'s {prize}!")
    await thread_message.edit(embed=embed, view=None)

    await thread.send(f'<@{winner_id}>, <@{interaction.user.id}> \n 추첨 결과를 확인하세요!')

async def handle_input_error(database, interaction, thread, thread_message, embed, prize, deadline, line_number):
    # Update status
    database.update(1, 0, 'Input Error', line_number)

    # Feedback to Thread and remove view from embed
    update_embed(embed, prize, deadline, interaction.user.id, 'Input error occurred!', '마감 시간 입력이 잘못됐을 수 있습니다.')
    Logger.error("Deadline Input Error.")

    await thread_message.edit(embed=embed, view=None)
    await thread.send(f'<@{interaction.user.id}> \n 마감 시간 입력이 정상적이었는지 확인해 주세요.')

def update_embed(embed, prize, deadline, user_id, field_name, field_value):
    embed.clear_fields()
    embed.add_field(name='상품', value=prize, inline=True)
    embed.add_field(name='마감시간', value=f"<t:{deadline}:F>", inline=False)
    embed.add_field(name='줄 세운 사람', value=f'<@{user_id}>')
    embed.add_field(name=field_name, inline=False, value=field_value)