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
        return super().__str__()

    def add_option(self, emoji, descriptor) -> bool:
        pass

    def remove_option(self, emoji) -> bool:
        pass

    def add_many(self, options) -> List[bool]:
        pass

    def remove_many(self, emojis) -> List[bool]:
        pass

    def to_dict(self) -> Dict:
        pass

    def from_dict(self, data: Dict):
        pass
