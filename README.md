# sin CLI

**sin CLI** is a powerful, user-friendly command-line tool for deploying and managing containerized services like MySQL and Kafka using Docker. With a sleek interface featuring animated spinners, styled output, and structured logging, sin simplifies service setup for developers and DevOps professionals.

<!-- ![sin CLI Screenshot](https://via.placeholder.com/800x200.png?text=sin+CLI+Demo) Replace with actual screenshot or GIF -->

## Features

- **Easy Service Deployment**: Deploy services like MySQL and Kafka with a single command.
- **Docker Integration**: Seamlessly interacts with Docker Compose V2 to manage containers.
- **Animated Console Output**: Professional spinners and banners for a polished user experience.
- **Structured Logging**: JSON logs for debugging and monitoring, written to `~/.sin/sin.log`.
- **Configurable**: Customize service settings via a `services.yml` configuration file.
- **Health Checks**: Ensures services are healthy before providing connection details.
- **Debug Mode**: Enable verbose logging with the `--debug` flag for troubleshooting.

## Prerequisites

- **Docker**: Docker Desktop or Docker CLI with Compose V2 installed.
  - Verify: `docker compose version`
- **Python**: Version 3.8 or higher.
- **Git**: For cloning service repositories.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/sumanmanna134/sin-installer-py.git
   cd sin-installer-py
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   **requirements.txt**:

   ```
   click==8.1.7
   structlog==24.4.0
   pydantic==2.9.2
   requests==2.32.3
   pyyaml==6.0.2
   rich==13.9.2
   ```

3. **Verify Docker**:
   Ensure Docker and Docker Compose are installed:

   ```bash
   docker --version
   docker compose version
   ```

   If Docker Compose V2 is not installed, follow [Docker's installation guide](https://docs.docker.com/compose/install/).

## Configuration

sin uses a `services.yml` file in the `sin/config` directory to define services. Example configuration:

```yaml
services:
  mysql:
    repo_url: https://github.com/yourusername/mysql-docker-repo
    compose_file: mysql-compose.yml
    service_name: mysql
    port_key: '3306'
    uri_format: 'mysql://{user}:{password}@{host}:{port}/{database}'
    env_vars:
      user: MYSQL_USER
      password: MYSQL_PASSWORD
      database: MYSQL_DATABASE
    defaults:
      user: root
      password: password
      database: mydb
      port: '3306'
    health_check:
      command: 'mysqladmin ping -h localhost -u {user} -p{password}'
      interval: '5'
      retries: '6'
  kafka:
    repo_url: https://github.com/yourusername/kafka-docker-repo
    compose_file: kafka-compose.yml
    service_name: kafka
    port_key: '9092'
    uri_format: 'kafka://{host}:{port}'
    env_vars:
      user: null
      password: null
      database: null
    defaults:
      port: '9092'
    health_check:
      command: 'kafka-topics.sh --list --bootstrap-server localhost:9092'
      interval: '5'
      retries: '6'
```

- **repo_url**: GitHub repository containing the Docker Compose file and `.env`.
- **base_dir**: Service files are downloaded to `~/.sin` by default.

Ensure the repositories specified in `repo_url` are accessible and contain the required `docker-compose.yml` and `.env` files.

## Usage

Run sin commands to manage services:

### Install a Service

Deploy a service (e.g., MySQL or Kafka):

```bash
python -m sin.cli install mysql
```

**Example Output**:

```
══════════════════════════════════════════════════
                sin CLI
══════════════════════════════════════════════════
           Installing Service: MYSQL
               Version: 1.0.0
    Timestamp: 2025-06-26 02:00:00 IST
══════════════════════════════════════════════════

Checking Docker installation... |  # 5-second spinner
✓ Docker is installed
Checking Docker Compose installation... |  # 5-second spinner
✓ Docker Compose is installed
Downloading mysql configuration... |  # 5-second spinner
Starting service with Docker Compose: sin_mysql...
✓ Service sin_mysql started
Waiting for mysql to be healthy... |  # 5-second spinner per retry
✓ Service mysql is healthy
MySQL Service Installed Successfully!
URI: mysql://user:pass@localhost:3306/mydb
Credentials: user=user, password=pass
Host: localhost:3306
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
python -m sin.cli --debug install mysql
```

Logs are written to `~/.sin/sin.log` in JSON format.

## Debugging

- **Log File**: Check `~/.sin/sin.log` for structured JSON logs:

  ```bash
  cat ~/.sin/sin.log
  ```

  Example log entry:

  ```json
  {
    "event": "Starting service installation",
    "service": "mysql",
    "timestamp": "2025-06-26T02:00:00.123456Z",
    "level": "info"
  }
  ```

- **Common Issues**:
  - **Docker Not Found**: Ensure Docker is installed and in your PATH.
  - **Repository Errors**: Verify `repo_url` in `services.yml` points to a valid repository.
  - **Health Check Failures**: Check the service’s Docker Compose file and `.env` for correct environment variables.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit changes: `git commit -m "Add your feature"`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Open a pull request.

Please include tests and update documentation as needed.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For issues or questions, open a GitHub issue or contact [sumanmanna134](https://github.com/sumanmanna134).

---

_Built with ❤️ for developers and DevOps enthusiasts._
