# GCP Deployment Guide - Enterprise RAG System

Complete step-by-step guide to deploy the multi-user Enterprise RAG System to Google Cloud Platform.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial GCP Setup](#initial-gcp-setup)
3. [Option 1: Cloud Run Deployment (Recommended)](#option-1-cloud-run-deployment-recommended)
4. [Option 2: App Engine Deployment](#option-2-app-engine-deployment)
5. [Option 3: GKE (Kubernetes) Deployment](#option-3-gke-kubernetes-deployment)
6. [Setting Up Secrets](#setting-up-secrets)
7. [Persistent Storage Setup](#persistent-storage-setup)
8. [Custom Domain & SSL](#custom-domain--ssl)
9. [Monitoring & Logging](#monitoring--logging)
10. [Cost Optimization](#cost-optimization)

---

## Prerequisites

### 1. Install Google Cloud SDK

**Windows:**
```powershell
# Download and install from:
https://cloud.google.com/sdk/docs/install

# Or use PowerShell:
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

**Mac/Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 2. Initialize gcloud

```bash
# Login to GCP
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable storage.googleapis.com
```

### 3. Required Information

- GCP Project ID
- OpenAI API Key
- xAI (Grok) API Key
- Billing account enabled

---

## Initial GCP Setup

### 1. Create GCP Project (if needed)

```bash
# Create new project
gcloud projects create your-project-id --name="Enterprise RAG System"

# Set as active project
gcloud config set project your-project-id

# Link billing account (required)
gcloud billing projects link your-project-id --billing-account=BILLING_ACCOUNT_ID
```

### 2. Set Environment Variables

```bash
# Set project ID
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Windows PowerShell:
$env:PROJECT_ID="your-project-id"
$env:REGION="us-central1"
```

---

## Option 1: Cloud Run Deployment (Recommended)

Cloud Run is serverless, auto-scaling, and cost-effective. **Best for most use cases.**

### Step 1: Prepare Your Code

Make sure you're in the project directory:
```bash
cd /path/to/Regulatory-Agent-RAG
```

### Step 2: Build and Push Docker Image

```bash
# Build the image
gcloud builds submit --tag gcr.io/$PROJECT_ID/enterprise-rag

# This will:
# 1. Build your Docker image
# 2. Push to Google Container Registry
# 3. Take ~5-10 minutes
```

### Step 3: Create Secrets

```bash
# Create secrets for API keys
echo -n "your-openai-api-key" | gcloud secrets create openai-api-key --data-file=-
echo -n "your-xai-api-key" | gcloud secrets create xai-api-key --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding xai-api-key \
  --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 4: Create Cloud Storage Buckets

```bash
# Create bucket for admin knowledge base
gsutil mb -p $PROJECT_ID -l $REGION gs://$PROJECT_ID-admin-kb

# Create bucket for user data
gsutil mb -p $PROJECT_ID -l $REGION gs://$PROJECT_ID-user-data

# Upload initial admin KB and vector DB
gsutil -m cp -r onestream_kb.json gs://$PROJECT_ID-admin-kb/
gsutil -m cp -r onestream_vectordb gs://$PROJECT_ID-admin-kb/
```

### Step 5: Deploy to Cloud Run

```bash
gcloud run deploy enterprise-rag \
  --image gcr.io/$PROJECT_ID/enterprise-rag \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 1 \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest,XAI_API_KEY=xai-api-key:latest" \
  --set-env-vars="CHUNK_SIZE=2000,CHUNK_OVERLAP=400,TOP_K_RESULTS=8,CONTEXT_WINDOW=6"
```

### Step 6: Get Your URL

```bash
# Get the deployed URL
gcloud run services describe enterprise-rag --region $REGION --format 'value(status.url)'
```

Your application will be live at: `https://enterprise-rag-xxxxx-uc.a.run.app`

---

## Option 2: App Engine Deployment

App Engine provides managed infrastructure with integrated services.

### Step 1: Deploy

```bash
# Deploy using app.yaml
gcloud app deploy app.yaml

# This will deploy to:
# https://YOUR_PROJECT_ID.appspot.com
```

### Step 2: Set Secrets via Environment

```bash
# Set API keys as environment variables
gcloud app deploy --set-env-vars OPENAI_API_KEY=your_key,XAI_API_KEY=your_key
```

---

## Option 3: GKE (Kubernetes) Deployment

For enterprise-scale deployments with advanced orchestration.

### Step 1: Create GKE Cluster

```bash
gcloud container clusters create enterprise-rag-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 10
```

### Step 2: Deploy to Kubernetes

```bash
# Get cluster credentials
gcloud container clusters get-credentials enterprise-rag-cluster --zone us-central1-a

# Apply Kubernetes manifests
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml
```

---

## Setting Up Secrets

### Using Secret Manager (Recommended)

```bash
# Create secrets
gcloud secrets create openai-api-key --replication-policy="automatic"
gcloud secrets create xai-api-key --replication-policy="automatic"

# Add secret versions
echo -n "your-openai-key" | gcloud secrets versions add openai-api-key --data-file=-
echo -n "your-xai-key" | gcloud secrets versions add xai-api-key --data-file=-

# Access in application (already configured in code)
```

### View Secrets

```bash
# List secrets
gcloud secrets list

# Get latest version
gcloud secrets versions access latest --secret="openai-api-key"
```

---

## Persistent Storage Setup

### Option A: Cloud Storage (Recommended for Cloud Run)

```bash
# Create buckets
gsutil mb gs://$PROJECT_ID-admin-kb
gsutil mb gs://$PROJECT_ID-user-data

# Set up FUSE mounting in Dockerfile
# Add to Dockerfile:
# RUN gcsfuse $PROJECT_ID-admin-kb /app/admin_kb
```

### Option B: Persistent Disk (For GKE)

```yaml
# In kubernetes/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: enterprise-rag-storage
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
```

### Option C: Cloud SQL (For User Database)

```bash
# Create Cloud SQL instance
gcloud sql instances create enterprise-rag-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=$REGION

# Create database
gcloud sql databases create enterprise_rag --instance=enterprise-rag-db
```

---

## Custom Domain & SSL

### Step 1: Map Custom Domain

```bash
# For Cloud Run
gcloud beta run domain-mappings create \
  --service enterprise-rag \
  --domain your-domain.com \
  --region $REGION
```

### Step 2: Configure DNS

Add the following DNS records in your domain registrar:

```
Type: CNAME
Name: www (or @)
Value: ghs.googlehosted.com
```

### Step 3: SSL Certificate

SSL is automatically provisioned by Google (Let's Encrypt). It may take 15-30 minutes.

Check status:
```bash
gcloud beta run domain-mappings describe --domain your-domain.com --region $REGION
```

---

## Monitoring & Logging

### Cloud Logging

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=enterprise-rag" --limit 50 --format json

# Stream logs
gcloud logging tail "resource.type=cloud_run_revision"
```

### Cloud Monitoring

```bash
# Create uptime check
gcloud monitoring uptime-checks create https://enterprise-rag-xxxxx.run.app \
  --display-name="Enterprise RAG Health Check"
```

### Set Up Alerts

In GCP Console:
1. Go to Monitoring > Alerting
2. Create Policy
3. Set conditions:
   - CPU usage > 80%
   - Memory usage > 90%
   - Error rate > 5%
4. Add notification channels (email, Slack, PagerDuty)

---

## Cost Optimization

### Cloud Run Pricing Optimization

```bash
# Set minimum instances to 0 for low traffic
gcloud run services update enterprise-rag \
  --region $REGION \
  --min-instances 0

# Use CPU throttling when idle
gcloud run services update enterprise-rag \
  --region $REGION \
  --cpu-throttling

# Set concurrency
gcloud run services update enterprise-rag \
  --region $REGION \
  --concurrency 80
```

### Estimated Monthly Costs

**Cloud Run (Low Traffic):**
- ~$20-50/month for < 10,000 requests
- $0.00002400 per request
- $0.00000900 per GB-second memory

**Cloud Run (Medium Traffic):**
- ~$100-200/month for < 100,000 requests

**Cloud Run (High Traffic):**
- ~$500+/month for > 500,000 requests

**Storage:**
- Cloud Storage: $0.020 per GB/month
- ~$5-10/month for typical usage

**Total estimated:** $30-70/month for typical startup usage

---

## Post-Deployment Tasks

### 1. Initialize Admin Vector Database

```bash
# SSH into Cloud Run instance (for one-time setup)
gcloud run services proxy enterprise-rag --region $REGION
```

### 2. Change Default Admin Password

1. Login at your deployed URL
2. Use: admin / admin123
3. Go to Admin Panel
4. Create new admin user
5. Delete default admin

### 3. Set Up Backups

```bash
# Automate backups with Cloud Scheduler
gcloud scheduler jobs create http backup-user-data \
  --schedule="0 2 * * *" \
  --uri="https://enterprise-rag-xxxxx.run.app/api/backup" \
  --http-method=POST
```

### 4. Configure Load Balancer (Optional)

For multi-region deployment with load balancing:

```bash
gcloud compute backend-services create enterprise-rag-backend \
  --global \
  --load-balancing-scheme=EXTERNAL

# Add regions
gcloud compute backend-services add-backend enterprise-rag-backend \
  --global \
  --region=$REGION \
  --serverless-deployment-platform=cloud-run
```

---

## Troubleshooting

### Issue: Deployment timeout

**Solution:**
```bash
# Increase timeout
gcloud run services update enterprise-rag --timeout 600 --region $REGION
```

### Issue: Out of memory

**Solution:**
```bash
# Increase memory
gcloud run services update enterprise-rag --memory 8Gi --region $REGION
```

### Issue: Cold starts

**Solution:**
```bash
# Keep minimum instances warm
gcloud run services update enterprise-rag --min-instances 1 --region $REGION
```

### Issue: Can't access secrets

**Solution:**
```bash
# Check IAM permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:$PROJECT_ID@appspot.gserviceaccount.com"
```

---

## CI/CD Setup

### GitHub Actions Integration

Create `.github/workflows/deploy-gcp.yml`:

```yaml
name: Deploy to GCP Cloud Run

on:
  push:
    branches: [ master ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - id: 'auth'
        uses: 'google-github-actions/auth@v1'
        with:
          credentials_json: '${{ secrets.GCP_SA_KEY }}'

      - name: 'Deploy to Cloud Run'
        run: |
          gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/enterprise-rag
          gcloud run deploy enterprise-rag \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/enterprise-rag \
            --region us-central1 \
            --platform managed
```

---

## Production Checklist

- [ ] Enable billing alerts
- [ ] Set up monitoring and alerting
- [ ] Configure automated backups
- [ ] Implement rate limiting
- [ ] Enable Cloud Armor (DDoS protection)
- [ ] Set up custom domain with SSL
- [ ] Configure IAM roles properly
- [ ] Enable audit logging
- [ ] Set up disaster recovery plan
- [ ] Document runbooks for operations
- [ ] Train team on GCP tools

---

## Support & Resources

- **GCP Documentation:** https://cloud.google.com/run/docs
- **Pricing Calculator:** https://cloud.google.com/products/calculator
- **Support:** https://cloud.google.com/support
- **Community:** https://www.googlecloudcommunity.com/

---

**Deployment Time:** ~15-30 minutes
**Estimated Cost:** $30-70/month for typical usage

🚀 **Your Enterprise RAG System is now deployed on GCP!**
