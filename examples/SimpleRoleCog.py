from discord import PartialEmoji
from discord.ext import commands

from ExampleMenus import RoleReactMenu
from examplelib.reactable_lib import get_all_options, get_menu


class SimpleRoleCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.reaction_menus = {}

    @commands.group(invoke_without_command=True)
    async def roles(self, context: commands.Context):
        pass

    @roles.error
    async def roles_command_error(self, context: commands.Context, error: commands.CommandError):
        pass

    @roles.command(name="make-menu")
    async def reaction_menu(self, context: commands.Context, title: str = None, description: str = None):
        message_contents = context.message.content
        menu_options = get_all_options(message_contents.split("\n")[1:])

        role_menu = RoleReactMenu(title=title, description=description)

        role_menu.add_many(menu_options)

        await role_menu.finalise_and_send(self.bot, context.channel)

        self.reaction_menus[role_menu.id] = role_menu

    @roles.command("add-option")
    async def add_role_option(self, context: commands.Context, emoji: PartialEmoji, descriptor: str, menu_id: str = None):
        role_menu: RoleReactMenu = get_menu(self.reaction_menus, menu_id)

        if role_menu is None:
            await context.send(f"Could not find a Role Reaction Menu with the ID: {menu_id}. "
                               f"Perhaps you forgot to surround your descriptor with quotes?")
            return

        role_menu.add_option(emoji, descriptor)

        await role_menu.update_message()

    @roles.command("remove-option")
    async def remove_role_option(self, context: commands.Context, emoji: PartialEmoji, menu_id: str = None):
        role_menu: RoleReactMenu = get_menu(self.reaction_menus, menu_id)

        if role_menu is None:
            if menu_id is None:
                response = "Unable to find latest Role Reaction Menu. Maybe none have been created?"
            else:
                response = f"Could not find a Role Reaction Menu with the ID: {menu_id}."
            await context.send(response)
            return

        role_menu.remove_option(emoji)

        await role_menu.update_message()

    @roles.command("disable-menu")
    async def disable_menu(self, context: commands.Context, menu_id: str = None):
        role_menu: RoleReactMenu = get_menu(self.reaction_menus, menu_id)

        if role_menu is None:
            if menu_id is None:
                response = "Unable to find latest Role Reaction Menu. Maybe none have been created?"
            else:
                response = f"Could not find a Role Reaction Menu with the ID: {menu_id}."
            await context.send(response)
            return

        await role_menu.disable_menu(self.bot)

    @roles.command("enable-menu")
    async def enable_menu(self, context: commands.Context, menu_id: str = None):
        role_menu: RoleReactMenu = get_menu(self.reaction_menus, menu_id)

        if role_menu is None:
            if menu_id is None:
                response = "Unable to find latest Role Reaction Menu. Maybe none have been created?"
            else:
                response = f"Could not find a Role Reaction Menu with the ID: {menu_id}."
            await context.send(response)
            return

        await role_menu.enable_menu(self.bot)

    @roles.command("toggle-menu")
    async def toggle_menu(self, context: commands.Context, menu_id: str = None):
        role_menu: RoleReactMenu = get_menu(self.reaction_menus, menu_id)

        if role_menu is None:
            if menu_id is None:
                response = "Unable to find latest Role Reaction Menu. Maybe none have been created?"
            else:
                response = f"Could not find a Role Reaction Menu with the ID: {menu_id}."
            await context.send(response)
            return

        await role_menu.toggle_menu(self.bot)

    @roles.command("delete-menu")
    async def delete_menu(self, context: commands.Context, menu_id: str = None):
        role_menu: RoleReactMenu = get_menu(self.reaction_menus, menu_id)

        if role_menu is None:
            if menu_id is None:
                response = "Unable to find latest Role Reaction Menu. Maybe none have been created?"
            else:
                response = f"Could not find a Role Reaction Menu with the ID: {menu_id}."
            await context.send(response)
            return

        await role_menu.message.delete()
        self.reaction_menus.pop(role_menu.id)

    @roles.command("toggle-ids")
    async def toggle_showing_ids(self, context: commands.Context):
        for menu_id in self.reaction_menus:
            role_menu = self.reaction_menus.get(menu_id)
            role_menu.toggle_footer()
            await role_menu.update_message()


def setup(bot):
    bot.add_cog(SimpleRoleCog(bot))
