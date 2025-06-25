import subprocess
import yaml
import structlog
import click
from utils.console import ConsoleUtils
from pathlib import Path

logger = structlog.get_logger()

class DockerClient:
    def __init__(self):
        self.console = ConsoleUtils(use_rich=True)  # Set to False if rich is not installed

    def check_docker(self):
        self.console.display_spinner("Checking Docker installation...", 5.0)  # 5-second spinner
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            logger.info("Docker version check passed")
            click.echo(click.style("✓ Docker is installed", fg="green"))
        except subprocess.CalledProcessError as e:
            logger.error("Docker version check failed", error=str(e), stdout=e.stdout.decode(), stderr=e.stderr.decode())
            click.echo(click.style("❗ Docker is not installed or not accessible", fg="red"))
            raise RuntimeError("Docker is not installed. Please install Docker and ensure it's in your PATH.")

        self.console.display_spinner("Checking Docker Compose installation...", 5.0)  # 5-second spinner
        try:
            subprocess.run(["docker", "compose", "version"], check=True, capture_output=True)
            logger.info("Docker Compose version check passed")
            click.echo(click.style("✓ Docker Compose is installed", fg="green"))
        except subprocess.CalledProcessError as e:
            logger.error("Docker Compose version check failed", error=str(e), stdout=e.stdout.decode(), stderr=e.stderr.decode())
            click.echo(click.style("❗ Docker Compose is not installed or not accessible", fg="red"))
            raise RuntimeError("Docker Compose is not installed. Please install Docker Compose V2.")

    def run_docker_compose(self, compose_file: Path, project_name: str):
        try:
            click.echo(click.style(f"Starting service with Docker Compose: {project_name}...", fg="blue"))
            subprocess.run(
                ["docker", "compose", "-f", str(compose_file), "-p", project_name, "up", "-d"],
                check=True,
                capture_output=True
            )
            logger.info("Docker Compose started successfully", project=project_name)
            click.echo(click.style(f"✓ Service {project_name} started", fg="green"))
        except subprocess.CalledProcessError as e:
            logger.error("Failed to run docker compose", error=str(e), stderr=e.stderr.decode())
            click.echo(click.style(f"❗ Failed to start service {project_name}", fg="red"))
            raise RuntimeError(f"Failed to start service: {e.stderr.decode()}")

    def get_container_ports(self, project_name: str, service_name: str, port_key: str) -> str:
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={project_name}_{service_name}", "--format", "{{.Ports}}"],
                check=True,
                capture_output=True,
                text=True
            )
            ports = result.stdout.strip()
            for mapping in ports.split(","):
                if port_key in mapping:
                    return mapping.split("->")[0].strip()
            return f"0.0.0.0:{port_key}"
        except subprocess.CalledProcessError as e:
            logger.error("Failed to get container ports", error=str(e))
            raise RuntimeError(f"Failed to get ports: {e.stderr.decode()}")

    def get_compose_config(self, compose_file: Path) -> dict:
        try:
            with open(compose_file, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error("Failed to load compose config", error=str(e))
            raise RuntimeError(f"Failed to load docker-compose file: {str(e)}")

    def exec_health_check(self, container_name: str, command: str) -> bool:
        try:
            result = subprocess.run(
                ["docker", "exec", container_name, "sh", "-c", command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False