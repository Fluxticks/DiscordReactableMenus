from typing import Any, Dict, Union
import emoji
from discord import PartialEmoji, Emoji


def string_to_partial_emoji(string_emoji: str) -> PartialEmoji:
    string_emoji = string_emoji.strip()
    converted_emoji = emoji.demojize(string_emoji, use_aliases=True)
    if converted_emoji == string_emoji:
        # Emojis should be in the format <a:name:id>
        if string_emoji.count(":") < 2:
            return None
        animated = "<a:" in string_emoji
        first_colon_index = string_emoji.index(":")
        last_colon_index = string_emoji.index(":", first_colon_index + 1)
        emoji_name = string_emoji[first_colon_index + 1 : last_colon_index]
        emoji_id = string_emoji[last_colon_index + 1 : -1]

        emoji_data = {"name": emoji_name, "id": emoji_id, "animated": animated}
    else:
        emoji_data = {"name": string_emoji, "id": None, "animated": False}

    return PartialEmoji.from_dict(emoji_data)


def emoji_to_partial_emoji(full_emoji: Emoji) -> PartialEmoji:
    emoji_data = {
        "name": full_emoji.name,
        "id": full_emoji.id,
        "animated": full_emoji.animated,
    }
    return PartialEmoji.from_dict(emoji_data)


class ReactionEmoji:
    def __init__(
        self, emoji_input: Union[PartialEmoji, Emoji, Dict, str, "ReactionEmoji"]
    ):
        """Creates a universal emoji handler so that given some emoji, a Discord presentable emoji can be obtained.

        Args:
            emoji_input (Union[PartialEmoji, Emoji, Dict, str, ReactionEmoji]): The emoji to convert.

        Raises:
            ValueError: If the given input is not of a valid type a ValueError will be raised.
        """
        if isinstance(emoji_input, str):
            self.partial = string_to_partial_emoji(emoji_input)
        elif isinstance(emoji_input, Emoji):
            self.partial = emoji_to_partial_emoji(emoji_input)
        elif isinstance(emoji_input, PartialEmoji):
            self.partial = emoji_input
        elif isinstance(emoji_input, ReactionEmoji):
            self.partial = emoji_input.partial
        elif isinstance(emoji_input, dict):
            self.partial = PartialEmoji.from_dict(emoji_input)
        else:
            raise ValueError("Invalid emoji type given!")

    @property
    def name(self) -> str:
        """Get the name of the emoji.

        Returns:
            str: The name of the emoji.
        """
        return self.partial.name

    @property
    def emoji_id(self) -> str:
        """Get the ID of the emoji. If the emoji is a unicode emoji, its name will be returned.

        Returns:
            str: The ID of the emoji.
        """
        return str(self.partial.id) if self.partial.id else self.name

    @property
    def animated(self) -> bool:
        """If the emoji is a custom animated Discord emoji.

        Returns:
            bool: If the emoji is animated.
        """
        return self.partial.animated

    @property
    def discord_emoji(self) -> PartialEmoji:
        """Get a Discord representable emoji of the current emoji.

        Returns:
            PartialEmoji: A Discord representable emoji.
        """
        return self.partial

    @classmethod
    def from_dict(cls, emoji_data: Dict) -> "ReactionEmoji":
        """Create an emoji from dictionary data.

        Args:
            emoji_data (Dict): The emoji data to convert.

        Returns:
            ReactionEmoji: The handled emoji from the given data.
        """
        return ReactionEmoji(PartialEmoji.from_dict(emoji_data))

    def to_dict(self) -> Dict:
        """Get a dictionary representation of the current emoji.

        Returns:
            Dict: The dictionary of the emoji.
        """
        return self.partial.to_dict()

    def __str__(self) -> str:
        return emoji.emojize(self.name, use_aliases=True)

    def __repr__(self) -> str:
        return f"<{'a' if self.animated else ''}:{self.name}:{self.emoji_id}>"

    def __eq__(self, __o: Any) -> bool:
        return isinstance(__o, ReactionEmoji) and self.emoji_id == __o.emoji_id
