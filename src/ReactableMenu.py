from typing import Dict, List

from discord import Embed, Message
from discord.ext.commands import Context


class ReactableMenu(Embed):

    def __init__(self, **kwargs):
        self.react_add_func = kwargs.pop("add_func", None)
        self.react_remove_func = kwargs.pop("remove_func", None)
        super().__init__(**kwargs)
        self.id = None
        self.message = None
        self.options = {}

    def __str__(self) -> str:
        __str = ""
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
        for emoji, descriptor in self.options:
            self.add_field(name=emoji, value=descriptor, inline=False)
        return self

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
