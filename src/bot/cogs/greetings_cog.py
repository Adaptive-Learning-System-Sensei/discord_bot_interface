import discord
from discord.ext import commands
from src.core.domains.greetings.service import GreetingsService
from src.core.domains.greetings.help import Help_Service

class GreetingsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Instantiate the service (or inject it)
        self.greetings_service = GreetingsService()
        self.help_service = Help_Service()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        channel = member.guild.system_channel
        if channel:
            # Delegate logic to the service layer
            message = self.greetings_service.generate_welcome_message(
                username=member.mention,
                server_name=member.guild.name
            )
            await channel.send(message)

    @commands.command(name="hello")
    async def hello_command(self, ctx: commands.Context) -> None:
        # Extract data, call service, return response
        response = self.greetings_service.generate_hello_response(ctx.author.mention)
        await ctx.send(response)

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context) -> None:
        # Extract data, call service, return response
        response = self.help_service.generate_help_response()
        await ctx.send(response)


async def setup(bot: commands.Bot):
    bot.remove_command("help")
    await bot.add_cog(GreetingsCog(bot))