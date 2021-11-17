from examples.helpers import clean_mentioned_role, get_role_from_id
from src.EmojiHandler import MultiEmoji
from src.ReactableMenu import ReactableMenu


class RoleMenu(ReactableMenu):

    def __init__(self, **kwargs):
        kwargs["add_func"] = self.give_role_event
        kwargs["remove_func"] = self.remove_role_event
        super().__init__(**kwargs)

    async def give_role_event(self, payload):
        emoji_reaction = MultiEmoji(payload.emoji)

        if emoji_reaction.emoji_id in self.options:
            role_id = clean_mentioned_role(self.options.get(emoji_reaction.emoji_id).value)
        else:
            role_id = 0

        if not role_id:
            await self.message.remove_reaction(payload.emoji, payload.member)
            return False

        role_to_add = get_role_from_id(self.message.guild, role_id)
        await payload.member.add_roles(role_to_add, reason="Added with role reaction menu")
        return True

    async def remove_role_event(self, payload):
        emoji_reaction = MultiEmoji(payload.emoji)
        member = self.message.guild.get_member(payload.user_id)
        if member is None:
            member = await self.message.guild.fetch_member(payload.user_id)

        if emoji_reaction.emoji_id in self.options:
            role_id = clean_mentioned_role(self.options.get(emoji_reaction.emoji_id).value)
        else:
            role_id = 0

        if not role_id:
            return False

        role_to_remove = get_role_from_id(self.message.guild, role_id)
        await member.remove_roles(role_to_remove, reason="Removed with role reaction menu")
        return True
