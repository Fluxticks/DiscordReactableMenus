from discord import PartialEmoji
from discord.ext import commands

from ExampleMenus import PollReactMenu
from examplelib.reactable_lib import get_all_options, get_menu


class SimpleVotingCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.voting_menus = {}

    @commands.group(invoke_without_command=True)
    async def vote(self, context: commands.Context):
        pass

    @vote.error
    async def vote_command_error(self, context: commands.Context, error: commands.CommandError):
        pass

    @vote.command(name="make-poll")
    async def voting_menu(self, context: commands.Context, title: str = None, description: str = None):
        message_contents = context.message.content
        menu_options = get_all_options(message_contents.split("\n")[1:])

        voting_menu = PollReactMenu(title=title, description=description)

        voting_menu.add_many(menu_options)

        await voting_menu.finalise_and_send(self.bot, context.channel)

        self.voting_menus[voting_menu.id] = voting_menu

    @vote.command(name="add-option")
    async def add_voting_option(self, context: commands.Context, emoji: PartialEmoji, descriptor: str, menu_id: str = None):

        voting_menu: PollReactMenu = get_menu(self.voting_menus, menu_id)

        if voting_menu is None:
            await context.send(f"Could not find a Voting Menu with the ID: {menu_id}. "
                               f"Perhaps you forgot to surround your descriptor with quotes?")
            return

        voting_menu.add_option(emoji, descriptor)

        await voting_menu.update_message()

    @vote.command("remove-option")
    async def remove_voting_option(self, context: commands.Context, emoji: PartialEmoji, menu_id: str = None):
        voting_menu: PollReactMenu = get_menu(self.voting_menus, menu_id)

        if voting_menu is None:
            if menu_id is None:
                response = "Unable to find latest Voting Menu. Maybe none have been created?"
            else:
                response = f"Could not find a Voting Menu with the ID: {menu_id}."
            await context.send(response)
            return

        voting_menu.remove_option(emoji)

        await voting_menu.update_message()

    @vote.command("disable-menu")
    async def disable_menu(self, context: commands.Context, menu_id: str = None):
        voting_menu: PollReactMenu = get_menu(self.voting_menus, menu_id)

        if voting_menu is None:
            if menu_id is None:
                response = "Unable to find latest Voting Menu. Maybe none have been created?"
            else:
                response = f"Could not find a Voting Menu with the ID: {menu_id}."
            await context.send(response)
            return

        await voting_menu.disable_menu(self.bot)

    @vote.command("enable-menu")
    async def enable_menu(self, context: commands.Context, menu_id: str = None):
        voting_menu: PollReactMenu = get_menu(self.voting_menus, menu_id)

        if voting_menu is None:
            if menu_id is None:
                response = "Unable to find latest Voting Menu. Maybe none have been created?"
            else:
                response = f"Could not find a Voting Menu with the ID: {menu_id}."
            await context.send(response)
            return

        await voting_menu.enable_menu(self.bot)

    @vote.command("toggle-menu")
    async def toggle_menu(self, context: commands.Context, menu_id: str = None):
        voting_menu: PollReactMenu = get_menu(self.voting_menus, menu_id)

        if voting_menu is None:
            if menu_id is None:
                response = "Unable to find latest Voting Menu. Maybe none have been created?"
            else:
                response = f"Could not find a Voting Menu with the ID: {menu_id}."
            await context.send(response)
            return

        await voting_menu.toggle_menu(self.bot)

    @vote.command("delete-menu")
    async def delete_menu(self, context: commands.Context, menu_id: str = None):
        voting_menu: PollReactMenu = get_menu(self.voting_menus, menu_id)

        if voting_menu is None:
            if menu_id is None:
                response = "Unable to find latest Voting Menu. Maybe none have been created?"
            else:
                response = f"Could not find a Voting Menu with the ID: {menu_id}."
            await context.send(response)
            return

        await voting_menu.message.delete()
        self.voting_menus.pop(voting_menu.id)

    @vote.command("get-results")
    async def get_vote_results(self, context: commands.Context, menu_id: str = None):
        voting_menu: PollReactMenu = get_menu(self.voting_menus, menu_id)

        if voting_menu is None:
            if menu_id is None:
                response = "Unable to find latest Voting Menu. Maybe none have been created?"
            else:
                response = f"Could not find a Voting Menu with the ID: {menu_id}."
            await context.send(response)
            return

        results = voting_menu.generate_results()

        await context.send(embed=results)

    @vote.command("toggle-ids")
    async def toggle_showing_ids(self, context: commands.Context):
        for menu_id in self.voting_menus:
            voting_menu = self.voting_menus.get(menu_id)
            voting_menu.toggle_footer()
            await voting_menu.update_message()


def setup(bot):
    bot.add_cog(SimpleVotingCog(bot))
