# Ubuntu Server Setup for eBird RBA

This document provides instructions for setting up the eBird RBA application on Ubuntu Server using Docker.

## Prerequisites

1. Install Docker on Ubuntu Server (if not already installed):
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
```

2. Enable Docker to start on boot:
```bash
sudo systemctl enable docker
```

3. Add your user to the docker group (to run Docker without sudo):
```bash
sudo usermod -aG docker $USER
```
   
   Log out and log back in for this to take effect.

## Deployment

1. Clone this repository:
```bash
git clone https://github.com/your-username/ebird-rba.git
cd ebird-rba
```

2. Create and configure the environment file:
```bash
cp config/.env.template config/.env
nano config/.env  # Edit with your credentials
```

3. Start the container:
```bash
docker-compose up -d
```

The `restart: unless-stopped` setting in docker-compose.yml ensures the container automatically restarts whenever Docker starts, including after system boot.

## Additional Notes for Ubuntu Server

- File permissions: Ensure the application directory and files have appropriate permissions
- Check logs: `docker-compose logs -f` to view application logs
- Monitor system resources: `htop` or `docker stats` to monitor resource usage
