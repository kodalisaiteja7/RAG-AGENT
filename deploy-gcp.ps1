# PowerShell deployment script for GCP Cloud Run
# Enterprise RAG System

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Enterprise RAG - GCP Deployment" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check if gcloud is installed
try {
    $null = gcloud --version
} catch {
    Write-Host "❌ gcloud CLI is not installed!" -ForegroundColor Red
    Write-Host "Please install from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Get project ID
Write-Host "📋 Enter your GCP Project ID:" -ForegroundColor Green
$PROJECT_ID = Read-Host

if ([string]::IsNullOrWhiteSpace($PROJECT_ID)) {
    Write-Host "❌ Project ID cannot be empty!" -ForegroundColor Red
    exit 1
}

# Set project
Write-Host "🔧 Setting GCP project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

# Set region
$REGION = "us-central1"
Write-Host "🌍 Using region: $REGION" -ForegroundColor Yellow

# Enable APIs
Write-Host ""
Write-Host "🔌 Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable storage.googleapis.com

# Get API keys
Write-Host ""
Write-Host "🔑 Enter your OpenAI API Key:" -ForegroundColor Green
$OPENAI_KEY = Read-Host -AsSecureString
$OPENAI_KEY_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($OPENAI_KEY))

Write-Host "🔑 Enter your xAI (Grok) API Key:" -ForegroundColor Green
$XAI_KEY = Read-Host -AsSecureString
$XAI_KEY_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($XAI_KEY))

# Create secrets
Write-Host ""
Write-Host "🔐 Creating secrets..." -ForegroundColor Yellow

# Create or update OpenAI secret
$openaiSecretExists = gcloud secrets describe openai-api-key 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Updating existing openai-api-key secret..."
    echo $OPENAI_KEY_PLAIN | gcloud secrets versions add openai-api-key --data-file=-
} else {
    Write-Host "Creating new openai-api-key secret..."
    echo $OPENAI_KEY_PLAIN | gcloud secrets create openai-api-key --data-file=- --replication-policy="automatic"
}

# Create or update xAI secret
$xaiSecretExists = gcloud secrets describe xai-api-key 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Updating existing xai-api-key secret..."
    echo $XAI_KEY_PLAIN | gcloud secrets versions add xai-api-key --data-file=-
} else {
    Write-Host "Creating new xai-api-key secret..."
    echo $XAI_KEY_PLAIN | gcloud secrets create xai-api-key --data-file=- --replication-policy="automatic"
}

# Grant access
Write-Host "🔓 Granting secret access..." -ForegroundColor Yellow
gcloud secrets add-iam-policy-binding openai-api-key `
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" --quiet 2>$null

gcloud secrets add-iam-policy-binding xai-api-key `
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" --quiet 2>$null

# Build and push image
Write-Host ""
Write-Host "🏗️  Building Docker image (this may take 5-10 minutes)..." -ForegroundColor Yellow
gcloud builds submit --tag "gcr.io/$PROJECT_ID/enterprise-rag"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

# Deploy to Cloud Run
Write-Host ""
Write-Host "🚀 Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy enterprise-rag `
    --image "gcr.io/$PROJECT_ID/enterprise-rag" `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 4Gi `
    --cpu 2 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 1 `
    --set-secrets="OPENAI_API_KEY=openai-api-key:latest,XAI_API_KEY=xai-api-key:latest" `
    --set-env-vars="CHUNK_SIZE=2000,CHUNK_OVERLAP=400,TOP_K_RESULTS=8,CONTEXT_WINDOW=6"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}

# Get URL
Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

$SERVICE_URL = gcloud run services describe enterprise-rag --region $REGION --format "value(status.url)"
Write-Host "🌐 Your application is live at:" -ForegroundColor Cyan
Write-Host "   $SERVICE_URL" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Default login credentials:" -ForegroundColor Yellow
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANT: Change the admin password immediately!" -ForegroundColor Red
Write-Host ""
Write-Host "📊 View logs:" -ForegroundColor Cyan
Write-Host '   gcloud logging tail "resource.type=cloud_run_revision"' -ForegroundColor White
Write-Host ""
Write-Host "💰 Estimated cost: `$30-70/month for typical usage" -ForegroundColor Green
Write-Host ""

# Clear sensitive variables
$OPENAI_KEY_PLAIN = $null
$XAI_KEY_PLAIN = $null
