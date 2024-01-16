from datetime import datetime
import discord
import pytz

class Response:

    @staticmethod
    def create_embed(title, description, color):
        embed = discord.Embed(
            title = title,
            description = description,
            colour = color,
            timestamp=pytz.utc.localize(datetime.utcnow())
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