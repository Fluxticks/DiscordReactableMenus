# DiscordReactableMenus
<div align=left>  
    <img src="https://img.shields.io/badge/min%20python%20version-3.8.0-green?style=flat-square" />    
</div>  

`DiscordReactableMenus` is a simple package that eases the creation of interactable messages in a Discord server.
This package has base class menus that use Discord Buttons, Discord Select Menus as well as the traditional reactions.
The intention for this package is to be used in a [Discord.py](https://github.com/Rapptz/discord.py) bot. 

Any level of a reactable menu can be extended through subclasses, however the three most useful with most of the functionality implemented are the `ButtonMenu`, `SelectMenu` and the `ReactionMenu`.
These classes handle interactions with Discord Buttons, Discord Select Menus and traditional reactions respectively.
Some examples of possible extensions of these classes are:
- Role reaction menus
- Polls for user votes
- Action confirmation/cancellation menu

To use the base implementations in your bot, add one or multiple of the following import statements:
```python
from ReactableMenu import ButtonMenu
from ReactableMenu import SelectMenu
from ReactableMenu import ReactionMenu
```

### Button Menu
```python
async def on_button_press(interaction: discord.Interaction):
    button_id = interaction.data.get("custom_id")
    # Perform some logic based on which button was pressed...

button_menu = ButtonMenu(..., interaction_handler=on_button_press)
```
### Select Menu
```python
async def on_select_menu(interaction: discord.Interaction):
    options_selected = interaction.data.get("values")
    for item in options_selected:
        option_id = item.get("custom_id")
        # Perform some logic based on which options were selected...

select_menu = SelectMenu(..., interaction_handler=on_select_menu)
```
### Reaction Menu
```python
async def on_react_add(payload: discord.RawReactionActionEvent):
    emoji_reacted_with = payload.emoji
    # Perform some logic based on which emoji was reacted with...

async def on_react_remove(payload: discord.RawReactionActionEvent):
    emoji_reaction_removed = payload.emoji
    # Perform some logic based on which reaction was removed...

async def generic_reaction_event(paylod: discord.RawReactionActionEvent):
    emoji_used = payload.emoji
    # Handle both reactions added and removed in the same function

reaction_menu = ReactionMenu(react_add_handler=on_react_add, react_remove_handler=on_react_remove)
other_menu = ReactionMenu(react_add_handler=generic_reaction_event, react_remove_handler=generic_reaction_event)
```

If your menu needs more attributes to keep track of more data you can subclass one of `ButtonMenu`, `SelectMenu`, `ReactionMenu` or even `InteractionMenu`.
Going the route of a subclass will allow further customisation of things such as appearance.
An important note is that the `to_dict()` and `from_dict()` methods may need to be extended for menu serial/deserialization if extra attributes/properties are added that need to be saved.
The ReactableMenu has the following functions that can be overridden for appearance customisation:
- `def generate_title()` , creates the title element of the Discord Embed object.
- `def generate_description()` , creates the value element of the Discord Embed object.
- `def generate_option_field()` , creates the name, value tuple to be given to a field element in a Discord Embed object.
- `def generate_footer_text()` , creates the footer element of the Discord Embed object.
- `def generate_colour()` , creates the colour element of the Discord Embed object.
- `def build_embed()` , creates the Discord Embed object based on the above functions.
- `def build_view()` , creates the buttons used to interact with the menu.

## Contributing
Any suggestions regarding changes are welcome, so feel free to create a Fork and then create a PR.
