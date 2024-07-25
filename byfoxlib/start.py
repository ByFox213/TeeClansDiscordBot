from os import listdir, environ

from .main import Loads
from .model import Lang
from config import TOKEN


def get_cogs_file(cogs_dir: str = None) -> list:
    rt = []
    if cogs_dir is None:
        cogs_dir = 'cogs'
    for filename in listdir(cogs_dir):
        if filename.endswith('.py'):
            rt.append(filename[:-3])
    return rt


def get_token() -> str:
    token = environ.get('DISCORD_TOKEN', None)
    if token is not None:
        return token
    if TOKEN:
        return TOKEN
    raise ValueError("Значени Token является None")


def load_cog(bot) -> None:  # ignore: W0613
    for file in get_cogs_file('cogs'):
        exec(f"from cogs.{file} import {file}")
        exec(f"bot.add_cog({file}(bot=bot))")


def get_language() -> dict[str, Lang]:
    lang = {}
    for filename in listdir("./language"):
        if not filename.endswith('.yaml') or filename == "commands.yaml":
            continue
        lang[filename[:-5]] = Loads.loads_yaml(f"./language/{filename}", Lang)
    return lang
