import inject
import logging
from tengi.command.command_handler import *
from tengi import telegram_bot_utils

from liker.state.enabled_channels import EnabledChannels
from liker.enabling_manager import EnablingManager

logger = logging.getLogger(__file__)


def parse_reactions_with_counts(reactions_args: list):
    """
    Parse reactions list with optional counts.
    Input:  ['❤', '100', '👍', '50']  or  ['❤', '👍', '😡']
    Output: [('❤', 100), ('👍', 50)]  or  [('❤', 0), ('👍', 0), ('😡', 0)]
    """
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
    """Extract message_id from https://t.me/channel/19 -> 19"""
    parts = post_link.rstrip('/').split('/')
    return int(parts[-1])


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
            channel_id = context.get_mandatory_arg('channel_id')
            reactions_args = context.get_mandatory_arg('reactions')
            post_link = context.get_arg('post_link')  # optional

            if not telegram_bot_utils.is_proper_chat_id(channel_id):
                context.reply('channel_id should be a number or start from @',
                              log_level=logging.INFO)
                return

            # Parse reactions with optional counts
            reactions_with_counts = parse_reactions_with_counts(reactions_args)
            reactions_only = [r for r, _ in reactions_with_counts]
            has_counts = any(c > 0 for _, c in reactions_with_counts)

            if post_link:
                # ── Apply reactions to a SPECIFIC post ──
                try:
                    message_id = extract_message_id_from_link(post_link)
                except (ValueError, IndexError):
                    context.reply('Invalid post_link format. Use: https://t.me/channel/19',
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
                # ── Set default reactions for ALL future posts ──
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

