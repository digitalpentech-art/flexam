# Deployment Guide

## Production Stack
- **Web Server:** Nginx
- **App Server:** Gunicorn
- **Database:** PostgreSQL
- **Task Queue:** Redis + Celery

## Steps
1. Configure `.env` with production credentials.
2. Build images: `docker-compose -f docker-compose.prod.yml build`
3. Start stack: `docker-compose -f docker-compose.prod.yml up -d`
4. Run migrations: `docker-compose -f docker-compose.prod.yml exec web flask db upgrade`
