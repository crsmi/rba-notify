# Docker Setup for eBird RBA

This document outlines how to build and run the eBird Rare Bird Alert application in Docker.

> **Note:** 
> - For Ubuntu Server specific instructions, please see [UBUNTU.md](UBUNTU.md)
> - For Portainer deployment instructions, please see [PORTAINER.md](PORTAINER.md)

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system

## Build and Run

### Using Docker Compose (Recommended)

1. Clone this repository
2. Navigate to the repository directory
3. Update `config/config.py` with your desired settings
4. Create and configure the environment file:
   ```bash
   cp config/.env.template config/.env
   # Edit .env with your credentials
   ```
5. Run:

```bash
docker-compose up -d
```

This will build the Docker image and start the container in detached mode.

### View logs

```bash
docker-compose logs -f
```

## Data Persistence

The application uses Docker volumes to persist data:

- `ebird_data`: Stores logs and previous alert data

This ensures that when the container restarts, it remembers which bird alerts it has already processed.

## Configuration

The configuration is mounted from your host system's `config/config.py` into the container. To update settings:

1. Edit the `config/config.py` file on your host machine
2. For environment variables (like Twilio and Discord credentials):
   - Create a copy of `config/.env.template` as `config/.env`
   - Fill in your credentials in the `.env` file
   - The Docker container will automatically use these settings
3. Restart the container:

```bash
docker-compose restart
```

## Troubleshooting

If the container isn't working as expected:

1. Check the logs:
```bash
docker-compose logs -f
```

2. Verify your configuration:
```bash
docker-compose exec ebird-rba cat config/config.py
```

3. Inspect the volume:
```bash
docker volume inspect ebird_data
```
