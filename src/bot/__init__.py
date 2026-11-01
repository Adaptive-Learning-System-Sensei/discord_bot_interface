import os
from discord.ext import commands as discord_commands

class myBot(discord_commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        await self.load_cogs()

    async def load_cogs(self):
        cog_package = [
            "src.bot.cogs.greetings_cog",
            "src.bot.cogs.leetcode_cog"]

        for cog_package in cog_package:
            try:
                await self.load_extension(cog_package)
                print(f"Successfully loaded {cog_package}")
            except Exception as e:
                print(f"Failed to load {cog_package}: {e}")