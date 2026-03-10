import os
import json

config = {
    "protected_vars": [
        "hash_salt",
        "hash_trim_bytes",
        "admin_password",
        "remembered_passwords"
    ],
    "hash_salt": os.environ.get("HASH_SALT", ""),
    "hash_bytes": int(os.environ.get("HASH_BYTES", "10")),
    "bot_token": os.environ.get("BOT_TOKEN", ""),
    "use_telegram_user_api": os.environ.get("USE_TELEGRAM_USER_API", "false").lower() == "true",
    "use_native_reactions": os.environ.get("USE_NATIVE_REACTIONS", "false").lower() == "true",
    "telegram_api_session": os.environ.get("TELEGRAM_API_SESSION", "liker"),
    "telegram_api_id": int(os.environ.get("TELEGRAM_API_ID", "0")),
    "telegram_api_hash": os.environ.get("TELEGRAM_API_HASH", ""),
    "admin_password": os.environ.get("ADMIN_PASSWORD", ""),
    "remembered_passwords": {},
    "enable_only_for": [],
    "last_reactions": int(os.environ.get("LAST_REACTIONS", "1000000")),
    "last_reactions_save_seconds": int(os.environ.get("LAST_REACTIONS_SAVE_SECONDS", "100")),
    "channel_rate_per_minute": int(os.environ.get("CHANNEL_RATE_PER_MINUTE", "20")),
    "channel_rate_min_seconds": int(os.environ.get("CHANNEL_RATE_MIN_SECONDS", "1")),
    "global_rate_per_second": int(os.environ.get("GLOBAL_RATE_PER_SECOND", "30")),
    "reply_markup_trail": int(os.environ.get("REPLY_MARKUP_TRAIL", "100")),
    "comment_trail": int(os.environ.get("COMMENT_TRAIL", "100")),
    "channel_state_save_seconds": int(os.environ.get("CHANNEL_STATE_SAVE_SECONDS", "2")),
    "response_start": os.environ.get("RESPONSE_START", "Liker bot allows you to add reactions (likes, etc.) to channel posts. Give Liker bot an admin permission to edit posts in your channel. Use /help to get more information."),
    "response_help": os.environ.get("RESPONSE_HELP", "Give Liker bot an admin permission to edit posts in your channel. Use /set_reactions command to customize channel post reactions"),
    "response_reaction_added": os.environ.get("RESPONSE_REACTION_ADDED", "{}"),
    "response_reaction_removed": os.environ.get("RESPONSE_REACTION_REMOVED", "{} removed"),
    "response_command_parser_error": os.environ.get("RESPONSE_COMMAND_PARSER_ERROR", "Unknown or incomplete command {command}"),
    "response_unknown_command": os.environ.get("RESPONSE_UNKNOWN_COMMAND", "Unknown or incomplete command {command}")
}

os.makedirs("data", exist_ok=True)

with open("data/config.json", "w") as f:
    json.dump(config, f, indent=2)

print("✅ config.json generated successfully from environment variables!")
