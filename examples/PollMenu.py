from discord import Embed

from src.EmojiHandler import MultiEmoji
from src.ReactableMenu import ReactableMenu, ReactableOption

BAR_MAX_LENGTH = 10
NO_VOTES_STRING = "No votes received!"


class PollMenu(ReactableMenu):

    def __init__(self, **kwargs):
        kwargs["add_func"] = self.add_vote_event
        kwargs["remove_func"] = self.remove_vote_event
        super().__init__(**kwargs)
        self.start_time = kwargs.pop("start_time", None)
        self.total_votes = kwargs.pop("vote_count", 0)
        self.single_choice = kwargs.pop("single_choice", False)
        self.members_voted = []

    def to_dict(self):
        data = super().to_dict()
        data["start_time"] = self.start_time
        data["single_choice"] = self.single_choice
        return data

    async def initialise(self, bot):
        if not await super().initialise(bot):
            return False

        votes, members = await self._get_current_votes()
        self.total_votes = votes
        self.members_voted = members

        return True

    async def _get_current_votes(self):
        reactions = self.message.reactions
        members = set()
        votes = 0
        for reaction in reactions:
            emoji = MultiEmoji(reaction.emoji)
            if emoji.emoji_id in self.options:
                votes += reaction.count
                users = [x.id for x in await reaction.users().flatten()]
                members.update(users)

        return votes, list(members)

    def generate_results(self):
        if self.total_votes > 0:
            string = self.generate_results_string()
        else:
            string = NO_VOTES_STRING

        title = self.generate_title()
        description = self.generate_description()
        embed = Embed(title=f"Results for — {title}", description=description)
        embed.add_field(name="Results", value=string, inline=False)
        return embed

    def generate_results_string(self):
        max_length = self._get_longest_option()
        winner_ids, winning_votes = self._get_winning_option()
        winning_strings = "\n".join(self.generate_bar(x, max_length, winning_votes, is_winner=True) for x in winner_ids)
        remaining_options = self.options.copy()
        for winner in winner_ids:
            remaining_options.pop(winner)

        other_strings = ""
        for key, _ in sorted(remaining_options.items(), key=lambda x: x[1].reaction_count, reverse=True):
            other_strings += "\n" + self.generate_bar(key, max_length, winning_votes)

        string = f"```\n{winning_strings}{other_strings}```"
        return string

    def generate_bar(self, option_id, longest_option, winning_votes, is_winner=False):
        option: ReactableOption = self.options.get(option_id)
        bar_length = int((option.reaction_count / winning_votes) * BAR_MAX_LENGTH)
        return f"{option.value}{' ' * (longest_option - len(option.value))} | {'=' * bar_length}" \
               f"{'' if option.reaction_count else ' '}{'🏆' if is_winner else ''} +{option.reaction_count} " \
               f"Vote{'' if option.reaction_count == 1 else 's'}"

    def _get_longest_option(self):
        longest = -1
        for option in self.options.values():
            if len(option.value) > longest:
                longest = len(option.value)
        return longest

    def _get_winning_option(self):
        winner = ([], -1)
        for emoji_id, option in self.options.items():
            if option.reaction_count > winner[1]:
                winner = ([emoji_id], option.reaction_count)
            elif option.reaction_count == winner[1]:
                winner[0].append(emoji_id)
        return winner

    async def add_vote_event(self, payload):
        emoji_reaction = MultiEmoji(payload.emoji)

        if emoji_reaction.emoji_id not in self.options:
            await self.message.remove_reaction(payload.emoji, payload.member)
            return False

        self.options[emoji_reaction.emoji_id].add_reaction()
        self.total_votes += 1

        if self.single_choice and payload.member.id in self.members_voted:
            # As the below remove_reaction triggers the remove_vote_event, the user id and an extra vote must be added
            # before the vote is removed.
            self.members_voted.append(payload.member.id)
            await self.message.remove_reaction(payload.emoji, payload.member)
            return False

        self.members_voted.append(payload.member.id)
        return True

    async def remove_vote_event(self, payload):
        emoji_reaction = MultiEmoji(payload.emoji)

        if emoji_reaction.emoji_id not in self.options:
            return False

        if payload.user_id not in self.members_voted:
            return False

        self.options[emoji_reaction.emoji_id].remove_reaction()
        self.total_votes -= 1
        self.members_voted.remove(payload.user_id)
        return False
