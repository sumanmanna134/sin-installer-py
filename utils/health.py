import structlog
import time
import click
from utils.docker import DockerClient
from utils.console import ConsoleUtils

logger = structlog.get_logger()

class HealthChecker:
    def __init__(self):
        self.docker = DockerClient()
        self.console = ConsoleUtils(use_rich=True)

    def wait_for_health(self, project_name: str, service_name: str, health_config: dict, timeout: int):
        start_time = time.time()
        interval = int(health_config.get("interval", "5"))
        retries = int(health_config.get("retries", "6"))
        command = health_config["command"]

        container_name = f"{project_name}_{service_name}_1"
        attempt = 0

        while attempt < retries:
            if time.time() - start_time > timeout:
                logger.error("Health check timed out", service=service_name)
                click.echo(click.style(f"❗ Service {service_name} failed to become healthy within {timeout}s", fg="red"))
                raise RuntimeError(f"Service {service_name} failed to become healthy within {timeout}s")

            if self.docker.exec_health_check(container_name, command):
                logger.info("Service is healthy", service=service_name)
                click.echo(click.style(f"✓ Service {service_name} is healthy", fg="green"))
                return

            attempt += 1
            logger.debug("Health check attempt failed", service=service_name, attempt=attempt)
            self.console.display_spinner(f"Waiting for {service_name} to be healthy...", interval)

        logger.error("Health check failed after max retries", service=service_name)
        click.echo(click.style(f"❗ Service {service_name} failed health check after {retries} attempts", fg="red"))
        raise RuntimeError(f"Service {service_name} failed health check after {retries} attempts")