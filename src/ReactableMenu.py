from abc import abstractmethod
from typing import Any, Callable, Dict, Tuple, Union
from discord import (
    Emoji,
    HTTPException,
    Interaction,
    Message,
    PartialEmoji,
    Role,
    Color,
    Embed,
    ButtonStyle,
    SelectOption,
)
from discord.ui import View, Button, Select
from discord.abc import GuildChannel
from discord.ext.commands import Bot

from src.EmojiHandler import ReactionEmoji


class MenuBase:
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
        use_inline: bool = False,
        show_id: bool = False,
        auto_enable: bool = False,
        **kwargs,
    ):
        """Creates a reactable menu that can have its options customised and actions upon interaction customised.

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

        self.use_inline = use_inline
        self.show_id = show_id
        self.auto_enable = auto_enable
        self.enabled = False

    @classmethod
    def from_dict(cls, data: Dict) -> "MenuBase":
        """Creates a MenuBase object from a dictionary of kwargs. Can be used to load a menu from a database.

        Args:
            data (Dict): The data used to instantiate a new menu.

        Returns:
            ReactableMenu: The MenuBase object that was created from the given data dictionary.
        """
        options_list = [MenuOption(x) for x in data.get("options", [])]
        data["options"] = {x.id: x for x in options_list}
        if data.get("enabled_color"):
            data["enabled_color"] = Color(int(data.get("enabled_color")))
        if data.get("disabled_color"):
            data["disabled_color"] = Color(int(data.get("disabled_color")))
        return MenuBase(**data)

    def to_dict(self) -> Dict:
        """Creates a dictionary from a menu. Allows for saving and with from_dict loading of menus to a database.

        Returns:
            Dict: The dictionary representation of a menu.
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

    @abstractmethod
    def send_menu(self, channel: GuildChannel):
        """Used to send the menu to a channel. This method sets the message attribute, builds the menu and then sends it.

        Args:
            channel (GuildChannel): The channel to send the menu in.
        """
        pass

    @abstractmethod
    def enable(self, *args, **kwargs):
        """Method used to enable the menu."""
        pass

    @abstractmethod
    def disable(self, *args, **kwargs):
        """Method used to disable the menu"""
        pass

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
        """Add an option to a menu. Each option is an emoji associated with some data.

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


class InteractionMenu(MenuBase):
    def __init__(
        self,
        title: str,
        interaction_handler: Callable = None,
        view: View = None,
        **kwargs,
    ):
        """Creates a reactable menu that uses the Discord Interaction system to handle events.

        Args:
            title (str): The title of the menu. Displays in the title of the embed.
            interaction_handler (Callable, optional): The coroutine that handles the interactions. Must be async. Defaults to None.
            view (View, optional): The view used to hold the components that users interact with. Defaults to None.
        """
        super().__init__(title, **kwargs)
        self.interaction_handler = interaction_handler
        self.view = view

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

    async def on_interact_event(self, interaction: Interaction) -> bool:
        """The function that is called whenever the view for the given InteractionMenu is interacted with. Will perform some checks and then will run the given interaction_handler function.

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
            # try:
            await self.interaction_handler(self, interaction)
            return True
            # except:
            # await interaction.response.send_message(
            #     "There was an error handling your interaction, please contact a developer",
            #     ephemeral=True,
            # )
        else:
            await interaction.response.send_message(
                content="This menu is currently disabled!", ephemeral=True
            )
        return False

    def build_view(self, is_persistent: bool = False, timeout: int = 180) -> View:
        """Build the view object that represents a menu. Can be then sent in a message.

        Args:
            is_persistent (bool, optional): If the view should be persistent. Defaults to False.
            timeout (int, optional): If the view is not persistent, how long should it last. Defaults to 180.

        Returns:
            View: The view object that represent a InteractionMenu.
        """
        for item in self.view.children:
            item.callback = self.on_interact_event

        return self.view


