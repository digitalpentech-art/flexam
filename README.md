# FLEXAM Platform

Flexible Examination, Assessment and Academic Management Platform.

## Installation
1. Clone the repository.
2. `cp .env.example .env` (Configure DB, Redis, Secrets)
3. `make setup`
4. `make migrate`
5. `make run`

## Production Deployment
- Use `docker-compose -f docker-compose.prod.yml up -d`
- Ensure all environment variables are set.
- Requires PostgreSQL, Redis, and Nginx.

## Guides
Detailed guides are available in the `docs/` directory:
- [Developer Guide](docs/developer.md)
- [Administrator Guide](docs/administrator.md)
- [Deployment Guide](docs/deployment.md)
