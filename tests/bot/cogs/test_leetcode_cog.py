import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord.ext import commands

import main
from src.bot.cogs.leetcode_cog import LeetCodeCog


@pytest.fixture
def cog():
    bot = MagicMock(spec=commands.Bot)
    return LeetCodeCog(bot=bot)


def test_pattern_button_return_url(cog):
    button = cog.PatternButton(label="Two Pointers")

    assert (
        button.return_url("Two Pointers")
        == "https://leetcode-wrapper.onrender.com/api/problems?pattern=two-pointers"
    )


@pytest.mark.asyncio
async def test_pattern_button_callback_formats_problem_data(cog):
    button = cog.PatternButton(label="Two Pointers")
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()

    await button.callback(interaction)

    interaction.response.send_message.assert_awaited_once()
    sent_message = interaction.response.send_message.await_args.args[0]
    assert sent_message == "Select a difficulty for Two Pointers:"
    assert isinstance(interaction.response.send_message.await_args.kwargs["view"], discord.ui.View)

    difficulty_buttons = interaction.response.send_message.await_args.kwargs["view"].children
    assert [button.label for button in difficulty_buttons] == ["Easy", "Medium", "Hard"]

    easy_button = next(button for button in difficulty_buttons if button.label == "Easy")

    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()

    fake_response = MagicMock()
    fake_response.status = 200
    fake_response.json = AsyncMock(
        return_value={
            "data": [
                {"title": "Two Sum", "difficulty": "Easy", "titleSlug": "two-sum"},
                {"title": "Valid Anagram", "difficulty": "Medium", "titleSlug": "valid-anagram"},
                {"title": "Median of Two Sorted Arrays", "difficulty": "Hard", "titleSlug": "median-of-two-sorted-arrays"},
            ]
        }
    )

    mock_get_context = MagicMock()
    mock_get_context.__aenter__ = AsyncMock(return_value=fake_response)
    mock_get_context.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=mock_get_context)

    mock_client_session = MagicMock()
    mock_client_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_client_session.__aexit__ = AsyncMock(return_value=False)

    with patch("src.bot.cogs.leetcode_cog.aiohttp.ClientSession", return_value=mock_client_session):
        await easy_button.callback(interaction)

    interaction.followup.send.assert_awaited_once()
    sent_message = interaction.followup.send.await_args.args[0]
    assert "**Problems for Two Pointers (Easy, Top 20):**" in sent_message
    assert "Two Sum" in sent_message
    assert "Valid Anagram" not in sent_message
    assert "Median of Two Sorted Arrays" not in sent_message


@pytest.mark.asyncio
async def test_patterns_command_sends_pattern_menu(cog):
    mock_ctx = AsyncMock()
    mock_ctx.author.name = "TestUser"

    await cog.leetcode_patterns.callback(cog, mock_ctx)

    mock_ctx.send.assert_awaited_once()
    message, kwargs = mock_ctx.send.await_args.args[0], mock_ctx.send.await_args.kwargs
    assert message == "Select a pattern to view problems for:"
    assert isinstance(kwargs["view"], discord.ui.View)
    assert len(kwargs["view"].children) <= 25

    pattern_labels = [
        child.label
        for child in kwargs["view"].children
        if hasattr(child, "label") and child.label not in {"Next", "Previous"}
    ]

    assert pattern_labels == [str(label) for label in cog.pattern_service.list_patterns()[:23]]
    assert any(getattr(child, "label", None) == "Next" for child in kwargs["view"].children)


@pytest.mark.asyncio
async def test_patterns_command_is_registered_on_bot():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
    await bot.add_cog(LeetCodeCog(bot))

    command = bot.get_command("patterns")

    assert command is not None
    assert command.name == "patterns"


def test_cron_endpoint_rejects_missing_secret(monkeypatch):
    monkeypatch.setenv("DAILY_LEETCODE_CHANNEL_ID", "123456")
    monkeypatch.setenv("CRON_SECRET", "super-secret")
    monkeypatch.setattr(main.bot, "is_ready", lambda: True)

    response = main.app.test_client().get("/cron/daily-leetcode")

    assert response.status_code == 403
    assert response.json["status"] == "error"


def test_cron_endpoint_posts_daily_challenge(monkeypatch):
    monkeypatch.setenv("DAILY_LEETCODE_CHANNEL_ID", "123456")
    monkeypatch.setenv("CRON_SECRET", "super-secret")
    monkeypatch.setattr(main.bot, "is_ready", lambda: True)
    try:
        main.bot.loop = asyncio.get_running_loop()
    except RuntimeError:
        main.bot.loop = None

    fake_cog = MagicMock()
    fake_cog.fetch_daily_challenge_data = AsyncMock(
        return_value={"title": "Two Sum", "difficulty": "Easy", "titleSlug": "two-sum", "url": "https://leetcode.com/problems/two-sum/"}
    )
    fake_cog.post_daily_challenge_to_channel = AsyncMock(return_value=True)
    monkeypatch.setattr(main.bot, "get_cog", lambda name: fake_cog)

    def fake_run_coroutine_threadsafe(coro, loop):
        mock_task = MagicMock()
        mock_task.result.return_value = asyncio.run(coro)
        return mock_task

    monkeypatch.setattr(main.asyncio, "run_coroutine_threadsafe", fake_run_coroutine_threadsafe)

    mock_redis = MagicMock()
    monkeypatch.setattr(main, "get_redis_client", lambda: mock_redis)

    response = main.app.test_client().get("/cron/daily-leetcode?token=super-secret")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    fake_cog.post_daily_challenge_to_channel.assert_awaited_once_with(123456)
    mock_redis.set.assert_called_once()
