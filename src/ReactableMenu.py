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
        """Creates a ReactableMenu that can have its options customised and actions upon interaction customised.

        Args:
            title (str): The title of the menu. Is used as the title in the embed.
            title_disabled_suffix (str, optional): The suffix to append to the title when the menu is disabled. Defaults to "Disabled".
            description (str, optional): The description of the menu. Can be used to provide more information about the menu to the user. Defaults to "".
            description_meta (str, optional): Additional notes for the description, again can be used to help inform the user about the menu. Defaults to "".
            options (Dict, optional): The options to be present in the menu. Defaults to {}.
            enabled_color (Color, optional): The embed color to use when the menu is enabled. Defaults to Color.green().
            disabled_color (Color, optional): The embed color to use when the menu is disabled. Defaults to Color.red().
            message_id (int, optional): The ID of the messsage the menu is tied to. Defaults to None.
            message (Message, optional): The message object the menu is tied to. Defaults to None.
            view (View, optional): The view that is used to display the buttons that users interact with. Defaults to None.
            on_button_click (Callable, optional): The function that is called when a user interacts with the menu. Must be async. Defaults to None.
            use_inline (bool, optional): Toggles if the embed uses in-line fields or not. Defaults to False.
            show_id (bool, optional): Toggles if the ID of the menu should be displayed in the footer of the menu. Defaults to False.
            auto_enable (bool, optional): Determines if the menu is automatically enabled after being sent. Defaults to False.
        """
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
        """Creates a ReactableMenu from a dictionary of kwargs. Can be used to load a menu from a database.

        Args:
            data (Dict): The data used to instantiate a ReactableMenu.

        Returns:
            ReactableMenu: The ReactableMenu that was created from the given data dictionary.
        """
        options_list = [MenuOption(x) for x in data.get("options", [])]
        data["options"] = {x.id: x for x in options_list}
        if data.get("enabled_color"):
            data["enabled_color"] = Color(int(data.get("enabled_color")))
        if data.get("disabled_color"):
            data["disabled_color"] = Color(int(data.get("disabled_color")))
        return ReactableMenu(**data)

    def to_dict(self) -> Dict:
        """Creates a dictionary from a ReactableMenu. Allows for saving and with from_dict loading of ReactableMenus to a database.

        Returns:
            Dict: The dictionary representation of a ReactableMenu.
        """
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
        """Get the ID of the menu.

        Returns:
            int: The ID of the menu.
        """
        return self.message_id if self.message_id else self.message.id

    def add_option(
        self, given_emoji: Union[PartialEmoji, Emoji, str], description: Any
    ) -> bool:
        """Add an option to a ReactableMenu. Each option is an emoji associated with some data.

        Args:
            given_emoji (Union[PartialEmoji, Emoji, str]): The emoji to use for the option.
            description (Any): The data associated with a given option/emoji.

        Returns:
            bool: True if the option was added successfully, False otherwise.
        """
        try:
            emoji = ReactionEmoji(given_emoji)

            if emoji.emoji_id in self.options:
                return False

            self.options[emoji.emoji_id] = MenuOption(emoji, description)
            return True
        except ValueError:
            return False

    def remove_option(self, given_emoji: Union[PartialEmoji, Emoji, str]) -> bool:
        """Remove an option from a menu using it's emoji to identify it.

        Args:
            given_emoji (Union[PartialEmoji, Emoji, str]): The emoji to remove as an option from the menu.

        Returns:
            bool: True if the option was remove, False otherwise.
        """
        try:
            emoji = ReactionEmoji(given_emoji)
            return self.options.pop(emoji.emoji_id, None) is not None
        except ValueError:
            return False

    def build_embed(self) -> Embed:
        """Build the embed object from the current menu data. Can be then sent in a message.

        Returns:
            Embed: The embed object that represents a ReactableMenu.
        """
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
        """Build the view object that represents a menu. Can be then sent in a message.

        Args:
            is_persistent (bool, optional): If the view should be persistent. Defaults to False.
            timeout (int, optional): If the view is not persistent, how long should it last. Defaults to 180.

        Returns:
            View: The view object that represent a ReactableMenu.
        """
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
        """Generate the title text for the embed.

        Returns:
            str: The title text to set in the embed.
        """
        suffix = f" ({self.title_disabled_suffix})" if not self.enabled else ""
        return f"{self.title}{suffix}"

    def generate_description(self) -> str:
        """Generate the description text for the embed.

        Returns:
            str: The description text for the embed.
        """
        description = ""

        if self.description:
            description += self.description

        if self.description_meta:
            description += f"\n{self.description_meta}"

        return description

    def get_current_color(self) -> Color:
        """Get the correct color based on if the menu is enabled or disabled.

        Returns:
            Color: The color representing the current state of the menu.
        """
        return self.enabled_color if self.enabled else self.disabled_color

    def generate_option_field(self, option: "MenuOption") -> Tuple[str, str]:
        """Generate the field data for a given option in the menu.

        Args:
            option (MenuOption): The option to generate the field data for.

        Returns:
            Tuple[str, str]: First item is the name data for the field. Second item is the value data for the field.
        """
        name = "​"
        value = str(option)
        return name, value

    def generate_footer_text(self) -> str:
        """Generate the footer text for the embed object.

        Returns:
            str: The footer text for the embed object.
        """
        return f"Menu ID: {self.message_id}"

    async def enable(self) -> None:
        """Enable the current menu.

        Raises:
            ValueError: If the menu has not been created it cannot be enabled and a ValueError is raised. This happens when the menu is enabled before sending.
        """
        if not self.enabled:
            self.enabled = True
            if not self.message:
                raise ValueError("ReactionMenu cannot be enabled before it is sent")
            await self.message.edit(embed=self.build_embed(), view=self.build_view())

    async def disable(self) -> None:
        """Disable the current menu."""
        if self.enabled:
            self.enabled = False
            if not self.message:
                return None
            await self.message.edit(embed=self.build_embed(), view=self.build_view())

    async def on_interaction_handler(self, interaction: Interaction) -> bool:
        """The function that is called whenever the view for the given ReactableMenu is interacted with. Will perform some checks and then will run the given on_button_click function.

        Args:
            interaction (Interaction): The interaction that caused the function to be called.

        Returns:
            bool: True if the interaction was a valid interaction and the process succeeded. False otherwise.
        """
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

    async def send_menu(self, channel: GuildChannel) -> Message:
        """Send the menu to a given channel.

        Args:
            channel (GuildChannel): The Discord channel to send the menu to.

        Returns:
            Message: The message that was created by the menu and in which the menu is.
        """
        # Send a temporary message so that we have an exisiting message object to reference
        self.message = await channel.send("_Building reaction menu..._")
        self.message_id = self.message.id
        self.enabled = self.auto_enable

        await self.message.edit(
            content="​", embed=self.build_embed(), view=self.build_view()
        )
        return self.message


