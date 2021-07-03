from typing import Dict, List

from discord import Embed, Message, Emoji, TextChannel


class ReactableMenu:

    def __init__(self, add_func=None, remove_func=None, show_ids=True, auto_enable=False, **kwargs):
        self.react_add_func = add_func
        self.react_remove_func = remove_func
        self.id = None
        self.message = None
        self.embed = Embed(**kwargs)
        self.options = {}
        self.enabled = False
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

    def add_option(self, emoji: Emoji, descriptor: str) -> bool:
        if emoji in self.options:
            return False

        self.options[emoji] = descriptor

    def remove_option(self, emoji: Emoji) -> bool:
        return self.options.pop(emoji, None) is not None

    def add_many(self, options: Dict[Emoji, str]) -> List[Dict[Emoji, str]]:
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

    def update_embed(self, **kwargs) -> Embed:
        old_data = self.embed.to_dict()
        for arg in kwargs:
            old_data[arg] = kwargs.get(arg)
        self.embed = Embed.from_dict(old_data)
        return self.embed

    def enable_menu(self, bot):
        self.enabled = True
        bot.add_listener(self.on_react_add, "on_raw_reaction_add")
        bot.add_listener(self.on_react_remove, "on_raw_reaction_remove")

    def disable_menu(self, bot):
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
        if self.react_add_func and self.enabled and payload.message_id == self.id:
            return self.react_add_func(payload)
        return None

    async def on_react_remove(self, payload):
        if self.react_remove_func and self.enabled and payload.message_id == self.id:
            return self.react_remove_func(payload)
        return None
