import setuptools

setuptools.setup(
        name="DiscordReactableMenus",
        version="0.1",
        description="A useful tool for creating menus in discord.py bots",
        author="Fluxticks",
        author_email="benjigarment.appdev@gmail.com",
        url="https://github.com/Fluxticks/DiscordReactableMenus",
        classifiers=[
                "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
                "Programming Language :: Python :: 3.8"
        ],
        packages=["DiscordReactableMenus"],
        install_requires=[
                "discord.py[voice]",
                "emoji"
        ]
)
