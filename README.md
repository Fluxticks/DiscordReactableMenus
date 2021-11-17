# DiscordReactableMenus
<div align=left>  
    <img src="https://img.shields.io/badge/min%20python%20version-3.8.0-green?style=flat-square" />    
</div>  

`DiscordReactableMenus` is a simple package that enables the creation of discord messages which can perform automated actions when users react to the message.
The intention is for this package to be used inside a `Discord.py` bot, and its function customised to the needs of the commands.
Some examples of possible uses are:
- Role reaction menus
- Polls for user votes

To use this in your bot, add the following import line:
```python
from ReactableMenu import ReactableMenu
```
The easiest option to get a ReactableMenu to perform an action is to first define a function (this must be `async`), which takes 1 argument, the `RawReactionActionEvent` payload:
```python
async def custom_reaction_added_function(payload):
    pass

async def custom_reaction_removed_function(payload):
    pass
```
and then when creating your ReactableMenu, give it the following kwargs:
```python
reaction_menu = ReactableMenu(*args, add_func=custom_reaction_added_function, remove_func=custom_reaction_removed_function, **kwargs)
```
You do not need to have a function defined for both events, as you may only want to react to the `on_raw_reaction_add` or only the `on_raw_reaction_remove`.

The other option is to go for a more in depth implementation by creating a subclass of the `ReactableMenu` class:
```python
from ReactableMenu import ReactableMenu

class CustomMenu(ReactableMenu):
    
    def __init__(self, *args, **kwargs):
        kwargs["add_func"] = self.react_add_func
        kwargs["remove_func"] = self.react_remove_func
        super().__init__(*args, **kwargs)

    async def react_add_func(self, payload):
        pass

    async def react_remove_func(self, payload):
        pass
```
Going the route of a subclass will allow further customisation of things such as appearance.
An important note is that the `to_dict()` and `from_dict()` methods may need to be extended for menu serial/deserialization if extra attributes/properties are added that need to be saved.
The ReactableMenu has the following functions that can be overridden for appearance customisation:
- `def generate_title()` , creates the title element of the Discord Embed object.
- `def generate_description()` , creates the value element of the Discord Embed object.
- `def generate_option_field()` , creates the name, value tuple to be given to a field element in a Discord Embed object.
- `def generate_footer_text()` , creates the footer element of the Discord Embed object.
- `def generate_colour()` , creates the colour element of the Discord Embed object.
- `def generate_embed()` , creates the Discord Embed object based on the above functions.

If you have any saved ReactableMenus from v1 of this packaged, the saved states can be converted to the new v2 implementation using `helpers.convert_v1_to_v2` function, which will output the corresponding v2 dictionary from a v1 dictionary.

## Contributing
Any suggestions regarding changes are welcome, so feel free to create a Fork and then create a PR.
