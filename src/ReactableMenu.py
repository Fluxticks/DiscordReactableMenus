from typing import Dict, List, Any, Union, Tuple
from discord import Embed, HTTPException, Role, Colour
from discord.abc import GuildChannel

from .EmojiHandler import MultiEmoji

DISABLED_STRING = "(Currently Disabled)"


class ReactableMenu:

    def __init__(self, **kwargs):
        self.react_add_func = kwargs.pop("add_func", None)
        self.react_remove_func = kwargs.pop("remove_func", None)
        self.id = kwargs.pop("id", None)
        self._channel_id = kwargs.pop("channel_id", None)
        self.message = kwargs.pop("message", None)
        self.options = kwargs.pop("options", {})
        self.enabled = kwargs.pop("enabled", False)
        self.use_inline = kwargs.pop("use_inline", False)
        self.title = kwargs.pop("title", "Reaction Menu")
        self.disabled_string = kwargs.pop("disabled_string", DISABLED_STRING)
        self.description = kwargs.pop("description", "")
        self.meta = kwargs.pop("meta", "")
        self.show_id = kwargs.pop("show_id", False)
        self.auto_enable = kwargs.pop("auto_enable", False)

    @classmethod
    def from_dict(cls, data: Dict):
        """
        Creates a new reaction menu from a dictionary of data.
        :param data: The data of a saved reaction menu.
        """
        menu_options = data.pop("options")
        data["options"] = cls._parse_options(menu_options)
        return ReactableMenu(**data)

    @staticmethod
    def _parse_options(options):
        parsed_options = {}
        for option in options:
            formatted_option = ReactableOption.from_dict(option)
            parsed_options[formatted_option.emoji.emoji_id] = formatted_option
        return parsed_options

    def to_dict(self):
        """
        Gets the current state of the reaction menu and creates a dictionary that can be saved to a file or database.
        :return: A dictionary of the current state of the reaction menu.
        """
        data = {"id": self.id,
                "channel_id": self._channel_id,
                "use_inline": self.use_inline,
                "title": self.title,
                "disabled_string": self.disabled_string,
                "description": self.description,
                "meta": self.meta,
                "show_id": self.show_id,
                "enabled": self.enabled,
                "options": []
                }
        for option in self.options.values():
            data["options"].append(option.to_dict())
        return data

    async def initialise(self, bot):
        """
        Initialises the reaction menu. This will grab the latest instance of the reaction menu message and any other
        attributes which require the bot to be ready. Will return True if the message exists and the initialisation was
        successful, otherwise False.
        :param bot: The instance of the bot to use to access the API.
        :return: True if successful, False otherwise.
        """
        if self.id is None or self._channel_id is None:
            return False

        self.message = await (await bot.fetch_channel(self._channel_id)).fetch_message(self.id)
        if self.message is None:
            return False

        if self.auto_enable:
            self.enabled = False
            await self.enable_menu(bot)

        self._update_reaction_counts()

        return True

    def set_title(self, new_title: str) -> str:
        """
        Set the title attribute of a reaction menu.
        :param new_title: The new title to set.
        :return: The title after the update.
        """
        self.title = new_title
        return self.title

    def set_description(self, new_description: str) -> str:
        """
        Sets the description attribute of a reaction menu. This is not the description attribute of the embed.
        :param new_description: The new description to set.
        :return: The description attribute after the update.
        """
        self.description = new_description
        return self.description

    def set_meta(self, new_meta: str) -> str:
        """
        Sets the meta attribute of a reaction menu.
        :param new_meta: The new meta to set.
        :return: The meta attribute after the update.
        """
        self.meta = new_meta
        return self.meta

    def generate_title(self) -> str:
        """
        Generate the string used in the title of the embed message.
        :return: A string representing the title of the embed message.
        """
        if self.enabled:
            return self.title
        else:
            return f"{self.title} {self.disabled_string}"

    def generate_description(self) -> str:
        """
        Generate the description string used in the description arg of the embed message.
        :return: A string representing the description of the embed message.
        """
        result = ""
        if self.description:
            result += self.description

        if self.meta:
            result += "\n" + self.meta

        return result

    @staticmethod
    def generate_option_field(option: "ReactableOption") -> Tuple[str, str]:
        """
        Generate the name and value strings of a field to be added to the embed.
        :param option: The option to use the data of to format the string.
        :return: A tuple of strings of name, value representing the strings of a field in the embed message.
        """
        name = "​"
        value = str(option)
        return name, value

    def generate_colour(self) -> Colour:
        """
        Generate the colour used to colour the embed message.
        :return: A discord colour of the embed message.
        """
        if self.enabled:
            return Colour.green()
        else:
            return Colour.red()

    def generate_footer_text(self) -> str:
        """
        Generate the string used to set the footer of the embed message.
        :return: A string representing the footer of the embed message.
        """
        return f"Message ID: {self.id}"

    def generate_embed(self) -> Embed:
        """
        Generate the embed object representing this ReactableMenu using the generators of each of the sections of the
        embed to populate its fields.
        :return: An embed object representing this ReactableMenu
        """
        title = self.generate_title()
        description = self.generate_description()
        colour = self.generate_colour()

        embed = Embed(title=title, description=description, colour=colour)

        for option in self.options:
            name, value = self.generate_option_field(self.options.get(option))
            embed.add_field(name=name, value=value, inline=self.use_inline)

        if self.show_id:
            embed.set_footer(text=self.generate_footer_text())

        return embed

    def __contains__(self, item: Any) -> bool:
        return self.__getitem__(item) is not None

    def __getitem__(self, item: Any) -> Union["ReactableOption", Any]:
        try:
            p_emoji = MultiEmoji(item)
            return self.options.get(p_emoji.emoji_id)
        except ValueError:
            return None

    def add_option(self, emoji: Any, value: Union[Role, str]) -> bool:
        """
        Adds a single option to the reaction menu.
        :param emoji: The emoji of the option. Cannot already exist as an option.
        :param value: The value associated with the emoji. Eg a string or Role.
        :return: A boolean of if the option was added to the reaction menu.
        """
        try:
            formatted_emoji = MultiEmoji(emoji)

            if formatted_emoji in self:
                return False

            self.options[formatted_emoji.emoji_id] = ReactableOption(formatted_emoji, value)
            return True
        except ValueError:
            return False

    def add_many(self, options: List[Tuple[MultiEmoji, Any]]) -> bool:
        """
        Adds multiple options to a reaction menu.
        :param options: The list of tuple of Emoji, Value pairs to add.
        :return: A boolean of if all the options were added.
        """
        total_success = True
        for emoji, value in options:
            total_success = total_success and self.add_option(emoji, value)
        return total_success

    def remove_option(self, emoji: Any) -> bool:
        """
        Removes a single option from the reaction menu.
        :param emoji: The emoji of the option to remove.
        :return: A boolean of if the option with the given emoji was removed.
        """
        try:
            formatted_emoji = MultiEmoji(emoji)
            return self.options.pop(formatted_emoji.emoji_id, None) is not None
        except ValueError:
            return False

    def remove_many(self, options: List) -> bool:
        """
        Remove more than one option from the reaction menu.
        :param options: The list of emojis to remove the options of.
        :return: A boolean of if all the removals were successful.
        """
        total_success = True
        for option in options:
            total_success = total_success and self.remove_option(option)
        return total_success

    async def update_reactions(self):
        """
        Updates the reactions on the message. If the reaction menu is disabled, remove all reactions.
        If the reaction menu is enabled, ensure that only valid options are reactions in the message, and add any
        missing options as reactions.
        """
        if not self.message:
            raise ValueError(f"Unable to add reactions to '{self.message}' message")

        if not self.enabled:
            await self.message.clear_reactions()
        else:
            emojis_missing = list(self.options.keys())
            for reaction in self.message.reactions:
                emoji = MultiEmoji(reaction.emoji)
                if emoji.emoji_id in emojis_missing:
                    emojis_missing.remove(emoji.emoji_id)
                else:
                    await reaction.clear()

            for emoji in emojis_missing:
                try:
                    await self.message.add_reaction(self.options.get(emoji).emoji.discord_emoji)
                except HTTPException:
                    pass

    def _update_reaction_counts(self):
        for reaction in self.message.reactions:
            emoji = MultiEmoji(reaction.emoji)
            if emoji.emoji_id in self.options:
                self.options.get(emoji.emoji_id).reaction_count = reaction.count

    async def update_message(self):
        """
        Update the contents of the message with the current state of the reaction menu.
        """
        if not self.message:
            raise ValueError(f"Unable to update message of type '{self.message}'")

        new_embed = self.generate_embed()
        await self.message.edit(embed=new_embed)
        self.message = await self.message.channel.fetch_message(self.id)
        await self.update_reactions()

    async def enable_menu(self, bot_instance):
        """
        Enables a reaction menu. This removes the adds the appropriate event listeners for on_react_add and
        on_react_remove, as well as ensures that only the emojis for valid options are reactions to the message.
        :param bot_instance: The instance of the bot running.
        """
        if not self.message:
            raise ValueError(f"Unable to enable reaction menu with message of '{self.message}'")

        if not self.enabled:
            self.enabled = True
            await self.update_message()
            if self.react_add_func is not None:
                bot_instance.add_listener(self.on_react_add, "on_raw_reaction_add")
            if self.react_remove_func is not None:
                bot_instance.add_listener(self.on_react_remove, "on_raw_reaction_remove")

    async def disable_menu(self, bot_instance):
        """
        Disables a reaction menu. This removes the listeners for on_react_add and on_react_remove.
        :param bot_instance: The instance of the bot running.
        """
        if not self.message:
            raise ValueError(f"Unable to disable reaction menu with message of '{self.message}'")

        if self.enabled:
            self.enabled = False
            await self.update_message()
            if self.react_add_func is not None:
                bot_instance.remove_listener(self.on_react_add, "on_raw_reaction_add")
            if self.react_remove_func is not None:
                bot_instance.remove_listener(self.on_react_remove, "on_raw_reaction_remove")

    async def finalise_and_send(self, bot_instance, text_channel):
        """
        Create the embed for the current state of the reaction menu and send the message.
        :param bot_instance: The instance of the bot running.
        :param text_channel: The text channel to send the message to.
        """
        self.message = await text_channel.send(content="​")
        self.id = self.message.id
        self._channel_id = text_channel.id
        if self.auto_enable:
            await self.enable_menu(bot_instance)
        else:
            self.enabled = True  # self.enabled must be first set to True so that self.disable_menu runs as intended.
            await self.disable_menu(bot_instance)

    async def on_react_add(self, payload) -> Any:
        """
        The function that runs when a reaction is added to any message.
        :param payload: The payload of the raw reaction event.
        :return: None if the reaction is invalid or not for this reaction menu, or the result of self.react_add_func.
        """
        if payload is None:
            return None

        if self.enabled and self.react_add_func and not payload.member.bot and payload.message_id == self.id:
            return await self.react_add_func(payload)
        return None

    async def on_react_remove(self, payload) -> Any:
        """
        The function that runs when a reaction is removed from any message.
        :param payload: The payload of the raw reaction event.
        :return: None if the reaction is invalid or not for this reaction menu, or the result of self.react_remove_func.
        """
        if payload is None:
            return None

        if self.enabled and self.react_remove_func and payload.message_id == self.id:
            return await self.react_remove_func(payload)
        return None


