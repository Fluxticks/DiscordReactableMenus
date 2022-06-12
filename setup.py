import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.readlines()

setuptools.setup(
    name="DiscordReactableMenus",
    version="3.0.0",
    author="Fluxticks",
    author_email="benjigarment.appdev@gmail.com",
    description="Interactable Discord messages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Fluxticks/DiscordReactableMenus",
    project_urls={
        "Bug Tracker": "https://github.com/Fluxticks/DiscordReactableMenus/issues"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GPL-3.0 License",
        "Operating System :: OS Independant",
    ],
    install_requires=requirements,
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)
