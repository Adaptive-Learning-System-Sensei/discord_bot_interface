import json
import os
import urllib.parse

import aiohttp
import discord
import redis
from discord.ext import commands
from discord.ui.button import Button

from src.core.domains.leetcode.patterns import Patterns
from src.utils.python_logging import setup_logging

LEETCODE_WRAPPER = os.getenv("LEETCODE_WRAPPER", "https://leetcode-wrapper.onrender.com")

logger = setup_logging()


class LeetCodeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.pattern_service = Patterns()


    """
    A custom class for creating pattern buttons.
    """
    class PatternButton(Button):
        def __init__(self, label: str):
            super().__init__(label=label, style=discord.ButtonStyle.primary)
            self.pattern_name = label

        def return_url(self, pattern_name: str) -> str:
            """
            Returns the URL for the given pattern name.
            """
            formatted_pattern = pattern_name.lower().replace(" ", "-")
            encoded_pattern = urllib.parse.quote(formatted_pattern)
            return f"{LEETCODE_WRAPPER}/api/problems?pattern={encoded_pattern}"

        async def callback(self, interaction: discord.Interaction):
            difficulty_view = LeetCodeCog.DifficultyMenuView(self.pattern_name)
            await interaction.response.send_message(
                f"Select a difficulty for {self.pattern_name}:",
                view=difficulty_view,
                ephemeral=True,
            )

    class DifficultyButton(Button):
        def __init__(self, pattern_name: str, difficulty: str):
            super().__init__(label=difficulty, style=discord.ButtonStyle.secondary)
            self.pattern_name = pattern_name
            self.difficulty = difficulty

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            api_url = LeetCodeCog.PatternButton(label=self.pattern_name).return_url(self.pattern_name)

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url) as response:
                        if response.status != 200:
                            await interaction.followup.send(f"Failed to fetch data: HTTP {response.status}")
                            return

                        data = await response.json()

                problems_data = data.get("data", [])
                filtered_problems = [
                    problem
                    for problem in problems_data
                    if str(problem.get("difficulty", "Unknown")).lower() == self.difficulty.lower()
                ]

                if filtered_problems:
                    formatted_problems = []
                    for problem in filtered_problems[:20]:
                        title = problem.get("title", "Unknown")
                        problem_difficulty = problem.get("difficulty", "Unknown")
                        url = f"https://leetcode.com/problems/{problem.get('titleSlug')}/"
                        formatted_problems.append(f"- [{title}]({url}) ({problem_difficulty})")

                    problems_list = "\n".join(formatted_problems)
                    response_text = f"**Problems for {self.pattern_name} ({self.difficulty}, Top 20):**\n{problems_list}"
                    await interaction.followup.send(response_text[:2000])
                else:
                    await interaction.followup.send(
                        f"No problems found for {self.pattern_name} at difficulty {self.difficulty}."
                    )

            except Exception as e:
                logger.error(f"Error processing response for {self.pattern_name} ({self.difficulty}): {e}")
                await interaction.followup.send(
                    f"An error occurred while fetching problems for {self.pattern_name} ({self.difficulty})."
                )

    class DifficultyMenuView(discord.ui.View):
        def __init__(self, pattern_name: str):
            super().__init__(timeout=180)
            for difficulty in ["Easy", "Medium", "Hard"]:
                self.add_item(LeetCodeCog.DifficultyButton(pattern_name=pattern_name, difficulty=difficulty))

    class PatternMenuView(discord.ui.View):
        """
        A custom view for displaying a paginated menu of pattern buttons. Discord has a limit of 25 buttons per view, so this class handles pagination.
        """
        def __init__(self, patterns: list[str], page_size: int = 23):
            super().__init__(timeout=180)
            self.patterns = patterns
            self.page_size = page_size
            self.page = 0
            self.refresh()

        def refresh(self):
            self.clear_items()
            start = self.page * self.page_size
            end = start + self.page_size
            for label in self.patterns[start:end]:
                self.add_item(LeetCodeCog.PatternButton(label=str(label)))

            if self.page > 0:
                prev_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.secondary)
                prev_button.callback = self._go_to_previous_page
                self.add_item(prev_button)

            if end < len(self.patterns):
                next_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.secondary)
                next_button.callback = self._go_to_next_page
                self.add_item(next_button)

        async def _go_to_previous_page(self, interaction: discord.Interaction):
            if self.page > 0:
                self.page -= 1
                self.refresh()
            await interaction.response.edit_message(content="Select a pattern to view problems for:", view=self)

        async def _go_to_next_page(self, interaction: discord.Interaction):
            self.page += 1
            self.refresh()
            await interaction.response.edit_message(content="Select a pattern to view problems for:", view=self)

    @commands.command(name="patterns")
    async def leetcode_patterns(self, ctx: commands.Context):
        logger.info(f"Fetching LeetCode patterns for user: {ctx.author.name}")
        patterns_list: list = self.pattern_service.list_patterns()
        view = self.PatternMenuView(patterns_list)
        await ctx.send("Select a pattern to view problems for:", view=view)

    async def fetch_daily_challenge_data(self):
        api_url = f"{LEETCODE_WRAPPER}/api/daily"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Failed to fetch daily challenge: HTTP {response.status}")

                    data = await response.json()
                    daily_challenge = data.get("data", {})
                    title = daily_challenge.get("title", "Unknown")
                    difficulty = daily_challenge.get("difficulty", "Unknown")
                    title_slug = daily_challenge.get("titleSlug")
                    url = f"https://leetcode.com/problems/{title_slug}/" if title_slug else "https://leetcode.com"
                    return {
                        "title": title,
                        "difficulty": difficulty,
                        "titleSlug": title_slug,
                        "url": url,
                    }
        except Exception as e:
            logger.error(f"Error fetching daily challenge: {e}")
            return None

    async def fetch_daily_challenge_embed(self):
        challenge = await self.fetch_daily_challenge_data()
        if challenge is None:
            return None

        embed = discord.Embed(
            title="LeetCode Daily Challenge",
            description=f"[{challenge['title']}]({challenge['url']})",
            color=discord.Color.gold(),
            url=challenge["url"],
        )
        embed.add_field(name="Difficulty", value=challenge["difficulty"], inline=True)
        embed.set_thumbnail(url="https://leetcode.com/static/images/LeetCode_logo_rvs.png")
        return embed

    async def store_daily_challenge_in_redis(self, challenge: dict | None = None):
        if challenge is None:
            challenge = await self.fetch_daily_challenge_data()

        if challenge is None:
            return False

        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            client = redis.Redis.from_url(redis_url, decode_responses=True)
            client.set("daily_leetcode:current", json.dumps(challenge), ex=60 * 60 * 24 * 2)
            return True
        except Exception as exc:
            logger.error(f"Failed to persist daily challenge to Redis: {exc}")
            return False

    async def post_daily_challenge_to_channel(self, channel_id: int | None = None):
        if channel_id is None:
            channel_id = int(os.getenv("DAILY_LEETCODE_CHANNEL_ID", "0"))

        if not channel_id:
            raise ValueError("DAILY_LEETCODE_CHANNEL_ID is not set")

        channel = self.bot.get_channel(channel_id)
        if channel is None:
            channel = await self.bot.fetch_channel(channel_id)

        challenge = await self.fetch_daily_challenge_data()
        if challenge is None:
            return False

        await self.store_daily_challenge_in_redis(challenge)

        embed = discord.Embed(
            title="LeetCode Daily Challenge",
            description=f"[{challenge['title']}]({challenge['url']})",
            color=discord.Color.gold(),
            url=challenge["url"],
        )
        embed.add_field(name="Difficulty", value=challenge["difficulty"], inline=True)
        embed.set_thumbnail(url="https://leetcode.com/static/images/LeetCode_logo_rvs.png")

        await channel.send(embed=embed)
        return True

    @commands.command(name="daily")
    async def leetcode_daily(self, ctx: commands.Context):
        logger.info(f"Fetching LeetCode daily challenge for user: {ctx.author.name}")
        embed = await self.fetch_daily_challenge_embed()
        if embed is None:
            await ctx.send("An error occurred while fetching the daily challenge.")
            return

        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(LeetCodeCog(bot))