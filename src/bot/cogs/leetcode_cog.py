import urllib.parse
import os

import aiohttp
import discord
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

async def setup(bot: commands.Bot):
    await bot.add_cog(LeetCodeCog(bot))