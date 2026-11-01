import discord
import pytest
from discord.ext import commands
from unittest.mock import AsyncMock, MagicMock
from src.bot.cogs.greetings_cog import GreetingsCog

@pytest.fixture
def cog():
    # Mock the bot instance
    mock_bot = MagicMock()
    return GreetingsCog(bot=mock_bot)

@pytest.mark.asyncio
async def test_hello_command(cog):
    # 1. Arrange: Create a mock Context
    mock_ctx = AsyncMock()
    mock_ctx.author.mention = "@TestUser"
    
    # 2. Act: Use .callback to access the raw method. 
    # Because it is the raw method, we must explicitly pass 'cog' as 'self'.
    await cog.hello_command.callback(cog, mock_ctx)
    
    # 3. Assert: Check if ctx.send was awaited with the correct text
    mock_ctx.send.assert_awaited_once_with("Hello there, @TestUser!")

@pytest.mark.asyncio
async def test_on_member_join(cog):
    # 1. Arrange: Create a mock Member and a mock System Channel
    mock_member = MagicMock()
    mock_member.mention = "@NewUser"
    mock_member.guild.name = "TestGuild"
    
    # Create an AsyncMock for the channel because channel.send() is async
    mock_channel = AsyncMock()
    mock_member.guild.system_channel = mock_channel
    
    # 2. Act: Trigger the event listener
    await cog.on_member_join(mock_member)
    
    # 3. Assert: Check if the channel sent the correct welcome message
    expected_message = "Welcome to TestGuild, @NewUser! Please read the rules."
    mock_channel.send.assert_awaited_once_with(expected_message)


@pytest.mark.asyncio
async def test_help_command_registers_without_conflict():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
    bot.remove_command("help")
    await bot.add_cog(GreetingsCog(bot))

    command = bot.get_command("help")
    assert command is not None
    assert command.name == "help"