# CodeGuard AI - Quick Setup Guide

## Prerequisites

1. **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
2. **Git** (already installed)

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Make sure Docker Desktop is running
./scripts/setup-docker.sh
```

### Option 2: Manual Setup

1. **Start Docker Desktop** (if not already running)

2. **Install docker-compose** (if needed):
   ```bash
   # macOS
   brew install docker-compose
   
   # Or use the newer docker compose plugin (included in newer Docker Desktop)
   ```

3. **Start services**:
   ```bash
   # If you have docker-compose command:
   docker-compose up -d --build
   
   # Or if you have docker compose plugin:
   docker compose up -d --build
   ```

4. **Check status**:
   ```bash
   docker-compose ps
   # or
   docker compose ps
   ```

## Access the Application

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## Configuration

The `.env` file has been created with default values. You can edit it to customize:

```bash
# Edit .env file
nano .env
# or
code .env
```

Key variables:
- `SECRET_KEY` - Change this in production!
- `DATABASE_URL` - PostgreSQL connection string
- `QDRANT_HOST` - Qdrant host (use `qdrant` for Docker, `localhost` for local)

## Common Commands

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Restart a service
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build
```

## Troubleshooting

### Docker is not running
```bash
# Start Docker Desktop, then verify:
docker info
```

### Port already in use
If ports 3000, 8000, 5432, or 6333 are already in use, edit `docker-compose.yml` to change the port mappings.

### Services won't start
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

### Database connection errors
Make sure PostgreSQL container is healthy:
```bash
docker-compose ps postgres
```

## Next Steps

1. **Test the API**: Visit http://localhost:8000/docs
2. **Create a scan**: Use the frontend at http://localhost:3000
3. **Try the CLI**: 
   ```bash
   docker-compose exec backend codeguard scan tests/fixtures/vulnerable-app
   ```

## Development Mode

The backend is configured for hot-reload. Code changes in `app/` will automatically restart the server.

For frontend changes, rebuild:
```bash
docker-compose up -d --build frontend
```

