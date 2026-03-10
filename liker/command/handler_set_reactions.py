import inject
import logging
from tengi.command.command_handler import *
from tengi import telegram_bot_utils

from liker.state.enabled_channels import EnabledChannels
from liker.enabling_manager import EnablingManager

logger = logging.getLogger(__file__)


def parse_reactions_with_counts(reactions_args: list):
    result = []
    i = 0
    while i < len(reactions_args):
        emoji = reactions_args[i]
        count = 0
        if i + 1 < len(reactions_args):
            try:
                count = int(reactions_args[i + 1])
                i += 2
            except ValueError:
                i += 1
        else:
            i += 1
        result.append((emoji, count))
    return result


def extract_message_id_from_link(post_link: str) -> int:
    parts = post_link.rstrip('/').split('/')
    return int(parts[-1])


def parse_raw_args(raw_text: str) -> dict:
    """
    Manually parse command args from raw text.
    Fixes em dash (—) and en dash (–) → -- before parsing.
    """
    # Fix all dash variants Telegram auto-converts
    fixed = raw_text \
        .replace('\u2014', '--') \
        .replace('\u2013', '--') \
        .replace('\u2012', '--')

    args = {}
    import shlex
    try:
        tokens = shlex.split(fixed)
    except ValueError:
        tokens = fixed.split()

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.startswith('--'):
            key = token[2:]
            values = []
            i += 1
            while i < len(tokens) and not tokens[i].startswith('--'):
                values.append(tokens[i])
                i += 1
            args[key] = values if len(values) > 1 else (values[0] if values else True)
        else:
            i += 1
    return args


class CommandHandlerSetReactions(CommandHandler):
    enabled_channels = inject.attr(EnabledChannels)
    enabling_manager = inject.attr(EnablingManager)

    def get_cards(self) -> Iterable[CommandCard]:
        return [CommandCard(command_str='/set_reactions',
                            description='Set reactions for channel or a specific post with counts',
                            is_admin=False),
                ]

    def handle(self, context: CommandContext):
        if context.command == '/set_reactions':

            # ── Parse from raw message text to fix em dash issue ──
            raw_text = context.sender_message.text or ''
            raw_args = parse_raw_args(raw_text)

            channel_id = raw_args.get('channel_id')
            reactions_raw = raw_args.get('reactions')
            post_link = raw_args.get('post_link')

            if not channel_id:
                context.reply('Missing --channel_id', log_level=logging.INFO)
                return
            if not reactions_raw:
                context.reply('Missing --reactions', log_level=logging.INFO)
                return

            # reactions_raw can be str or list
            if isinstance(reactions_raw, str):
                reactions_raw = [reactions_raw]

            if not telegram_bot_utils.is_proper_chat_id(channel_id):
                context.reply('channel_id should be a number or start from @',
                              log_level=logging.INFO)
                return

            reactions_with_counts = parse_reactions_with_counts(reactions_raw)
            reactions_only = [r for r, _ in reactions_with_counts]

            if post_link:
                # ── Apply to specific post ──
                if isinstance(post_link, list):
                    post_link = post_link[0]
                try:
                    message_id = extract_message_id_from_link(post_link)
                except (ValueError, IndexError):
                    context.reply('Invalid post_link. Use: https://t.me/channel/19',
                                  log_level=logging.WARNING)
                    return

                success = self.enabling_manager.apply_reactions_to_post(
                    channel_id=channel_id,
                    message_id=message_id,
                    reactions_with_counts=reactions_with_counts,
                    reply_context=context,
                    sender_id_to_check=context.sender_message.from_user.id
                )
                if success:
                    counts_str = ', '.join(
                        f'{r} x{c}' if c > 0 else r
                        for r, c in reactions_with_counts
                    )
                    context.reply(
                        f'✅ Reactions applied to post {message_id} in {channel_id}:\n{counts_str}',
                        log_level=logging.INFO
                    )
            else:
                # ── Set default for all future posts ──
                set_successfully = self.enabling_manager.try_set_reactions(
                    channel_id=channel_id,
                    reactions=reactions_only,
                    reply_context=context,
                    sender_id_to_check=context.sender_message.from_user.id
                )
                if set_successfully:
                    context.reply(
                        f'✅ For {channel_id} reactions set to: {reactions_only}\nWill be applied to new messages.',
                        log_level=logging.INFO
                    )
        else:
            raise ValueError(f'Unhandled command: {context.command}')
