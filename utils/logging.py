import structlog
import logging
import sys
from rich.console import Console
from rich.status import Status
from pathlib import Path
import time
console = Console()
def configure_logging(debug: bool = False):
    """Configure structlog for production-grade logging."""
    log_file = Path.home() / ".sin" / "sin.log"
    log_file.parent.mkdir(exist_ok=True)

    # Configure processors for structured JSON logging
    processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.JSONRenderer()
    ]

    # In debug mode, add console output with human-readable format
    if debug:
        processors = [
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.dev.ConsoleRenderer()  # Human-readable for debug
        ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Set up file handler for JSON logs
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler] if not debug else [file_handler, logging.StreamHandler(sys.stdout)],
    )

    # Set logging level to reduce verbosity in production
    logging.getLogger().setLevel(logging.INFO)
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

def display_spinner(self, message: str, duration: float):
        with Status(f"[blue]{message}[/blue]", console=console, spinner="dots"):
            time.sleep(duration)