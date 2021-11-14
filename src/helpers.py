import shlex

from .ReactableMenu import ReactableMenu


def get_options(command_name, message_contents):
    """
    Get the title, description and any options given in a command message
    :param command_name: The string for the command used.
    :param message_contents: The contents of the message.
    :return: A dictionary containing the title, description and the options for a reaction menu.
    """
    # starting from after the command, split the message into its sections
    message_contents = message_contents[message_contents.index(command_name)+len(command_name):].strip()
    if message_contents.count('"') % 2 != 0:
        raise InvalidCharacters(
            message_contents,
            message="There was an incorrect number of double quotes given. Check that all quotes are properly closed."
        )

    sections = shlex.split(message_contents)
    if len(sections) < 2:
        raise InvalidCharacters(
            message_contents,
            message="There was either no title or no description passed to the command! "
                    "Check to ensure that each is separated by a space and that multi-word options are enclosed "
                    "with quotes."
        )

    # first and second item will be the title and description respectively
    title = sections.pop(0).strip()
    if "<@&" in title or "<#" in title or "<:" in title:
        raise InvalidCharacters(
            title,
            message="Title cannot contain a Channel mention, a Role mention or a custom discord emoji"
        )

    description = sections.pop(0).strip()
    data = {"title": title, "description": description, "options": []}

    for i in range(0, len(sections), 2):
        if i+1 < len(sections):
            emoji = sections[i]
            value = sections[i+1]
            data["options"].append((emoji, value))

    return data


def menu_from_options(data, menu_type=ReactableMenu, **kwargs):
    """
    Create a menu from a dictionary containing the title, description and a list of tuple options.
    :param data: The data containing the title, description and options.
    :param menu_type: The type of menu to create. Defaults to the basic ReactableMenu
    :param kwargs: Any extra options to pass to the ReactableMenu constructor.
    :return: A ReactableMenu of type menu_type.
    """
    title = data.pop("title")
    description = data.pop("description")
    kwargs.pop("menu_type", None)
    menu = menu_type(title=title, description=description, **kwargs)
    for item in data.get("options"):
        emoji, value = item
        menu.add_option(emoji, value)
    return menu


def convert_v1_to_v2(v1_dict):
    """
    A function to convert a v1 reaction menu to be compatible with the new v2 implementation. This mostly involves
    converting the options to work correctly.
    :param v1_dict: The saved dictionary of a v1 reaction menu.
    """
    v2_dict = v1_dict.copy()
    options = []
    for option_id in v2_dict.get("options").keys():
        option = v2_dict.get("options").get(option_id)
        emoji = option.get("emoji")
        value = option.get("descriptor")
        description = option.get("description", None)
        reaction_count = option.get("reaction_count", 0)
        options.append({"emoji": emoji, "value": value, "description": description, "reaction_count": reaction_count})
    v2_dict["options"] = options
    return v2_dict


class InvalidCharacters(Exception):

    def __init__(self, attempted_characters, message="The string contained illegal characters"):
        self.attempted_characters = attempted_characters
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.attempted_characters} -> {self.message}"
