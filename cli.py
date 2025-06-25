import click
import structlog
from services.manager import ServiceManager
from config.settings import load_config
from utils.logging import configure_logging

logger = structlog.get_logger()

@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging to console.')
def sin(debug):
    """SIN CLI for deploying services via Docker."""
    configure_logging(debug=debug)

@sin.command()
@click.argument("service")
def install(service):
    """Install a specified service."""
    logger.info("Starting service installation", service=service)
    try:
        config = load_config()
        manager = ServiceManager(config)
        manager.install_service(service)
        logger.info("Service installation completed", service=service)
    except Exception as e:
        logger.error("Installation failed", service=service, error=str(e))
        raise click.ClickException(str(e))

if __name__ == "__main__":
    sin()