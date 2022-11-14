import os
import sys
import json
import hashlib
import subprocess
from getpass import getpass
try:
    import requests
except ImportError as module:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"], stdout=subprocess.DEVNULL)
finally:
    import requests
try:
    from bs4 import BeautifulSoup
except ImportError as package:
    subprocess.run([sys.executable, "-m", "pip", "install", "beautifulsoup4"], stdout=subprocess.DEVNULL)
finally:
    from bs4 import BeautifulSoup
try:
    from clint.textui import progress
except ImportError as module:
    subprocess.run([sys.executable, "-m", "pip", "install", "clint"], stdout=subprocess.DEVNULL)
finally:
    from clint.textui import progress
try:
    from rich.console import Console
except ImportError as module:
    subprocess.run([sys.executable, "-m", "pip", "install", "rich"], stdout=subprocess.DEVNULL)
finally:
    from rich.console import Console
    screen = Console()


path_of_file = os.path.abspath(__file__).split("/")
base_path = '/'.join(path_of_file[1:-2])
scripts_path = '/'.join(path_of_file[1:-1])

with open(f"/{base_path}/settings.json", "r") as settings_file:
    settings = json.load(settings_file)


guide_message = """With the scripts command, you can perform and manage tasks related to scripts.

Parameters:
scripts -> show all scripts installed
install -> scripts install <script_name>
uninstall -> scripts uninstall <script_name>
update -> scripts update <script_name>
-u -> show available updates
-n -> show new scripts"""


def authentication(password):
    sha_256 = hashlib.sha256()
    sha_256.update(str(password).encode("UTF-8"))
    hashed_password = sha_256.hexdigest()
    return True if hashed_password == settings["password"] else False


def download_script(url, script_name):
    script = requests.get(url, stream=True)
    with open(f"/{scripts_path}/{script_name}.py", "wb") as script_file:
        total_length = int(script.headers.get('content-length'))
        for chunk in progress.bar(script.iter_content(chunk_size=1024),
                                  expected_size=(total_length / 1024) + 1):
            if chunk:
                script_file.write(chunk)
                script_file.flush()


