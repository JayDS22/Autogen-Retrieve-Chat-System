# docs/deployment_guide.md
# AutoGen RetrieveChat Deployment Guide

## Prerequisites

- Python 3.9+
- Docker (optional)
- 4GB+ RAM
- API keys for LLM services (OpenAI, Anthropic)

## Local Development Setup

1. **Clone Repository**
```bash
git clone https://github.com/JayDS22/autogen-retrievechat-system
cd autogen-retrievechat-system
```

2. **Environment Setup**
```bash
chmod +x scripts/setup_environment.sh
./scripts/setup_environment.sh
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run Application**
```bash
source venv/bin/activate
python src/main.py
```

## Docker Deployment

1. **Build Image**
```bash
docker build -t retrievechat-app .
```

2. **Run with Docker Compose**
```bash
docker-compose up -d
```

3. **Services Available**
- API: http://localhost:8000
- ChromaDB: http://localhost:8001
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Production Deployment

### AWS ECS Deployment

1. **Create Task Definition**
```json
{
  "family": "retrievechat",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "retrievechat-app",
      "image": "your-ecr-repo/retrievechat:latest",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "OPENAI_API_KEY", "value": "your-key"},
        {"name": "ENVIRONMENT", "value": "production"}
      ]
    }
  ]
}
```

2. **Create Service**
```bash
aws ecs create-service \
  --cluster your-cluster \
  --service-name retrievechat-service \
  --task-definition retrievechat \
  --desired-count 2 \
  --launch-type FARGATE
```

### Kubernetes Deployment

1. **Deployment YAML**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: retrievechat-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: retrievechat
  template:
    metadata:
      labels:
        app: retrievechat
    spec:
      containers:
      - name: retrievechat
        image: retrievechat:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
```

2. **Service YAML**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: retrievechat-service
spec:
  selector:
    app: retrievechat
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Configuration Management

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional |
| `LOG_LEVEL` | Logging level | INFO |
| `MAX_WORKERS` | Worker processes | 4 |
| `REDIS_URL` | Redis connection | redis://localhost:6379 |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB storage | ./chroma_db |

### Scaling Configuration

```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: retrievechat-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: retrievechat-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Monitoring and Observability

### Prometheus Metrics

The application exposes metrics at `/metrics`:
- Request count and duration
- Error rates
- Model performance metrics
- Resource utilization

### Grafana Dashboards

Import dashboard from `config/grafana-dashboard.json`:
- Response time percentiles
- Throughput and error rates
- Resource usage
- Custom business metrics

### Health Checks

- **Liveness**: `GET /health`
- **Readiness**: `GET /health` (same endpoint)
- **Startup**: Configurable delay for initialization

## Security Considerations

### API Security
- Use HTTPS in production
- Implement rate limiting
- Add authentication middleware
- Validate all inputs

### Container Security
```dockerfile
# Use non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Limit capabilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
```

### Network Security
- Use private subnets for containers
- Implement security groups/network policies
- Enable VPC flow logs
- Use secrets management (AWS Secrets Manager, K8s Secrets)

## Performance Optimization

### Database Optimization
```python
# ChromaDB configuration
chroma_settings = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="/app/chroma_db",
    anonymized_telemetry=False
)
```

### Caching Strategy
```yaml
# Redis configuration
redis:
  maxmemory: 1gb
  maxmemory-policy: allkeys-lru
  timeout: 300
```

### Load Balancing
```nginx
upstream retrievechat {
    least_conn;
    server app1:8000;
    server app2:8000;
    server app3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://retrievechat;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Common Issues

1. **API Key Errors**
```bash
# Check environment variables
echo $OPENAI_API_KEY
# Verify API key validity
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

2. **Memory Issues**
```bash
# Monitor memory usage
docker stats
# Increase memory limits
docker run -m 4g retrievechat:latest
```

3. **ChromaDB Issues**
```bash
# Check ChromaDB logs
docker logs chromadb
# Reset ChromaDB
rm -rf chroma_db/
```

### Log Analysis
```bash
# Application logs
tail -f logs/retrievechat.log

# Error patterns
grep "ERROR" logs/retrievechat.log | tail -20

# Performance analysis
grep "TIMING" logs/retrievechat.log | awk '{print $6}' | sort -n
```
