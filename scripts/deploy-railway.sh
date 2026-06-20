#!/bin/bash
# Deployment script for Railway backend

set -e

echo "🚀 Deploying Devante CLI Backend to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    echo "Please login to Railway:"
    railway login
fi

# Initialize Railway project (if not already initialized)
if [ ! -f ".railway/config.json" ]; then
    echo "📦 Initializing Railway project..."
    railway init
fi

# Set environment variables
echo "⚙️  Setting environment variables..."
railway variables set DATABASE_URL=$DATABASE_URL
railway variables set SUPABASE_URL=$SUPABASE_URL
railway variables set SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
railway variables set SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY
railway variables set OLLAMA_BASE_URL=$OLLAMA_BASE_URL
railway variables set CLOUDFLARE_ACCOUNT_ID=$CLOUDFLARE_ACCOUNT_ID
railway variables set CLOUDFLARE_R2_ACCESS_KEY=$CLOUDFLARE_R2_ACCESS_KEY
railway variables set CLOUDFLARE_R2_SECRET_KEY=$CLOUDFLARE_R2_SECRET_KEY
railway variables set CLOUDFLARE_R2_BUCKET=$CLOUDFLARE_R2_BUCKET
railway variables set AUTH_ENABLED=true
railway variables set JWT_SECRET=$JWT_SECRET
railway variables set ALLOWED_ORIGINS=$ALLOWED_ORIGINS

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your Railway app URL: $(railway domain)"
