import ast
from abc import abstractmethod
from typing import Dict, List, Any, Union

from discord import Embed, Message, Emoji, PartialEmoji, TextChannel


class ReactableMenu:

    def __init__(self, add_func=None, remove_func=None, show_ids=True, auto_enable=False, **kwargs):
        self.react_add_func = add_func
        self.react_remove_func = remove_func
        self.id = kwargs.pop("id", None)
        self.message = kwargs.pop("message", None)
        self.options = kwargs.pop("options", {})
        self.enabled = kwargs.pop("enabled", False)
        self.embed = kwargs.pop("embed", Embed(**kwargs))
        self.show_ids = show_ids
        self.auto_enable = auto_enable

    def __str__(self) -> str:
        if self.embed is None:
            return ""
        __str = f"Title:{self.embed.title} | Description: {self.embed.description}"
        for emoji, descriptor in self.options.items():
            __str += f"\nEmoji: {emoji.name} | Descriptor: {descriptor}"
        return __str

    def __repr__(self):
        return repr(self.options)

    def __contains__(self, item):
        return self.__getitem__(item) is not None

    def __getitem__(self, item: Union[Emoji, PartialEmoji]):
        if isinstance(item, Emoji):
            return self.options.get(item)
        elif isinstance(item, PartialEmoji):
            emoji_id = item.id
            for emoji in self.options:
                if emoji.id == emoji_id:
                    return self.options.get(emoji)

        return None

    def to_dict(self):
        data = {
                "id": self.id,
                "guild_id": self.message.guild.id,
                "channel_id": self.message.channel.id,
                "options": self.serialize_options(),
                "enabled": self.enabled,
                "show_ids": self.show_ids
        }
        return data

    def serialize_options(self):
        data = {}
        for option in self.options:
            data[option.id] = {"descriptor": self.options.get(option)}
        return data

    @staticmethod
    def deserialize_options(bot, options) -> Dict[Emoji, Any]:
        data = {}
        if isinstance(options, str):
            options = ast.literal_eval(options)
        for option in options:
            emoji = bot.get_emoji(option)
            descriptor = options.get("descriptor")
            data[emoji] = descriptor
        return data

    @classmethod
    @abstractmethod
    async def from_dict(cls, bot, data) -> Dict:
        kwargs = {"id": int(data.get("id"))}

        guild_id = int(data.get("guild_id"))
        channel_id = int(data.get("channel_id"))
        kwargs["message"] = await bot.get_guild(guild_id).get_channel(channel_id).fetch_message(kwargs["id"])
        if kwargs["message"] is None:
            raise ValueError("The message for this reaction menu has been deleted!")

        if not kwargs["message"].embeds:
            raise ValueError("The message for this reaction menu has no menu in it!")

        kwargs["embed"] = kwargs["message"].embeds[0]
        kwargs["options"] = cls.deserialize_options(bot, data.get("options"))
        kwargs["enabled"] = bool(data.get("enabled"))
        kwargs["show_ids"] = bool(data.get("show_ids"))
        kwargs["auto_enable"] = False

        return kwargs

    def add_option(self, emoji: Emoji, descriptor: Any) -> bool:
        if emoji in self.options:
            return False

        self.options[emoji] = descriptor

    def remove_option(self, emoji: Emoji) -> bool:
        return self.options.pop(emoji, None) is not None

    def add_many(self, options: Dict[Emoji, Any]) -> List[Dict[Emoji, Any]]:
        failed = []
        for emoji, descriptor in options.items():
            if not self.add_option(emoji, descriptor):
                failed.append({emoji: descriptor})
        return failed

    def remove_many(self, emojis: List[Emoji]) -> List[Emoji]:
        failed = []
        for emoji in emojis:
            if not self.remove_option(emoji):
                failed.append(emoji)
        return failed

    def generate_embed(self) -> Embed:
        if self.embed is not None:
            self.embed = Embed(title=self.embed.title, description=self.embed.description)
        else:
            raise ValueError("There is no embed to create!")
        for emoji, descriptor in self.options.items():
            self.embed.add_field(name=emoji, value=descriptor, inline=False)

        return self.embed

    def add_footer(self):
        if self.show_ids and self.id:
            self.embed.set_footer(text=f"Menu message id: {self.id}")

    def remove_footer(self):
        if self.embed.footer:
            self.embed.set_footer()

    def update_embed(self, **kwargs) -> Embed:
        old_data = self.embed.to_dict()
        for arg in kwargs:
            old_data[arg] = kwargs.get(arg)
        self.embed = Embed.from_dict(old_data)
        return self.embed

    def enable_menu(self, bot):
        if not self.enabled:
            self.enabled = True
            bot.add_listener(self.on_react_add, "on_raw_reaction_add")
            bot.add_listener(self.on_react_remove, "on_raw_reaction_remove")

    def disable_menu(self, bot):
        if self.enabled:
            self.enabled = False
            bot.remove_listener(self.on_react_add, "on_raw_reaction_add")
            bot.remove_listener(self.on_react_remove, "on_raw_reaction_remove")

    def toggle_menu(self, bot):
        if not self.enabled:
            self.enable_menu(bot)
        else:
            self.disable_menu(bot)

    async def finalise_and_send(self, bot, channel: TextChannel):
        self.generate_embed()
        await self.send_to_channel(channel)
        self.add_footer()
        await self.message.edit(embed=self.embed)
        await self.add_reactions(self.message)
        if self.auto_enable:
            self.enable_menu(bot)

    async def update_message(self):
        self.generate_embed()
        await self.message.edit(embed=self.embed)
        await self.add_reactions()

    async def send_to_channel(self, channel: TextChannel) -> Message:
        self.message: Message = await channel.send(embed=self.embed)
        self.id = self.message.id
        return self.message

    async def add_reactions(self, message: Message = None):
        if message is None:
            message = self.message

        if message is None:
            raise ValueError("There is no message to add reactions to")

        current_reactions = [x.emoji for x in message.reactions]

        for emoji in self.options:
            if emoji not in current_reactions:
                await message.add_reaction(emoji)

    async def on_react_add(self, payload):
        if payload is None:
            return None
        if self.enabled and self.react_add_func and not payload.member.bot and payload.message_id == self.id:
            return await self.react_add_func(payload)
        return None

    async def on_react_remove(self, payload):
        if payload is None:
            return None
        if self.enabled and self.react_remove_func and payload.message_id == self.id:
            return await self.react_remove_func(payload)
        return None
