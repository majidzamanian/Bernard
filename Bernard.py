"""
Bernard Version 1.0

Bernard is an assistant and application to customize the terminal to do the tasks you need,
which can be run on all bash Unix shells. Bernard consists of a script reader and a directory of scripts.
With the help of script reader, Bernard can read and execute smaller programs by Python interpreter.
In this way, it will be easier to develop Bernard by writing small and separate programs.

Bernard is open source under the MIT license and you can easily use it
and make any changes you like and share it with others.

Bernard github repository:
https://github.com/mimseyedi/Bernard
"""


import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime
from rich.console import Console
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter


def init():
    screen = Console()
    subprocess.run(["clear"])

    with open("settings.json", "r") as settings_file:
        settings = json.load(settings_file)
        scripts_path = settings["path_settings"]["scripts_path"]
        home_path = settings["path_settings"]["home_path"]

    os.chdir(home_path)
    season = PromptSession(history=InMemoryHistory())

    while True:
        current_dir = list()
        current_dir.append(os.getcwd().split('/'))
        items = os.listdir(os.getcwd())

        for item in items:
            if item.startswith("."):
                items.remove(item)

        items = map(lambda item: r'\ '.join(item.split(" ")), items)

        autocompleter = WordCompleter(sorted(items), ignore_case=False)

        cmd_input = season.prompt(f'➜ {current_dir[0][-1]}: ', completer=autocompleter).lstrip().split()

        if len(cmd_input) > 0:
            if cmd_input[0] not in ["home", "goto", "back", "exit"] :
                main_command = cmd_input[0] + '.py'
                parameters = ' '.join(cmd_input[1:])

                if os.path.exists(f'{scripts_path}/{main_command}'):
                    os.system(f'{sys.executable} {scripts_path}/{main_command} {parameters}')
                else:
                    screen.print(f"Error: '{main_command[:-3]}' command not found!", style="red")

            elif cmd_input[0] == "home":
                if len(cmd_input) == 1:
                    os.chdir(home_path)
                elif len(cmd_input) == 2 and cmd_input[1] == "-h":
                    screen.print("With the home command, you can goto home location.", style="green")
                else:
                    sceen.print("Error: Unknown parameters!", style="red")

            elif cmd_input[0] == "goto":
                if len(cmd_input) == 1:
                    screen.print("Error: You must choose a path!", style="red")
                elif len(cmd_input) == 2 and cmd_input[1] == "-h":
                    screen.print("With the goto command, you can change path location and move between directories.",
                                  style="green")
                elif len(cmd_input) == 2 and cmd_input[1] != "-h":
                    if os.path.exists(f'{os.getcwd()}/{cmd_input[1]}'):
                        if os.path.isdir(f'{os.getcwd()}/{cmd_input[1]}'):
                            os.chdir(f'{os.getcwd()}/{cmd_input[1]}')
                        else:
                            screen.print("Error: you must select a directory!", style="red")
                    else:
                        screen.print("Error: path not found!", style="red")

            elif cmd_input[0] == "back":
                if len(cmd_input) == 1:
                    os.chdir("..")
                elif len(cmd_input) == 2 and cmd_input[1] == "-h":
                    screen.print("With the back command, you can change path location and back to last path.",
                                  style="green")
                else:
                    screen.print("Error: Unknown parameters!", style="red")

            elif cmd_input[0] == 'exit': break


if __name__ == "__main__":
    init()
