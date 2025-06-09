# Deploying eBird RBA with Portainer

This guide explains how to deploy the eBird RBA application using Portainer, a web-based Docker management tool, with a focus on configuration and secrets management.

> **Note:**
> - For verification and troubleshooting after deployment, see [VERIFICATION.md](VERIFICATION.md)

## Prerequisites

- Portainer installed on your Docker host
- Access to the Portainer web interface

## Deployment Steps

### 1. Prepare the Application Files

You have two options to deploy the application with Portainer:

#### Option A: Using a Git Repository (Recommended)

1. Push your project to a Git repository (GitHub, GitLab, etc.)
2. Make sure to include all required files (Dockerfile, docker-compose.yml, etc.)
3. Do not include sensitive data in the repository

#### Option B: Manual Upload

If you prefer not to use a Git repository, you can:
1. Create a ZIP archive of the application
2. Upload it to your Docker host
3. Extract it to a directory that Portainer can access

### 2. Deploy with Portainer

#### Using the Stack Feature (Recommended)

1. Log in to your Portainer interface
2. Go to "Stacks" in the side menu
3. Click "Add stack"
4. Fill in the form:
   - **Name**: `ebird-rba`
   - **Build method**: Choose one:
     - **Git repository**: 
       - Enter repository URL: `https://github.com/crsmi/rba-notify/` (include the trailing slash)
       - Leave the branch field empty (this will use the default branch)
       - Reference name: Can be left empty
     - **Web editor**: Paste the contents of your docker-compose.yml file
   - **Environment variables**: Configure the application settings:
     ```
     CHECK_INTERVAL=15
     NOTIFY_ON_STARTUP=false
     ENABLE_TEXT_NOTIFICATIONS=false
     ENABLE_DISCORD_NOTIFICATIONS=true
     
     # For SMS notifications (if needed)
     TWILIO_ACCOUNT_SID=your_account_sid
     TWILIO_AUTH_TOKEN=your_auth_token
     TWILIO_FROM_NUMBER=+1234567890
     TWILIO_TO_NUMBERS=+1234567890,+0987654321
     
     # For Discord notifications (if needed)
     DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-url
     ```

5. Click "Deploy the stack"

### 3. Managing Secrets and Configuration

#### Option 1: Environment Variables (Simple)

All configuration is available through environment variables that you can set directly in Portainer's UI when deploying or updating the stack:

- `CHECK_INTERVAL`: How often to check for updates (in minutes)
- `NOTIFY_ON_STARTUP`: Whether to send notifications for existing alerts at startup
- `ENABLE_TEXT_NOTIFICATIONS`: Enable/disable SMS notifications
- `ENABLE_DISCORD_NOTIFICATIONS`: Enable/disable Discord notifications
- `TWILIO_*`: Credentials for SMS notifications
- `DISCORD_WEBHOOK_URL`: Webhook URL for Discord notifications

#### Option 2: Configuration Files (Advanced)

For more complex configurations or when you need to modify the list of counties to monitor:

1. After deployment, go to "Volumes" in Portainer
2. Find the `ebird_data` volume
3. Browse the volume and edit configuration files directly

#### Option 3: Using Docker Secrets (Most Secure, Swarm Mode Only)

If using Docker Swarm mode:

1. Go to "Secrets" in Portainer
2. Create secrets for each sensitive value
3. Update the docker-compose.yml to use these secrets

### 4. Monitor the Application

1. View logs through the Portainer interface:
   - Go to the container or stack details
   - Click on "Logs"

2. Check the container status to ensure it's running properly

### 5. Adding More Counties to Monitor

To add more counties to monitor:

1. Deploy the stack first
2. Go to "Volumes" in Portainer
3. Find the volume where the container is running
4. Edit the `config/config.py` file to add more counties
5. Restart the container

## Making the Image Available in Portainer

For easier deployment across multiple systems, you can build and push your image to a Docker registry:

1. Build the image:
```bash
docker build -t your-username/ebird-rba:latest .
```

2. Push to Docker Hub or another registry:
```bash
docker push your-username/ebird-rba:latest
```

3. In Portainer, you can then deploy directly from the registry.

## Best Practices for Portainer Deployment

1. **Use stacks instead of individual containers** - Easier to manage and update
2. **Use environment variables for basic configuration** - Simpler to change in Portainer
3. **Use volumes for persistent data** - Ensures data survives container updates
4. **Consider using Docker Registry** - Makes deployment across multiple systems easier

## Troubleshooting

### Repository URL Format Issues
- When deploying from GitHub, ensure the repository URL includes a trailing slash (e.g., `https://github.com/crsmi/rba-notify/`)
- If you encounter "repository reference is invalid" errors, try leaving the branch field empty to use the default branch

### Container Not Starting
- Check container logs in Portainer for error messages
- Verify all required environment variables are set correctly
- Ensure volumes are properly mounted and accessible

### Notifications Not Working
- For Discord issues, verify your webhook URL is correctly formatted
- Check if `ENABLE_DISCORD_NOTIFICATIONS` is set to `true`
- Check container logs for API connection errors
