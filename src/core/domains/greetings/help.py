class Help_Service:
    commands_description = {
        "hello": "Greet the bot.",
        "help": "Show this help message.",
        "patterns": "Get LeetCode problem patterns based on difficulties.",
    }
    def generate_help_response(self) -> str:
        return "Here are the available commands:\n" + "\n".join(
            f"**{command}**: {description}" for command, description in self.commands_description.items()
        )