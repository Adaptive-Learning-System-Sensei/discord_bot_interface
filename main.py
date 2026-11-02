import asyncio
import json
import os
from threading import Thread

import discord
import redis
from flask import Flask, jsonify, request
from discord.ext import commands as discord_commands

from src.bot import myBot

app = Flask(__name__)


def create_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    return myBot(command_prefix=discord_commands.when_mentioned_or("!"), intents=intents)


bot = create_bot()


def get_redis_client():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.Redis.from_url(redis_url, decode_responses=True)


def get_provided_secret():
    return (
        request.args.get("token")
        or request.headers.get("X-Cron-Secret")
        or request.headers.get("Authorization", "").replace("Bearer ", "")
    )


@app.route("/keepalive", methods=["GET", "POST"])
@app.route("/health", methods=["GET", "POST"])
def keepalive():
    cron_secret = os.getenv("CRON_SECRET")
    provided_secret = get_provided_secret()
    if cron_secret and provided_secret != cron_secret:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    return jsonify({"status": "ok", "message": "Server is alive"}), 200


@app.route("/cron/daily-leetcode", methods=["GET", "POST"])
def cron_daily_leetcode():
    channel_id = os.getenv("DAILY_LEETCODE_CHANNEL_ID")
    if not channel_id:
        return jsonify({"status": "error", "message": "DAILY_LEETCODE_CHANNEL_ID is not set"}), 400

    if channel_id == "YOUR_DISCORD_CHANNEL_ID" or channel_id.strip() == "":
        return jsonify({
            "status": "error",
            "message": "DAILY_LEETCODE_CHANNEL_ID is still a placeholder. Set it to a real Discord channel ID."
        }), 400

    try:
        parsed_channel_id = int(channel_id)
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "DAILY_LEETCODE_CHANNEL_ID must be a numeric Discord channel ID."
        }), 400

    cron_secret = os.getenv("CRON_SECRET")
    provided_secret = get_provided_secret()
    if cron_secret and provided_secret != cron_secret:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    if not bot.is_ready():
        return jsonify({"status": "error", "message": "Bot is not ready yet"}), 503

    async def _post():
        cog = bot.get_cog("LeetCodeCog")
        if cog is None:
            return False

        challenge = await cog.fetch_daily_challenge_data()
        if challenge is None:
            return False

        try:
            get_redis_client().set("daily_leetcode:current", json.dumps(challenge), ex=60 * 60 * 24 * 2)
        except Exception:
            pass

        return await cog.post_daily_challenge_to_channel(parsed_channel_id)

    task = asyncio.run_coroutine_threadsafe(_post(), bot.loop)
    result = task.result(timeout=30)
    if result:
        return jsonify({"status": "ok", "message": "Daily challenge posted"}), 200
    return jsonify({"status": "error", "message": "Unable to post daily challenge"}), 500


def start_webhook_server():
    app.run(host="0.0.0.0", port=int(os.getenv("WEBHOOK_PORT", "8081")), debug=False, use_reloader=False)


def main() -> None:
    print("Starting the bot...")
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN environment variable is not set")

    webhook_thread = Thread(target=start_webhook_server, daemon=True)
    webhook_thread.start()
    bot.run(token)


if __name__ == "__main__":
    main()
