#!/bin/bash
# Quick deployment script for GCP Cloud Run

set -e  # Exit on error

echo "==================================="
echo "Enterprise RAG - GCP Deployment"
echo "==================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed!"
    echo "Please install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
echo "📋 Enter your GCP Project ID:"
read -r PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Project ID cannot be empty!"
    exit 1
fi

# Set project
echo "🔧 Setting GCP project..."
gcloud config set project "$PROJECT_ID"

# Set region
REGION="us-central1"
echo "🌍 Using region: $REGION"

# Enable APIs
echo ""
echo "🔌 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable storage.googleapis.com

# Get API keys
echo ""
echo "🔑 Enter your OpenAI API Key:"
read -rs OPENAI_KEY

echo "🔑 Enter your xAI (Grok) API Key:"
read -rs XAI_KEY

# Create secrets
echo ""
echo "🔐 Creating secrets..."
echo -n "$OPENAI_KEY" | gcloud secrets create openai-api-key --data-file=- --replication-policy="automatic" 2>/dev/null || \
    echo -n "$OPENAI_KEY" | gcloud secrets versions add openai-api-key --data-file=-

echo -n "$XAI_KEY" | gcloud secrets create xai-api-key --data-file=- --replication-policy="automatic" 2>/dev/null || \
    echo -n "$XAI_KEY" | gcloud secrets versions add xai-api-key --data-file=-

# Grant access
echo "🔓 Granting secret access..."
gcloud secrets add-iam-policy-binding openai-api-key \
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" --quiet

gcloud secrets add-iam-policy-binding xai-api-key \
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" --quiet

# Build and push image
echo ""
echo "🏗️  Building Docker image (this may take 5-10 minutes)..."
gcloud builds submit --tag "gcr.io/$PROJECT_ID/enterprise-rag"

# Deploy to Cloud Run
echo ""
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy enterprise-rag \
    --image "gcr.io/$PROJECT_ID/enterprise-rag" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 1 \
    --set-secrets="OPENAI_API_KEY=openai-api-key:latest,XAI_API_KEY=xai-api-key:latest" \
    --set-env-vars="CHUNK_SIZE=2000,CHUNK_OVERLAP=400,TOP_K_RESULTS=8,CONTEXT_WINDOW=6"

# Get URL
echo ""
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
echo ""

SERVICE_URL=$(gcloud run services describe enterprise-rag --region "$REGION" --format 'value(status.url)')
echo "🌐 Your application is live at:"
echo "   $SERVICE_URL"
echo ""
echo "🔐 Default login credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "⚠️  IMPORTANT: Change the admin password immediately!"
echo ""
echo "📊 View logs:"
echo "   gcloud logging tail \"resource.type=cloud_run_revision\""
echo ""
echo "💰 Estimated cost: $30-70/month for typical usage"
echo ""
