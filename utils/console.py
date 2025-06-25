import time
import itertools
import click
try:
    from rich.console import Console
    from rich.status import Status
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
import structlog

logger = structlog.get_logger()
class ConsoleUtils:
    def __init__(self, use_rich: bool = True):
        """Initialize ConsoleUtils with optional rich support."""
        self.use_rich = use_rich and RICH_AVAILABLE
        self.console = Console() if self.use_rich else None

    def display_spinner(self, message: str, duration: float):
        """Display a spinner animation for the specified duration."""
        logger.debug("Starting spinner", message=message, duration=duration)
        if self.use_rich:
            with Status(f"[blue]{message}[/blue]", console=self.console, spinner="dots"):
                time.sleep(duration)
        else:
            spinner = itertools.cycle(['|', '/', '-', '\\'])
            end_time = time.time() + duration
            while time.time() < end_time:
                click.echo(f"\r{click.style(message, fg='blue')} {next(spinner)}", nl=False)
                time.sleep(0.1)  # Update every 100ms for smooth animation
            click.echo("\r" + " " * (len(message) + 2) + "\r", nl=False)  # Clear the line
        logger.debug("Spinner completed", message=message)