def init():
    if len(sys.argv) == 1:
        scripts = sorted(os.listdir(f"/{scripts_path}"))
        max_length = 0
        for item in scripts:
            if item.endswith(".py"):
                max_length = len(item) if len(item) > max_length else max_length
            else:
                scripts.remove(item)

        screen.print(f"[{len(scripts)} Installed scripts]: ", style="bold yellow")

        index = 0
        while index < len(scripts):
            space = " " * (max_length - len(scripts[index]))
            screen.print(scripts[index][:-3], end=f"{space} \t\t\t", style="green")
            if index + 1 < len(scripts):
                screen.print(scripts[index + 1][:-3], style="green")
            index += 2

        if len(scripts) % 2 != 0: print()

    elif len(sys.argv) == 2 and sys.argv[1] == "-h":
        screen.print(guide_message, style="green")

    elif len(sys.argv) == 2 and sys.argv[1] == "-n":
        installed_scripts = sorted(os.listdir(f"/{scripts_path}"))
        request = requests.get("https://github.com/mimseyedi/Bernard/tree/master/scripts")
        soup = BeautifulSoup(request.text, "lxml")

        items = soup.findAll("div", class_="flex-auto min-width-0 col-md-2 mr-3")
        repo_scripts = [item.text.strip() for item in items if item.text.strip().endswith(".py")]
        new_scripts = [repo_script for repo_script in repo_scripts if repo_script not in installed_scripts]

        if len(new_scripts) > 0:
            max_length = 0
            for item in new_scripts:
                max_length = len(item) if len(item) > max_length else max_length

            screen.print(f"{len(new_scripts)} New scripts are not installed: ", style="bold yellow")

            index = 0
            while index < len(new_scripts):
                space = " " * (max_length - len(new_scripts[index]))
                screen.print(new_scripts[index][:-3], end=f"{space} \t\t\t", style="green")
                if index + 1 < len(new_scripts):
                    screen.print(new_scripts[index + 1][:-3], style="green")
                index += 2
            if len(new_scripts) % 2 != 0: print()
        else:
            screen.print(f"Error: No new script found that is not installed!", style="red")

    elif len(sys.argv) == 2 and sys.argv[1] == "-u":
        scripts = sorted(os.listdir(f"/{scripts_path}"))
        available_updates = list()

        for script in scripts:
            if script.endswith(".py"):
                request = requests.get(
                    f"https://raw.githubusercontent.com/mimseyedi/Bernard/master/scripts/{script}")
                if request.status_code == 200:
                    with open(f"/{scripts_path}/{script}", "r") as current_file:
                        current_script = current_file.read()

                    if current_script != request.text:
                        available_updates.append(script)

        if len(available_updates) > 0:
            max_length = 0
            for item in available_updates:
                max_length = len(item) if len(item) > max_length else max_length

            screen.print(f"{len(available_updates)} Available updates: ", style="bold yellow")

            index = 0
            while index < len(available_updates):
                space = " " * (max_length - len(available_updates[index]))
                screen.print(available_updates[index][:-3], end=f"{space} \t\t\t", style="green")
                if index + 1 < len(available_updates):
                    screen.print(available_updates[index + 1][:-3], style="green")
                index += 2
            if len(available_updates) % 2 != 0: print()
        else:
            screen.print(f"Error: No updates found for scripts!", style="red")

    elif len(sys.argv) == 3 and sys.argv[1] == "install":
        user_password = getpass("Enter password: ")
        if authentication(user_password):
            request = requests.get(f"https://raw.githubusercontent.com/mimseyedi/Bernard/master/scripts/{sys.argv[2]}.py")
            if request.status_code == 200:
                if not os.path.exists(f"/{scripts_path}/{sys.argv[2]}.py"):
                    download_script(
                        f"https://raw.githubusercontent.com/mimseyedi/Bernard/master/scripts/{sys.argv[2]}.py",
                        script_name=sys.argv[2])

                    screen.print(f"The '{sys.argv[2]}' script was successfully installed!", style="green")
                else:
                    screen.print(f"Error: '{sys.argv[2]}' script already exists!", style="red")

            elif request.status_code == 404:
                screen.print(f"Error: '{sys.argv[2]}' script not found!", style="red")
            else:
                screen.print(f"Error: No internet connection!", style="red")
        else:
            screen.print("Error: Authentication failed!", style="red")

    elif len(sys.argv) == 3 and sys.argv[1] == "uninstall":
        user_password = getpass("Enter password: ")
        if authentication(user_password):
            if os.path.exists(f"/{scripts_path}/{sys.argv[2]}.py"):
                ask_to_uninstall = input("Are you sure? (y/n): ").lower()
                if ask_to_uninstall == "y":
                    os.remove(f"/{scripts_path}/{sys.argv[2]}.py")
                    screen.print(f"'{sys.argv[2]}' script was successfully uninstalled!", style="green")
            else:
                screen.print(f"Error: '{sys.argv[2]}' script not found!", style="red")
        else:
            screen.print("Error: Authentication failed!", style="red")

    elif len(sys.argv) == 3 and sys.argv[1] == "update":
        user_password = getpass("Enter password: ")
        if authentication(user_password):
            if os.path.exists(f"/{scripts_path}/{sys.argv[2]}.py"):
                request = requests.get(f"https://raw.githubusercontent.com/mimseyedi/Bernard/master/scripts/{sys.argv[2]}.py")
                if request.status_code == 200:
                    with open(f"/{scripts_path}/{sys.argv[2]}.py", "r") as current_file:
                        current_script = current_file.read()

                    if current_script != request.text:
                        os.remove(f"/{scripts_path}/{sys.argv[2]}.py")
                        download_script(
                            f"https://raw.githubusercontent.com/mimseyedi/Bernard/master/scripts/{sys.argv[2]}.py",
                            script_name=sys.argv[2])

                        screen.print(f"'{sys.argv[2]}' script was successfully updated!", style="green")
                    else:
                        screen.print(f"Error: No updates found for '{sys.argv[2]}' script!", style="red")

                elif request.status_code == 404:
                    screen.print(f"Error: '{sys.argv[2]}' script not found!", style="red")
                else:
                    screen.print(f"Error: No internet connection!", style="red")
            else:
                screen.print(f"Error: '{sys.argv[1]}' script not installed!", style="red")
        else:
            screen.print("Error: Authentication failed!", style="red")

    else:
        screen.print("Error: Unknown parameters!", style="red")


if __name__ == "__main__":
    init()