class ButtonMenu(InteractionMenu):
    def __init__(
        self,
        title: str,
        button_labels: bool = False,
        button_style: ButtonStyle = ButtonStyle.primary,
        **kwargs,
    ):
        """Creates an InterationMenu that uses Discord buttons to operate.

        Args:
            title (str): The title of the menu. Is used as the title in the embed.
            button_labels (bool, optional): Toggles if the buttons in the menu should have the label in them or only the emoji. Defaults to False.
            button_style (ButtonStyle, optional): The style of the buttons that users interact with. Defaults to ButtonStyle.primary.
        """
        super().__init__(title, **kwargs)

        self.button_labels = button_labels
        self.button_style = button_style

    def to_dict(self) -> Dict:
        """Creates a dictionary from a menu. Allows for saving and with from_dict loading of menus to a database.

        Returns:
            Dict: The dictionary representation of a menu.
        """
        data = super().to_dict()
        data["button_style"] = self.button_style
        data["button_labels"] = self.button_labels
        return data

    def build_view(self, is_persistent: bool = False, timeout: int = 180) -> View:
        """Build the view object that represents a menu. Can be then sent in a message.

        Args:
            is_persistent (bool, optional): If the view should be persistent. Defaults to False.
            timeout (int, optional): If the view is not persistent, how long should it last. Defaults to 180.

        Returns:
            View: The view object that represent a ButtonMenu.
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
                        label=option.label if self.button_labels else "",
                        emoji=option.emoji,
                        custom_id=f"{emoji_id}_{self.message_id}",
                        style=self.button_style,
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

        self.view = super().build_view()

        return self.view


class SelectMenu(InteractionMenu):
    def __init__(
        self, title: str, menu_labels: bool = False, placeholder: str = "", **kwargs
    ):
        """Creates an InterationMenu that uses a Discord Select Menu to operate.

        Args:
            title (str): The title of the menu. Is used as the title in the embed.
            menu_labels (bool, optional): Toggles if the options in the menu should have the label in them or only the emoji. Defaults to False.
            placeholder (str, optional): The placeholder string that displays in the menu selector. Defaults to "".
        """
        super().__init__(title, **kwargs)
        self.menu_labels = menu_labels
        self.placeholder = placeholder

    def to_dict(self) -> Dict:
        """Creates a dictionary from a menu. Allows for saving and with from_dict loading of menus to a database.

        Returns:
            Dict: The dictionary representation of a menu.
        """
        data = super().to_dict()
        data["menu_labels"] = self.menu_labels
        data["placeholder"] = self.placeholder
        return data

    def build_view(self, is_persistent: bool = False, timeout: int = 180) -> View:
        """Build the view object that represents a menu. Can be then sent in a message.

        Args:
            is_persistent (bool, optional): If the view should be persistent. Defaults to False.
            timeout (int, optional): If the view is not persistent, how long should it last. Defaults to 180.

        Returns:
            View: The view object that represent a SelectMenu.
        """
        if is_persistent:
            self.view = View(timeout=None)
        else:
            self.view = View(timeout=timeout)

        select_options = []
        for emoji_id, option in self.options.items():
            select_options.append(
                SelectOption(
                    label=option.label if self.menu_labels else "​",
                    value=f"{emoji_id}_{self.message_id}",
                    emoji=option.emoji,
                )
            )

        select_menu = Select(
            max_values=len(select_options),
            min_values=0,
            placeholder=self.placeholder,
            custom_id=f"selectmenu_{self.message_id}",
            options=select_options,
            disabled=not self.enabled,
        )

        if self.enabled:
            self.view.add_item(
                Button(
                    label="",
                    emoji="⏹️",
                    custom_id=f"disable_{self.message_id}",
                    style=ButtonStyle.red,
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

        self.view.add_item(select_menu)
        self.view = super().build_view()

        return self.view


class ReactionMenu(MenuBase):
    def __init__(
        self,
        title: str,
        react_add_handler: Callable = None,
        react_remove_handler: Callable = None,
        **kwargs,
    ):
        super().__init__(title, **kwargs)
        self.react_add_handler = react_add_handler
        self.react_remove_handler = react_remove_handler

    async def send_menu(self, channel: GuildChannel, bot_instance: Bot):
        self.message = await channel.send("_Building reaction menu..._")
        self.message_id = self.message.id

        if self.auto_enable:
            await self.enable(bot_instance)
        else:
            self.enabled = True
            await self.disable(bot_instance)

        return self.message

    async def enable(self, bot_instance: Bot):
        if not self.enabled:
            self.enabled = True
            await self.update_menu()
            bot_instance.add_listener(self.on_react_add_event, "on_raw_reaction_add")
            bot_instance.add_listener(
                self.on_react_remove_event, "on_raw_reaction_remove"
            )
            return True
        return False

    async def disable(self, bot_instance: Bot):
        if self.enabled:
            self.enabled = False
            bot_instance.remove_listener(self.on_react_add_event, "on_raw_reaction_add")
            bot_instance.remove_listener(
                self.on_react_remove_event, "on_raw_reaction_remove"
            )
            await self.update_menu()
            return True
        return False

    async def update_menu(self):
        if not self.message:
            raise ValueError("Cannot update message before creation!")

        await self.message.edit(content="", embed=self.build_embed())
        self.message = await self.message.channel.fetch_message(self.message_id)
        if self.enabled:
            await self.add_reactions()

    async def add_reactions(self, message: Message = None):
        if message is None and self.message is None:
            raise ValueError("Cannot add reactions to empty message")

        if message is None:
            message = self.message

        missing_emojis = [x.id for x in self.options.values()]
        for react in self.message.reactions:
            react_emoji = ReactionEmoji(react.emoji)
            if react_emoji.emoji_id in missing_emojis:
                missing_emojis.remove(react_emoji.emoji_id)
            else:
                await react.clear()

        for emoji_id in missing_emojis:
            emoji = self.options.get(emoji_id).emoji
            try:
                await message.add_reaction(emoji)
            except HTTPException:
                pass

    async def on_react_add_event(self, payload):
        if payload is None:
            return None

        if payload.member.bot:
            return None

        if payload.message_id != self.message_id:
            return None

        if self.react_add_handler is None:
            return None

        if self.enabled:
            self.message = await self.message.channel.fetch_message(payload.message_id)
            return await self.react_add_handler(payload)
        return None

    async def on_react_remove_event(self, payload):
        if payload is None:
            return None

        if payload.message_id != self.message_id:
            return None

        if self.react_remove_handler is None:
            return None

        if self.enabled:
            self.message = await self.message.channel.fetch_message(payload.message_id)
            return await self.react_remove_handler(payload)
        return None


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
        return self._emoji.emoji_id

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
