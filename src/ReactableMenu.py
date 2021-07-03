from typing import Dict, List

from discord import Embed, Message
from discord.ext.commands import Context


class ReactableMenu:

    def __init__(self, add_func=None, remove_func=None, **kwargs):
        self.react_add_func = add_func
        self.react_remove_func = remove_func
        self.id = None
        self.message = None
        self.embed = Embed(**kwargs)
        self.options = {}
        self.enabled = False

    def __str__(self) -> str:
        if self.embed is None:
            return ""
        __str = f"Title:{self.embed.title} | Description: {self.embed.description}"
        for emoji, descriptor in self.options.items():
            __str += f"Emoji: {emoji} | Descriptor: {descriptor}\n"
        return __str

    def __repr__(self):
        return repr(self.options)

    def add_option(self, emoji: str, descriptor: str) -> bool:
        if emoji in self.options:
            return False

        self.options[emoji] = descriptor

    def remove_option(self, emoji: str) -> bool:
        return self.options.pop(emoji, None) is not None

    def add_many(self, options: Dict[str, str]) -> List[Dict[str, str]]:
        failed = []
        for emoji, descriptor in options.items():
            if not self.add_option(emoji, descriptor):
                failed.append({emoji: descriptor})
        return failed

    def remove_many(self, emojis: List[str]) -> List[str]:
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

    def to_dict(self) -> Dict:
        pass

    def from_dict(self, data: Dict):
        pass

    async def send_to_context(self, context: Context) -> Message:
        self.message: Message = await context.send(embed=self)
        self.id = self.message.id
        return self.message

    def on_react(self, payload):
        if self.react_add_func:
            return self.react_add_func(payload)
        return None

    def on_react_remove(self, payload):
        if self.react_remove_func:
            return self.react_remove_func(payload)
        return None