class MenuOption:
    def __init__(self, emoji: ReactionEmoji, description: Any, reaction_count: int = 0):
        """Creates a menu option object. Stores any relevant data to each option.

        Args:
            emoji (ReactionEmoji): The emoji associated with the option.
            description (Any): The data associated with the option.
            reaction_count (int, optional): The number of times the option has been selected. Defaults to 0.
        """
        self._emoji = emoji
        self.reaction_count = reaction_count
        self._description = description

    @property
    def id(self) -> str:
        """The ID of the option. Each option is identified by its emoji ID.

        Returns:
            str: The string of the ID of the emoji for the option.
        """
        return self.emoji.emoji_id

    @classmethod
    def from_dict(cls, data: Dict) -> "MenuOption":
        """Creates a menu option from a dictionary of kwargs. Can be used to load an option from a database.

        Args:
            data (Dict): The dictionary containing the menu option data.

        Returns:
            MenuOption: The menu option created from the given dictionary.
        """
        data["emoji"] = ReactionEmoji(data["emoji"])
        try:
            data["reaction_count"] = int(data.get("reaction_count"))
        except ValueError:
            data["reaction_count"] = 0
        return MenuOption(**data)

    @property
    def description(self) -> str:
        """Get the description of the option in a format Discord can represent.

        Returns:
            str: The description in a Discord format.
        """
        if isinstance(self._description, Role) or isinstance(
            self._description, GuildChannel
        ):
            return self._description.mention
        else:
            return str(self._description)

    @property
    def label(self) -> str:
        """Get the description of the option in a readable format.

        Returns:
            str: The description formatted in a readable format.
        """
        if isinstance(self._description, Role):
            return f"{self._description.name} (Role)"
        elif isinstance(self._description, GuildChannel):
            return f"{self._description.name} (Channel)"
        else:
            return str(self._description)

    @property
    def emoji(self) -> Union[PartialEmoji, Emoji]:
        """Get the Discord representable emoji of the option.

        Returns:
            Union[PartialEmoji, Emoji]: The emoji associated with the option in a Discord presentable format.
        """
        return self._emoji.discord_emoji

    def to_dict(self) -> Dict:
        """Get a dictionary object that represents a MenuOption. Can be used for saving/loading using the from_dict function.

        Returns:
            Dict: The dictionary object that represents a MenuOption.
        """
        return {
            "emoji": self.emoji.to_dict(),
            "description": self.description,
            "reaction_count": self.reaction_count,
        }

    def __str__(self) -> str:
        return f"{self.emoji} **—** {self.description}"

    def __repr__(self) -> str:
        return f"{{Emoji: {self.emoji.discord_emoji}, Description: {self.description!r}, Reaction Count: {self.reaction_count!r}}}"
