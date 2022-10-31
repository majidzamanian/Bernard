import sys
import subprocess
try:
    from rich.console import Console
except ImportError as module:
    subprocess.run([sys.executable, "-m", "pip", "install", "rich"], stdout=subprocess.DEVNULL)


def init():
    screen = Console()

    if len(sys.argv) == 1:
        subprocess.run(["clear"])
    elif len(sys.argv) == 2 and sys.argv[1] == "-h":
        screen.print("The clear command allows you to clean the screen.", style="green")
    else:
        screen.print("Error: Unknown parameters!", style="red")


if __name__ == "__main__":
    init()