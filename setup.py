import setuptools

setuptools.setup(
        name="DiscordReactableMenus",
        description="A useful tool for creating menus in discord.py bots",
        author="Fluxticks",
        url="https://github.com/Fluxticks/DiscordReactableMenus",
        classifiers=[
                "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
                "Programming Language :: Python :: 3.8"
        ],
        packages=["src", "examples"],
        install_requires=[
                "discord.py[voice]",
                "emoji"
        ],
        python_requires="~=3.8"
)
