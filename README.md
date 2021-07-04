# DiscordReactableMenus

<div align=left>  
    <img src="https://img.shields.io/badge/min%20python%20version-3.8.0-green?style=flat-square" />    
</div>  

`DiscordReactableMenus` is a simple package that makes making messages in discord with reactions that perform actions when adding/removing reactions as defining the operation for each of the events. It is also possible, using this package, to create messages with more interesting effects by creating subclasses of the main `ReactableMenu` class provided.



DiscordReactableMenus provides a simple base class in the `src/ReactableMenu.py`, namely `ReactableMenu`. This base class can be used "as is" without modification, with the default action performed when adding or removing a reaction in discord being to do nothing.

The `ReactableMenu` without modification can be given functions to perform when a reaction is added/removed, or can be fully implemented in a subclass for finer control over how reactions are handled. Examples of how `ReactableMenu` can be implemented can be found in `examples/ExampleMenus.py`. There are also examples of these Example Menus being implemented in discord.py cogs:
   - For a role reaction menu look in `SimpleRoleCog.py`
   - For a voting/poll menu look in `SimpleVotingCog.py`

These are just examples of what can be done using the base class of this package, feel free to use, modify or make your own implementations of these examples.

# Contributing
Feel free to fork/make pull requests to suggest changes, this is currently a "first implementation" with only minor testing and optimisations to be made.