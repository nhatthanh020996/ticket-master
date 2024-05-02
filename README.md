## Run.

### 1. Create database, cache.
```bash
docker compose -f dockers/docker-compose.yml up -d
```

### 2. Create webserver.
```bash
mkdir logs

chmod +x deployment/prod.webserver.sh

./deployment/prod.webserver.sh
```

### 3. Start Nginx.
```bash
docker compose -f dockers/nginx-docker-compose.yml up -d
```