class ReactableOption:

    def __init__(self, emoji: MultiEmoji, value: Any, description=None, reaction_count=0):
        self._emoji = emoji
        self._value = self._format_value(value)
        self._description = description
        self._reaction_count = reaction_count

    @classmethod
    def from_dict(cls, data: Dict):
        emoji = MultiEmoji(data.get("emoji"))
        value = data.get("value")
        description = data.get("description")
        try:
            reaction_count = int(data.get("reaction_count"))
        except ValueError:
            reaction_count = 0
        return ReactableOption(emoji, value, description, reaction_count)

    def to_dict(self) -> Dict:
        data = {"emoji": self._emoji.to_dict(),
                "value": self._value,
                "description": self._description,
                "reaction_count": int(self._reaction_count),
                }

        return data

    def __str__(self) -> str:
        return f"{self.emoji.discord_emoji} **—** {self.value}"

    def __repr__(self) -> str:
        return f"Emoji: {self.emoji.discord_emoji}\n Value: {self.value!r}\n Description: {self.description!r}"

    @staticmethod
    def _format_value(value):
        if isinstance(value, Role):
            return str(value.mention)
        elif isinstance(value, GuildChannel):
            return str(value.mention)
        else:
            return str(value)

    @property
    def value(self):
        return self._value

    @property
    def emoji(self):
        return self._emoji

    @property
    def description(self):
        return self._description

    @property
    def reaction_count(self):
        return self._reaction_count

    @reaction_count.setter
    def reaction_count(self, value):
        self._reaction_count = value

    def get_emoji(self) -> MultiEmoji:
        """
        Get the emoji used to react for this option.
        :return: A MultiEmoji representing this reaction option.
        """
        return self.emoji

    def get_value(self) -> Any:
        """
        Get the value of this reaction option.
        :return: Get the value of this reaction option.
        """
        return self.value

    def get_description(self) -> str:
        """
        Get the extra details of this reaction option.
        :return: A string that represents any extra details regarding this reaction option.
        """
        return self.description

    def add_reaction(self, count: int = 1) -> int:
        """
        Increase the number of reactions on this reaction option.
        :param count: The number of reactions to increase by.
        :return: The number of reactions after the change.
        """
        self._reaction_count += count
        return self.reaction_count

    def remove_reaction(self, count: int = 1) -> int:
        """
        Reduce the number of reactions on this reaction option.
        :param count: The number of reactions to reduce by.
        :return: The number of reactions after the change.
        """
        self._reaction_count -= count
        return self.reaction_count
