from datetime import datetime
import discord
from pytz import timezone

class Response:

    @staticmethod
    def create_embed(title, description, color):
        embed = discord.Embed(
            title = title,
            description = description,
            colour = color,
            timestamp=datetime.utcnow()
        )
        return embed

    @staticmethod
    def general(title, content):
        return Response.create_embed(title, content, discord.Colour.dark_blue())

    @staticmethod
    def info(content):
        return Response.create_embed(":large_blue_diamond: **INFO**", content, discord.Colour.dark_blue())

    @staticmethod
    def error(content):
        return Response.create_embed(":warning: **ERROR**", content, discord.Colour.red())