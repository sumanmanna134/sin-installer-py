import structlog
from config.settings import AppConfig
from utils.docker import DockerClient
from utils.repo import RepositoryDownloader
from utils.health import HealthChecker
from utils.console import ConsoleUtils
from urllib.parse import quote_plus
from pathlib import Path
import click
from datetime import datetime
from zoneinfo import ZoneInfo

logger = structlog.get_logger()

class ServiceManager:
    def __init__(self, config: AppConfig):
        self.config = config
        self.docker = DockerClient()
        self.downloader = RepositoryDownloader()
        self.health_checker = HealthChecker()
        self.console = ConsoleUtils(use_rich=True)  # Set to False if rich is not installed

    def _display_banner(self, service_name: str):
        """Display a professional banner for the service installation."""
        banner_width = 50
        service_name = service_name.upper()
        cli_version = "1.0.0"  # Replace with dynamic version if available
        timestamp = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S %Z")

        click.echo(click.style("═" * banner_width, fg="blue", bold=True))
        click.echo(click.style(f"{'SIN CLI':^{banner_width}}", fg="green", bold=True))
        click.echo(click.style("═" * banner_width, fg="blue", bold=True))
        click.echo(click.style(f"{'Installing Service: ' + service_name:^{banner_width}}", fg="cyan"))
        click.echo(click.style(f"{'Version: ' + cli_version:^{banner_width}}", fg="white"))
        click.echo(click.style(f"{'Timestamp: ' + timestamp:^{banner_width}}", fg="white"))
        click.echo(click.style("═" * banner_width, fg="blue", bold=True))
        click.echo()

    def install_service(self, service_name: str):
        if service_name not in self.config.services:
            raise ValueError(f"Service '{service_name}' is not supported. Available: {', '.join(self.config.services.keys())}")

        self._display_banner(service_name)
        logger.info("Starting service installation", service=service_name)

        service_config = self.config.services[service_name]
        project_name = f"SIN_{service_name}"
        dest_dir = Path(self.config.base_dir) / service_name
        compose_file = dest_dir / service_config.compose_file

        logger.info("Checking Docker availability")
        self.docker.check_docker()

        logger.info("Downloading service configuration", service=service_name)
        self.console.display_spinner(f"Downloading {service_name} configuration...", 5.0)  # 5-second spinner
        self.downloader.download_repo(service_config.repo_url, dest_dir)

        logger.info("Starting service", service=service_name)
        self.docker.run_docker_compose(compose_file, project_name)

        logger.info("Waiting for service to be healthy", service=service_name)
        if service_config.health_check:
            self.health_checker.wait_for_health(
                project_name,
                service_config.service_name,
                service_config.health_check,
                self.config.wait_timeout
            )

        ports = self.docker.get_container_ports(project_name, service_config.service_name, service_config.port_key)
        host = "localhost"
        port = ports.split(":")[1] if ":" in ports else service_config.defaults.get("port", service_config.port_key)

        compose_config = self.docker.get_compose_config(compose_file)
        service_def = compose_config["services"][service_config.service_name]
        env = service_def.get("environment", {})

        uri_vars = {"host": host, "port": port}
        for key, env_var in service_config.env_vars.items():
            if env_var:
                value = env.get(env_var, service_config.defaults.get(key))
                if key == "password" and value:
                    value = quote_plus(value)
                uri_vars[key] = value

        uri = service_config.uri_format.format(**{k: v for k, v in uri_vars.items() if v is not None})

        click.echo(f"\n{click.style(service_name.capitalize() + ' Service Installed Successfully!', fg='green', bold=True)}")
        click.echo(click.style(f"URI: {uri}", fg="cyan"))
        if uri_vars.get("user") or uri_vars.get("password"):
            click.echo(click.style(f"Credentials: user={uri_vars.get('user', 'N/A')}, password={uri_vars.get('password', 'N/A')}", fg="cyan"))
        click.echo(click.style(f"Host: {host}:{port}", fg="cyan"))