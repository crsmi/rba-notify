# Ubuntu Server Setup for eBird RBA

This document provides instructions for setting up the eBird RBA application on Ubuntu Server using Docker.

## Prerequisites

1. Install Docker on Ubuntu Server (if not already installed):
```bash
sudo apt update
sudo apt install -y docker.io
```

2. Install Docker Compose (if not using Portainer):
```bash
# For Docker Compose V1
sudo apt install -y docker-compose

# For Docker Compose V2 (recommended)
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-compose-plugin
```

3. Enable Docker to start on boot:
```bash
sudo systemctl enable docker
```

4. Add your user to the docker group (to run Docker without sudo):
```bash
sudo usermod -aG docker $USER
```
   
   Log out and log back in for this to take effect.

## Deployment

1. Clone this repository:
```bash
git clone https://github.com/crsmi/rba-notify.git
cd rba-notify
```

2. You have two options for deployment:

### Option A: Using docker-compose

a. Create and configure the environment file:
```bash
cp config/.env.template config/.env
nano config/.env  # Edit with your credentials
```

b. Start the container:
```bash
docker-compose up -d
```

### Option B: Using Portainer (Recommended)

a. Install Portainer if not already installed:
```bash
docker volume create portainer_data
docker run -d -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce
```

b. Access Portainer through your browser at `http://your-server-ip:9000`

c. Follow the instructions in [PORTAINER.md](PORTAINER.md) to deploy the application

Note: Deploying with Portainer has been tested and confirmed working on Ubuntu Server running on a mini PC.

The `restart: unless-stopped` setting in docker-compose.yml ensures the container automatically restarts whenever Docker starts, including after system boot.

## Additional Notes for Ubuntu Server

- File permissions: Ensure the application directory and files have appropriate permissions
- Check logs: `docker-compose logs -f` or in Portainer UI to view application logs
- Monitor system resources: `htop` or `docker stats` to monitor resource usage

## Troubleshooting

### Docker Compose Issues
- If you encounter "docker-compose command not found" errors, try using `docker compose` (with a space) if you installed Docker Compose V2
- For Docker Compose V2: Use `docker compose up -d` instead of `docker-compose up -d`

### Container Not Starting
- Check logs: `docker logs ebird-rba` or through Portainer
- Verify permissions on volume directories: `sudo ls -la /var/lib/docker/volumes/ebird_data/_data`
- Check if the container is running: `docker ps -a`

### Portainer Issues
- If you can't access Portainer, check if it's running: `docker ps | grep portainer`
- Verify port 9000 is open in your firewall: `sudo ufw status`

### Application Verification
To confirm the application is working correctly:

1. Check that the container is running with proper restart policy:
   ```bash
   docker inspect ebird-rba | grep -A 10 RestartPolicy
   ```

2. Monitor logs for activity:
   ```bash
   docker logs -f ebird-rba | grep "Checking for new alerts"
   ```

3. Test Discord notifications by restarting the container:
   ```bash
   docker restart ebird-rba
   ```
   (If `NOTIFY_ON_STARTUP` is set to `true`)
