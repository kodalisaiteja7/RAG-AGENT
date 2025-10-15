# Deployment Guide - Multi-User Regulatory Agent RAG

Complete guide for deploying the enterprise multi-user Regulatory Agent RAG system.

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment Options](#cloud-deployment-options)
6. [Production Considerations](#production-considerations)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## System Architecture

### Multi-User Knowledge Base Architecture
```
┌─────────────────────────────────────────────┐
│           User Interface (Streamlit)        │
│  - Authentication                           │
│  - Chat Interface                           │
│  - Document Upload                          │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────┴──────────────────────────┐
│        Multi-User Vector Store              │
│  ┌────────────────┐  ┌──────────────────┐  │
│  │  Admin KB      │  │  User-Specific   │  │
│  │  (Shared)      │  │  KB (Private)    │  │
│  └────────────────┘  └──────────────────┘  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────┴──────────────────────────┐
│        RAG Expert (Grok-4)                  │
│  - Query Processing                         │
│  - Context Retrieval                        │
│  - Response Generation                      │
└─────────────────────────────────────────────┘
```

### Features
- ✅ Multi-user authentication
- ✅ Admin knowledge base (shared across all users)
- ✅ User-specific knowledge bases (private)
- ✅ Professional UI with role-based access
- ✅ Real-time document upload
- ✅ Admin panel for user management
- ✅ Production-ready deployment

---

## Prerequisites

### Required
- Python 3.9+
- Docker & Docker Compose (for containerized deployment)
- 4GB+ RAM
- OpenAI API Key
- xAI (Grok) API Key

### Optional
- NVIDIA GPU (for faster embeddings)
- Cloud platform account (AWS/Azure/GCP)
- Domain name & SSL certificate

---

## Local Development Setup

### 1. Clone and Setup

```bash
cd /path/to/Regulatory-Agent-RAG

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:
```env
OPENAI_API_KEY=your_openai_key_here
XAI_API_KEY=your_xai_key_here
```

### 3. Initialize Admin Knowledge Base

```bash
# Build admin vector database
python vector_store.py

# Or load regulations dataset
python load_regulations_dataset.py
python vector_store.py
```

### 4. Run Application

```bash
streamlit run app_multiuser.py
```

Access at: `http://localhost:8501`

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **IMPORTANT:** Change admin password immediately after first login!

---

## Docker Deployment

### Option 1: Docker Compose (Recommended)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 2: Docker Run

```bash
# Build image
docker build -t regulatory-rag:latest .

# Run container
docker run -d \
  -p 8501:8501 \
  -e OPENAI_API_KEY="your_key" \
  -e XAI_API_KEY="your_key" \
  -v $(pwd)/user_data:/app/user_data \
  -v $(pwd)/onestream_vectordb:/app/onestream_vectordb \
  -v $(pwd)/onestream_kb.json:/app/onestream_kb.json \
  --name regulatory-rag \
  regulatory-rag:latest
```

---

## Cloud Deployment Options

### AWS Deployment

#### Option A: AWS ECS (Elastic Container Service)

1. **Push Docker Image to ECR**

```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag regulatory-rag:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/regulatory-rag:latest
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/regulatory-rag:latest
```

2. **Create ECS Task Definition**

```json
{
  "family": "regulatory-rag-task",
  "containerDefinitions": [
    {
      "name": "regulatory-rag",
      "image": "your-account-id.dkr.ecr.us-east-1.amazonaws.com/regulatory-rag:latest",
      "memory": 4096,
      "cpu": 2048,
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "your_key"
        },
        {
          "name": "XAI_API_KEY",
          "value": "your_key"
        }
      ]
    }
  ]
}
```

3. **Create ECS Service with Load Balancer**

#### Option B: AWS EC2

```bash
# SSH into EC2 instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository and deploy
git clone https://github.com/kodalisaiteja7/Regulatory-Agent-RAG.git
cd Regulatory-Agent-RAG
docker-compose up -d
```

### Azure Deployment

#### Azure Container Instances

```bash
# Login
az login

# Create resource group
az group create --name regulatory-rag-rg --location eastus

# Create container
az container create \
  --resource-group regulatory-rag-rg \
  --name regulatory-rag-app \
  --image your-registry/regulatory-rag:latest \
  --dns-name-label regulatory-rag \
  --ports 8501 \
  --environment-variables \
    OPENAI_API_KEY=your_key \
    XAI_API_KEY=your_key \
  --memory 4 \
  --cpu 2
```

### Google Cloud Platform

#### Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/your-project-id/regulatory-rag

# Deploy to Cloud Run
gcloud run deploy regulatory-rag \
  --image gcr.io/your-project-id/regulatory-rag \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --set-env-vars OPENAI_API_KEY=your_key,XAI_API_KEY=your_key
```

### DigitalOcean App Platform

1. Go to DigitalOcean App Platform
2. Connect your GitHub repository
3. Configure:
   - **Source:** GitHub - kodalisaiteja7/Regulatory-Agent-RAG
   - **Type:** Dockerfile
   - **Port:** 8501
   - **Size:** Professional (4GB RAM)
4. Add Environment Variables
5. Deploy

---

## Production Considerations

### Security

#### 1. Authentication Enhancement

Replace simple password auth with:
- OAuth 2.0 (Google, Microsoft)
- LDAP/Active Directory
- JWT tokens
- Multi-factor authentication (MFA)

#### 2. HTTPS Configuration

##### Using Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 3. Environment Variables Security

Use secrets management:
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Kubernetes Secrets

#### 4. Database Security

Store user credentials securely:
- Use bcrypt instead of SHA-256
- Implement rate limiting
- Add password complexity requirements
- Enable account lockout after failed attempts

### Performance Optimization

#### 1. Caching

Implement Redis for:
- Session management
- Query result caching
- Embedding caching

#### 2. Load Balancing

For high traffic, use:
- Multiple Streamlit instances
- Load balancer (Nginx/HAProxy)
- Kubernetes horizontal pod autoscaling

#### 3. Database Optimization

- Use PostgreSQL for user management
- Index frequently queried fields
- Implement connection pooling

### Scalability

#### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: regulatory-rag
spec:
  replicas: 3
  selector:
    matchLabels:
      app: regulatory-rag
  template:
    metadata:
      labels:
        app: regulatory-rag
    spec:
      containers:
      - name: regulatory-rag
        image: your-registry/regulatory-rag:latest
        ports:
        - containerPort: 8501
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-key
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
---
apiVersion: v1
kind: Service
metadata:
  name: regulatory-rag-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8501
  selector:
    app: regulatory-rag
```

---

## Monitoring & Maintenance

### Logging

#### Application Logs

```bash
# Docker logs
docker logs -f regulatory-rag

# Docker Compose logs
docker-compose logs -f
```

#### Centralized Logging

Use ELK Stack or Cloud Logging:
- AWS CloudWatch
- Azure Monitor
- GCP Cloud Logging

### Health Checks

The application includes health endpoints:
- `http://localhost:8501/_stcore/health`

### Backup Strategy

#### 1. User Data Backup

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/regulatory-rag"

# Backup user data
tar -czf $BACKUP_DIR/user_data_$DATE.tar.gz user_data/

# Backup admin KB
cp onestream_kb.json $BACKUP_DIR/onestream_kb_$DATE.json

# Backup users file
cp users.json $BACKUP_DIR/users_$DATE.json

# Backup vector databases
tar -czf $BACKUP_DIR/vectordb_$DATE.tar.gz onestream_vectordb/

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

#### 2. Automated Backups

Set up cron job:
```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup-script.sh
```

### Updates & Patches

```bash
# Pull latest code
git pull origin master

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Troubleshooting

### Common Issues

#### Issue: Application won't start

**Solution:**
```bash
# Check logs
docker-compose logs

# Verify environment variables
docker-compose config

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

#### Issue: Vector database not found

**Solution:**
```bash
# Initialize admin vector database
docker-compose exec regulatory-rag python vector_store.py
```

#### Issue: Out of memory

**Solution:**
- Increase Docker memory allocation
- Reduce `CHUNK_SIZE` and `TOP_K_RESULTS` in config.py
- Use smaller embedding model

---

## Support & Maintenance

### Regular Maintenance Tasks

- [ ] Weekly: Review logs for errors
- [ ] Weekly: Check disk space
- [ ] Monthly: Update dependencies
- [ ] Monthly: Review user accounts
- [ ] Quarterly: Security audit
- [ ] Quarterly: Performance optimization review

### Contact

For issues or questions:
- GitHub Issues: https://github.com/kodalisaiteja7/Regulatory-Agent-RAG/issues
- Email: [Your Support Email]

---

## License

[Your License Here]

---

**Last Updated:** December 2024
