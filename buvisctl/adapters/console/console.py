from rich.console import Console
from rich.prompt import Confirm

CHECKMARK = "[bold green1]\u2714[/bold green1]"
CROSSMARK = "[bold indian_red]\u2718[/bold indian_red]"


class ConsoleAdapter:

    def __init__(self):
        self.console = Console(log_path=False)

    def success(self, message):
        self.console.print(f"{CHECKMARK} {message}")

    def failure(self, message, details=""):
        if details:
            self.console.print(
                f"{CROSSMARK} {message} \n\nDetails:\n\n {details}")
        else:
            self.console.print(f"{CROSSMARK} {message}")

    def panic(self, message, details=""):
        self.failure(message, details)
        exit()

    def status(self, message):
        return self.console.status(message, spinner="arrow3")

    def capture(self):
        return self.console.capture()

    def confirm(self, message):
        return Confirm.ask(message)


console = ConsoleAdapter()
