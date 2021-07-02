from discord import Embed


class ReactableMenu(Embed):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_option(self, emoji, descriptor):
        pass

    def remove_option(self, emoji):
        pass

    def to_dict(self):
        pass

    def from_dict(self, data):
        pass
