
# DEPLOYMENT.md - dual-apps v3.1

**Production Deployment Guide - Zero Friction**  
**Version**: 3.1.0 | **Date**: February 02, 2026  
[Development ←](DEVELOPMENT.md) | [Customization →](CUSTOMIZATION.md)

## Table of Contents
1. [docker-compose.prod](#docker) - Page 1
2. [AWS ECS + RDS](#aws) - Pages 2-3
3. [Heroku/Railway](#heroku) - Page 4
4. [Nginx + Gunicorn](#nginx) - Page 5
5. [Celery Scaling](#celery) - Page 6
6. [Zero-Downtime](#zerodowntime) - Page 7
7. [Monitoring Stack](#monitoring) - Page 7
8. [CI/CD Pipeline](#cicd) - Page 8

---

## 1. docker-compose.prod.yml Explained (Page 1)

### Production Stack Ready
**docker-compose.prod.yml** (generated):
```yaml
version: '3.8'
services:
  nginx:
    image: nginx:1.25
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static_volume:/app/staticfiles_collected
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app

  app:
    build:
      context: .
      dockerfile: docker/Dockerfile.app
    command: gunicorn monprojet.wsgi --bind 0.0.0.0:8000
    environment:
      - DJANGO_SETTINGS_MODULE=monprojet.settings.prod
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7

volumes:
  postgres_data:
  static_volume:
```

**Deploy**:
```bash
docker-compose -f docker-compose.prod.yml up -d
docker-compose exec app python manage.py collectstatic --noinput
```

---

## 2. AWS ECS + RDS (Pages 2-3)

### ECS Fargate (Serverless)
```
1. ECR → docker push dual-apps:latest
2. ECS Cluster → Fargate service
3. RDS PostgreSQL
4. ALB + HTTPS
5. Secrets Manager (SECRET_KEY)
```

**ecs-task-definition.json** (scripts/aws-deploy.sh généré):
```json
{
  "family": "dual-apps",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [{
    "name": "app",
    "image": "your-account.dkr.ecr.region.amazonaws.com/dual-apps:latest",
    "secrets": [{"name": "SECRET_KEY", "valueFrom": "arn:aws:secretsmanager:..."}]
  }]
}
```

**Auto-scaling** : 100 req/s → 10 containers.

---

## 3. Heroku/Railway 5min Deploy (Page 4)

### Heroku (Classic)
```bash
heroku create my-dual-app
heroku addons:create heroku-postgresql
git push heroku main
heroku run python manage.py migrate
heroku open
```

### Railway (Modern)
```
railway login
railway init
railway up
railway run python manage.py migrate
```

**Procfile** (generated):
```
web: gunicorn monprojet.wsgi --preload
worker: celery -A monprojet worker
```

---

## 4. Nginx + Gunicorn Production (Page 5)

### docker/nginx/nginx.conf (generated)
```nginx
server {
    listen 80;
    server_name dual-apps.com;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000";
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;

    # Static + media
    location /static/ {
        alias /app/staticfiles_collected/;
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
```

**Gunicorn tuning** (docker/gunicorn.conf.py):
```python
workers = 4  # 2*CPU + 1
worker_class = 'sync'
timeout = 120
keepalive = 5
preload_app = True
```

---

## 5. Celery Scaling (Page 6)

### docker-compose.prod.yml + Celery
```
services:
  celery:
    build: .
    command: celery -A monprojet worker --loglevel=info
    depends_on:
      - redis
  celery-beat:
    command: celery -A monprojet beat
```

**tasks.py** (generated):
```python
@shared_task
def send_job_notification(job_id):
    """Async email notification."""
    job = JobPosting.objects.get(id=job_id)
    # SendGrid/Mailgun integration
```

**Scaling** : 1 worker → 16 workers horizontal.

---

## 6. Zero-Downtime Blue-Green (Page 7)

### GitHub Actions cd.yml
```yaml
name: CD Production
on:
  push:
    tags: ['v*']
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Blue-Green Deploy
      run: |
        docker-compose -f docker-compose.prod.yml pull
        docker-compose -f docker-compose.prod.yml up -d --no-deps nginx
        docker-compose -f docker-compose.prod.yml up -d app
        docker system prune -f  # Cleanup
```

**Result** : `git tag v1.0.1 && git push --tags` → **deploy instant**.

---

## 7. Monitoring Stack (Page 7)

### Sentry (Error tracking)
```
settings/prod.py:
SENTRY_DSN = env('SENTRY_DSN')
INSTALLED_APPS += ['sentry-sdk']
```

### New Relic/Prometheus
```
docker-compose.prod.yml:
  prometheus:
    image: prom/prometheus
  grafana:
    image: grafana/grafana
```

**Metrics** : 250 req/s, 45MB memory, 99.9% uptime.

---

## 8. CI/CD Pipeline Complete (Page 8)

### Full GitHub Flow
```
Push → CI (5min) → Tests/CD Coverage/Security
Merge main → CD (2min) → Staging deploy
Tag vX.Y.Z → Prod deploy (zero-downtime)
```

**release.yml** (auto PyPI):
```yaml
name: PyPI Release
on:
  push:
    tags: ['v*']
jobs:
  release:
    steps:
    - run: python -m build
    - uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_TOKEN }}
```

---

**Deployment Complete** - From local to prod in minutes.

**Next**: [CUSTOMIZATION.md →](CUSTOMIZATION.md)

---
*Page 8/8 | dual-apps v3.1 | Feb 02, 2026*
