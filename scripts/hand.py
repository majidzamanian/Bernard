import os
import sys
import json
import shutil
from pathlib import Path
try:
    from rich.console import Console
except ImportError as module:
    subprocess.run([sys.executable, "-m", "pip", "install", "rich"], stdout=subprocess.DEVNULL)
finally:
    from rich.console import Console
    screen = Console()


guide_message = """With the hand command, you can keep files or directories in memory and select them to move.

Parameters:
get will be select current directory
    <file> <file> <file> ...
drop paste the selected all files
     paste with index of file
-w hand washing -> clean the memory!
-c remove one path by index
-z undo drop action"""


def add_last_drop(actions):
    hand["last_drop"].append(actions)
    with open(Path(scripts_path, ".hand_memory.json"), "w") as hand_file:
        json.dump(hand, hand_file)


def rem_last_drop():
    with open(Path(scripts_path, ".hand_memory.json"), "r") as hand_file:
        hand = json.load(hand_file)

    hand["last_drop"].clear()
    with open(Path(scripts_path, ".hand_memory.json"), "w") as hand_file:
        json.dump(hand, hand_file)


def init():
    global hand, scripts_path
    hand = {"items": [], "last_drop": []}
    path_of_file = Path(__file__)
    scripts_path = path_of_file.parent

    if not Path(scripts_path, ".hand_memory.json").exists():
        with open(Path(scripts_path, ".hand_memory.json"), "w") as hand_file:
            json.dump(hand, hand_file)
    else:
        with open(Path(scripts_path, ".hand_memory.json"), "r") as hand_file:
            hand = json.load(hand_file)

    for index, item in enumerate(hand["items"]):
        if not os.path.exists(item):
            hand["items"].remove(item)
    with open(Path(scripts_path, ".hand_memory.json"), "w") as hand_file:
        json.dump(hand, hand_file)

    if len(sys.argv) == 1:
        with open(Path(scripts_path, ".hand_memory.json"), "r") as hand_file:
            hand = json.load(hand_file)

        if len(hand["items"]) > 0:
            for index, item in enumerate(hand["items"]):
                if os.path.isfile(item):
                    screen.print(f"{index+1} - f - {item}")
                else:
                    screen.print(f"{index + 1} - d - {item}")
        else:
            screen.print("Message: Hand is empty!", style="yellow")

    elif len(sys.argv) == 2 and sys.argv[1] == "-h":
        screen.print(guide_message, style="green")

    elif len(sys.argv) == 2 and sys.argv[1] == "get":
        if os.getcwd() not in hand["items"]:
            hand["items"].append(os.getcwd())
            with open(Path(scripts_path, ".hand_memory.json"), "w") as hand_file:
                json.dump(hand, hand_file)
            screen.print(f"The hand successfully caught '{os.getcwd()}'", style="green")
        else:
            screen.print(f"Error: '{os.getcwd()}' already in the hand!", style="red")

    elif len(sys.argv) > 2 and sys.argv[1] == "get":
        for item in sys.argv[2:]:
            item = Path(item)
            if Path(os.getcwd(), item.name).exists():
                if f"{Path(os.getcwd(), item.name)}" not in hand["items"]:
                    hand["items"].append(f"{Path(os.getcwd(), item.name)}")
                    screen.print(f"The hand successfully caught '{Path(os.getcwd(), item.name)}'", style="green")
                else:
                    screen.print(f"Error: '{Path(os.getcwd(), item.name)}' already in the hand!", style="red")
            else:
                screen.print(f"Error: '{Path(os.getcwd(), item.name)}' not found!", style="red")

        with open(Path(scripts_path, ".hand_memory.json"), "w") as hand_file:
            json.dump(hand, hand_file)

    elif len(sys.argv) == 2 and sys.argv[1] == "drop":
        last_action = []
        for item in hand["items"]:
            item = Path(item)
            if item.is_file():
                if Path(os.getcwd(), item.name).exists():
                    screen.print(f"Error: '{item.name}' already exists!", style="red")
                else:
                    shutil.copyfile(item, item.name)
                    screen.print(f"'{item}' was copied successfully!", style="green")
                    last_action.append(f"{item}")
            else:
                if Path(os.getcwd(), item.name).exists():
                    screen.print(f"Error: '{item.name}' already exists!", style="red")
                else:
                    shutil.copytree(item, item.name)
                    screen.print(f"'{item}' was copied successfully!", style="green")
                    last_action.append(f"{Path(os.getcwd(), item.name)}")

        if len(last_action) > 0:
            add_last_drop(last_action)

    elif len(sys.argv) >= 3 and sys.argv[1] == "drop":
        indexes = sys.argv[2:]

        last_action = []
        for index in indexes:
            if index.isdigit():
                index = int(index) - 1
                item = Path(hand["items"][index])
                if item.is_file():
                    if Path(os.getcwd(), item.name).exists():
                        screen.print(f"Error: '{item.name}' already exists!", style="red")
                    else:
                        shutil.copyfile(item, item.name)
                        screen.print(f"'{item.name}' was copied successfully!", style="green")
                        last_action.append(f"{Path(os.getcwd(), item.name)}")
                else:
                    if Path(os.getcwd(), item.name).exists():
                        screen.print(f"Error: '{item.name}' already exists!", style="red")
                    else:
                        shutil.copytree(item, item.name)
                        screen.print(f"'{item.name}' was copied successfully!", style="green")
                        last_action.append(f"{Path(os.getcwd(), item.name)}")
            else:
                screen.print(f"Error: Index is not a digit!", style="red")

        if len(last_action) > 0:
            add_last_drop(last_action)

    elif len(sys.argv) == 2 and sys.argv[1] == "-w":
        if len(hand["items"]) > 0:
            hand["items"].clear()
            with open(Path(scripts_path, ".hand_memory.json"), "w") as hand_file:
                json.dump(hand, hand_file)
            screen.print(f"The Hand washed successfully", style="green")
        else:
            screen.print("Message: Hand is empty!", style="yellow")

    elif len(sys.argv) >= 3 and sys.argv[1] == "-c":
        garbages = []
        for index in sys.argv[2:]:
            if index.isdigit():
                index = int(index)
                if index <= len(hand["items"]):
                    garbages.append(hand["items"][index - 1])
                else:
                    screen.print(f"Error: Index out of range!", style="red")
            else:
                screen.print(f"Error: Index is not a digit!", style="red")


        for item in garbages:
            if item in hand["items"]:
                hand["items"].remove(item)
                screen.print(f"'{item}' removed successfully", style="green")

        with open(Path(scripts_path, ".hand_memory.json"), "w") as hand_file:
            json.dump(hand, hand_file)

    elif len(sys.argv) == 2 and sys.argv[1] == "-z":
        if len(hand["last_drop"]) > 0:
            for item in hand["last_drop"][-1]:
                if os.path.exists(item):
                    if os.path.isfile(item):
                        os.remove(item)
                    else:
                        shutil.rmtree(item)
            screen.print("return to the previous position was applied", style="green")

        if len(hand["last_drop"]) == 0:
            screen.print("Error: The required action was not found", style="red")

        rem_last_drop()

    else:
        screen.print("Error: Unknown parameters!", style="red")


if __name__ == "__main__":
    init()
