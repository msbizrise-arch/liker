import inject
import logging
import re
from tengi.command.command_handler import *
from tengi import telegram_bot_utils

from liker.state.enabled_channels import EnabledChannels
from liker.enabling_manager import EnablingManager

logger = logging.getLogger(__file__)


def parse_new_format(raw_text: str) -> dict:
    """
    Parse command in format:
    /set_reactions — channel_id: VALUE — post_link: VALUE — reactions: ❤ 100
    
    Supports both — (em dash) and -- (double dash)
    Supports params with or without colon
    """
    # Normalize: replace em dash / en dash variants with a unique separator
    text = raw_text \
        .replace('\u2014', '|||') \
        .replace('\u2013', '|||') \
        .replace('\u2012', '|||')

    # Remove the command itself
    text = re.sub(r'^/\S+\s*', '', text).strip()

    args = {}
    # Split by ||| separator
    parts = [p.strip() for p in text.split('|||') if p.strip()]

    for part in parts:
        # Each part: "channel_id: VALUE" or "channel_id VALUE"
        # Split on first space or colon+space
        match = re.match(r'^(\w+)\s*:?\s+(.*)', part, re.DOTALL)
        if match:
            key = match.group(1).strip().lower()
            value = match.group(2).strip()
            args[key] = value

    return args


def parse_reactions_and_count(reactions_str: str):
    """
    Parse reactions string — only ONE emoji supported.
    Input: "❤ 100" or "❤"
    Output: (emoji, count)
    """
    tokens = reactions_str.strip().split()
    emoji = None
    count = 0

    for token in tokens:
        if token.isdigit():
            count = int(token)
        elif not token.lower() in {'times', 'time', 'x', 'baar', 'bar'}:
            emoji = token  # take the emoji

    return (emoji, count) if emoji else None


def extract_message_id_from_link(post_link: str) -> int:
    parts = post_link.rstrip('/').split('/')
    return int(parts[-1])


class CommandHandlerSetReactions(CommandHandler):
    enabled_channels = inject.attr(EnabledChannels)
    enabling_manager = inject.attr(EnablingManager)

    def get_cards(self) -> Iterable[CommandCard]:
        return [CommandCard(command_str='/set_reactions',
                            description='Set reactions for channel or a specific post',
                            is_admin=False),
                ]

    def handle(self, context: CommandContext):
        if context.command == '/set_reactions':
            raw_text = context.sender_message.text or ''
            args = parse_new_format(raw_text)

            channel_id = args.get('channel_id')
            reactions_str = args.get('reactions')
            post_link = args.get('post_link')

            if not channel_id:
                context.reply(
                    '❌ channel_id missing!\n\nFormat:\n'
                    '/set_reactions — channel_id: -100XXXXXXXXX — reactions: ❤ 100',
                    log_level=logging.INFO)
                return

            if not reactions_str:
                context.reply(
                    '❌ reactions missing!\n\nFormat:\n'
                    '/set_reactions — channel_id: -100XXXXXXXXX — reactions: ❤ 100',
                    log_level=logging.INFO)
                return

            if not telegram_bot_utils.is_proper_chat_id(channel_id):
                context.reply('❌ channel_id should be a number like -1001234567890',
                              log_level=logging.INFO)
                return

            parsed = parse_reactions_and_count(reactions_str)
            if not parsed:
                context.reply('❌ Invalid reactions format. Example: ❤ 100',
                              log_level=logging.INFO)
                return

            emoji, count = parsed

            if post_link:
                # ── Apply to specific post ──
                try:
                    message_id = extract_message_id_from_link(post_link)
                except (ValueError, IndexError):
                    context.reply('❌ Invalid post_link. Use: https://t.me/yourchannel/19',
                                  log_level=logging.WARNING)
                    return

                success = self.enabling_manager.apply_reactions_to_post(
                    channel_id=channel_id,
                    message_id=message_id,
                    reactions_with_counts=[(emoji, count)],
                    reply_context=context,
                    sender_id_to_check=context.sender_message.from_user.id
                )
                if success:
                    context.reply(
                        f'✅ Done! {emoji} x{count} applied to post {message_id} in {channel_id}',
                        log_level=logging.INFO
                    )
            else:
                # ── Set default for all future posts ──
                set_successfully = self.enabling_manager.try_set_reactions(
                    channel_id=channel_id,
                    reactions=[emoji],
                    reply_context=context,
                    sender_id_to_check=context.sender_message.from_user.id
                )
                if set_successfully:
                    context.reply(
                        f'✅ Default reaction set to {emoji} for channel {channel_id}\n'
                        f'Will be applied to all new posts.',
                        log_level=logging.INFO
                    )
        else:
            raise ValueError(f'Unhandled command: {context.command}')
