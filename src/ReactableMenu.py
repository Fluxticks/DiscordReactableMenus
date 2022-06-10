from typing import Any, Callable, Dict, Tuple, Union
from discord import (
    Emoji,
    Interaction,
    Message,
    PartialEmoji,
    Role,
    Color,
    Embed,
    ButtonStyle,
)
from discord.ui import View, Button
from discord.abc import GuildChannel
from discord.ext import commands

from src.EmojiHandler import ReactionEmoji


class ReactableMenu:
    def __init__(
        self,
        title: str,
        title_disabled_suffix: str = "Disabled",
        description: str = "",
        description_meta: str = "",
        options: Dict = {},
        enabled_color: Color = Color.green(),
        disabled_color: Color = Color.red(),
        message_id: int = None,
        message: Message = None,
        view: View = None,
        on_button_click: Callable = None,
        use_inline: bool = False,
        show_id: bool = False,
        auto_enable: bool = False,
        **kwargs,
    ):
        self.title = title
        self.title_disabled_suffix = title_disabled_suffix
        self.description = description
        self.description_meta = description_meta
        self.enabled_color = enabled_color
        self.disabled_color = disabled_color
        self.options = options

        self.message = message
        self.message_id = message_id
        self.view = view
        if self.message is not None:
            self.channel = message.channel
            self.guild = message.channel.guild

            self.channel_id = self.channel.id
            self.guild_id = self.guild.id
        else:
            self.channel = None
            self.guild = None

            self.channel_id = None
            self.guild_id = None

        self.on_button_click = on_button_click

        self.use_inline = use_inline
        self.show_id = show_id
        self.auto_enable = auto_enable
        self.enabled = False

    @classmethod
    def from_dict(cls, data: Dict) -> "ReactableMenu":
        options_list = [MenuOption(x) for x in data.get("options", [])]
        data["options"] = {x.id: x for x in options_list}
        if data.get("enabled_color"):
            data["enabled_color"] = Color(int(data.get("enabled_color")))
        if data.get("disabled_color"):
            data["disabled_color"] = Color(int(data.get("disabled_color")))
        return ReactableMenu(**data)

    def to_dict(self) -> Dict:
        options = [x.to_dict() for x in self.options.values()]
        data = {
            "title": self.title,
            "title_disabled_suffix": self.title_disabled_suffix,
            "description": self.description,
            "description_meta": self.description_meta,
            "enabled_color": self.enabled_color.value,
            "disabled_color": self.disabled_color.value,
            "use_inline": self.use_inline,
            "show_id": self.show_id,
            "enabled": self.enabled,
            "options": options,
        }
        return data

    @property
    def id(self) -> int:
        return self.message_id if self.message_id else self.message.id

    def add_option(
        self, given_emoji: Union[PartialEmoji, Emoji, str], description: Any
    ) -> bool:
        try:
            emoji = ReactionEmoji(given_emoji)

            if emoji.emoji_id in self.options:
                return False

            self.options[emoji.emoji_id] = MenuOption(emoji, description)
            return True
        except ValueError:
            return False

    def remove_option(self, given_emoji: Union[PartialEmoji, Emoji, str]) -> bool:
        try:
            emoji = ReactionEmoji(given_emoji)
            return self.options.pop(emoji.emoji_id, None) is not None
        except ValueError:
            return False

    def build_embed(self) -> Embed:
        title = self.generate_title()
        description = self.generate_description()
        color = self.get_current_color()

        embed = Embed(title=title, description=description, color=color)

        for option in self.options.values():
            name, description = self.generate_option_field(option)
            embed.add_field(name=name, value=description, inline=self.use_inline)

        if self.show_id:
            embed.set_footer(text=self.generate_footer_text())

        return embed

    def build_view(self, is_persistent: bool = False, timeout: int = 180) -> View:
        if is_persistent:
            self.view = View(timeout=None)
        else:
            self.view = View(timeout=timeout)

        if self.enabled:
            self.view.add_item(
                Button(
                    label="",
                    emoji="⏹️",
                    custom_id=f"disable_{self.message_id}",
                    style=ButtonStyle.red,
                )
            )

            for emoji_id, option in self.options.items():
                self.view.add_item(
                    Button(
                        label=option.label,
                        emoji=option.emoji,
                        custom_id=f"{emoji_id}_{self.message_id}",
                    )
                )
        else:
            self.view.add_item(
                Button(
                    label="",
                    emoji="▶️",
                    custom_id=f"enable_{self.message_id}",
                    style=ButtonStyle.green,
                )
            )

        for item in self.view.children:
            item.callback = self.on_interaction_handler

        return self.view

    def generate_title(self) -> str:
        suffix = f" ({self.title_disabled_suffix})" if not self.enabled else ""
        return f"{self.title}{suffix}"

    def generate_description(self) -> str:
        description = ""

        if self.description:
            description += self.description

        if self.description_meta:
            description += f"\n{self.description_meta}"

        return description

    def get_current_color(self) -> Color:
        return self.enabled_color if self.enabled else self.disabled_color

    def generate_option_field(self, option: "MenuOption") -> Tuple[str, str]:
        name = "​"
        value = str(option)
        return name, value

    def generate_footer_text(self) -> str:
        return f"Menu ID: {self.message_id}"

    async def enable(self) -> None:
        if not self.enabled:
            self.enabled = True
            if not self.message:
                raise ValueError("ReactionMenu cannot be enabled before it is sent")
            await self.message.edit(embed=self.build_embed(), view=self.build_view())

    async def disable(self) -> None:
        if self.enabled:
            self.enabled = False
            if not self.message:
                return None
            await self.message.edit(embed=self.build_embed(), view=self.build_view())

    async def on_interaction_handler(self, interaction: Interaction) -> bool:
        if interaction is None:
            # Ignore empty interactions
            return False

        if interaction.message.id != self.message_id:
            # Interactions that belong to other messages will be handled by other menus/cogs
            return False

        interaction_id = interaction.data.get("custom_id")

        # The enable/disable buttons need to be handled seperately from the rest of the menu
        if "enable" in interaction_id:
            await self.enable()
            await interaction.response.send_message("Menu enabled!", ephemeral=True)
            return True
        elif "disable" in interaction_id:
            await self.disable()
            await interaction.response.send_message("Menu disabled!", ephemeral=True)
            return True

        if self.enabled:
            try:
                await self.on_button_click(self, interaction)
                return True
            except:
                await interaction.response.send_message(
                    "There was an error handling your interaction, please contact a developer",
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message(
                content="This menu is currently disabled!", ephemeral=True
            )
        return False

    async def send_menu(self, context: commands.Context) -> Message:
        # Send a temporary message so that we have an exisiting message object to reference
        self.message = await context.send("_Building reaction menu..._")
        self.message_id = self.message.id
        self.enabled = self.auto_enable

        await self.message.edit(
            content="​", embed=self.build_embed(), view=self.build_view()
        )
        return self.message


class MenuOption:
    def __init__(self, emoji: ReactionEmoji, description: Any, reaction_count: int = 0):
        self._emoji = emoji
        self.reaction_count = reaction_count
        self._description = description

    @property
    def id(self) -> str:
        return self.emoji.emoji_id

    @classmethod
    def from_dict(cls, data: Dict) -> "MenuOption":
        data["emoji"] = ReactionEmoji(data["emoji"])
        try:
            data["reaction_count"] = int(data.get("reaction_count"))
        except ValueError:
            data["reaction_count"] = 0
        return MenuOption(**data)

    @property
    def description(self) -> str:
        if isinstance(self._description, Role) or isinstance(
            self._description, GuildChannel
        ):
            return self._description.mention
        else:
            return str(self._description)

    @property
    def label(self) -> str:
        if isinstance(self._description, Role):
            return f"{self._description.name} (Role)"
        elif isinstance(self._description, GuildChannel):
            return f"{self._description.name} (Channel)"
        else:
            return str(self._description)

    @property
    def emoji(self) -> Union[PartialEmoji, Emoji]:
        return self._emoji.discord_emoji

    def to_dict(self) -> Dict:
        return {
            "emoji": self.emoji.to_dict(),
            "description": self.description,
            "reaction_count": self.reaction_count,
        }

    def __str__(self) -> str:
        return f"{self.emoji} **—** {self.description}"

    def __repr__(self) -> str:
        return f"{{Emoji: {self.emoji.discord_emoji}, Description: {self.description!r}, Reaction Count: {self.reaction_count!r}}}"
