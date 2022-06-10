# DiscordReactableMenus
<div align=left>  
    <img src="https://img.shields.io/badge/min%20python%20version-3.8.0-green?style=flat-square" />    
</div>  

`DiscordReactableMenus` is a simple package that enables the creation of discord messages which can perform automated actions when users use the given Discord Component Buttons.
The intention is for this package to be used inside a [Discord.py](https://github.com/Rapptz/discord.py) bot, and for the functionality of the base `ReactableMenu` to be extended for a specific use.
Some examples of possible uses are:
- Role reaction menus
- Polls for user votes
- Action confirmation/cancellation menu

To use this in your bot, add the following import line:
```python
from ReactableMenu import ReactableMenu
```
To customise the action of a ReactableMenu upon being interacted with, create an `async` function that takes two arguments, an instance of a `ReactableMenu` and a [discord.Interaction](https://discordpy.readthedocs.io/en/latest/interactions/api.html?highlight=command#discord.Interaction) object:
```python
async def custom_interaction_handler(menu: ReactableMenu, interaction: discord.Interaction):
    pass
```
and then when creating your ReactableMenu, give it the following kwargs:
```python
reaction_menu = ReactableMenu(*args, on_button_click=custom_interaction_handler, **kwargs)
```
By default the ReactableMenu will automatically handle if the interaction is intended for the given menu and the enable/disable interaction buttons. This means that the interactions for the options in the menu must still be handled.

More functionality can be gained by subclassing the `ReactableMenu` class and overriding its methods:
```python
from ReactableMenu import ReactableMenu

class CustomMenu(ReactableMenu):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    ...
```
Going the route of a subclass will allow further customisation of things such as appearance.
An important note is that the `to_dict()` and `from_dict()` methods may need to be extended for menu serial/deserialization if extra attributes/properties are added that need to be saved.
The ReactableMenu has the following functions that can be overridden for appearance customisation:
- `def generate_title()` , creates the title element of the Discord Embed object.
- `def generate_description()` , creates the value element of the Discord Embed object.
- `def generate_option_field()` , creates the name, value tuple to be given to a field element in a Discord Embed object.
- `def generate_footer_text()` , creates the footer element of the Discord Embed object.
- `def generate_colour()` , creates the colour element of the Discord Embed object.
- `def build_embed()` , creates the Discord Embed object based on the above functions.
- `def buidl_view()` , creates the buttons used to interact with the menu.

## Contributing
Any suggestions regarding changes are welcome, so feel free to create a Fork and then create a PR.
