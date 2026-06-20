# Devante CLI Cloud Migration Guide

This guide will help you migrate Devante CLI from the current Docker-based architecture to a modern cloud architecture:

- **Frontend (UI)** → Vercel
- **Database + Auth** → Supabase
- **Backend (Agent Orchestration)** → Railway
- **Local AI Models** → Ollama on your machine
- **Optional Storage** → Cloudflare R2

## Prerequisites

- Node.js 18+ installed locally
- Supabase account (free tier available)
- Railway account (free tier available)
- Cloudflare account (for R2 storage)
- Ollama installed locally for AI models
- Git repository for version control

## Phase 1: Database & Auth Setup (Supabase)

### 1.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Choose a region close to your users
4. Wait for the project to be provisioned

### 1.2 Set Up Database Schema

1. Go to your Supabase project → SQL Editor
2. Copy the contents of `supabase/schema.sql`
3. Paste and execute the SQL script
4. This will create all necessary tables and RLS policies

### 1.3 Configure Authentication

1. Go to Authentication → Settings
2. Enable email/password authentication
3. Configure your site URL (will be your Vercel domain)
4. Add redirect URLs:
   - `http://localhost:3000` (for local development)
   - `https://your-vercel-app.vercel.app` (production)

### 1.4 Get Supabase Credentials

1. Go to Project Settings → API
2. Copy these values:
   - `Project URL`
   - `anon public` key
   - `service_role` secret (for backend)

## Phase 2: Storage Setup (Cloudflare R2)

### 2.1 Create R2 Bucket

1. Go to Cloudflare Dashboard → R2
2. Create a new bucket (e.g., `devante-cli-storage`)
3. Note your Account ID from the dashboard

### 2.2 Get R2 Credentials

1. Go to R2 → Manage R2 API Tokens
2. Create an API token with Object Read & Write permissions
3. Copy the Access Key ID and Secret Access Key
4. Note the endpoint URL: `https://<account-id>.r2.cloudflarestorage.com`

## Phase 3: Backend Deployment (Railway)

### 3.1 Prepare Backend Code

1. Update `app.py` to use Supabase instead of SQLite
2. Replace file system operations with R2 storage
3. Update authentication to use Supabase Auth
4. Add CORS configuration for your Vercel domain

### 3.2 Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Create a new project
3. Select "Deploy from GitHub repo"
4. Connect your repository

### 3.3 Configure Environment Variables

Add these environment variables in Railway:

```bash
# Database
DATABASE_URL=postgresql://postgres:[password]@[host]:[port]/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# AI Models
OLLAMA_BASE_URL=http://your-local-ip:11434
OPENAI_API_KEY=your-openai-key

# Storage
CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_R2_ACCESS_KEY=your-r2-access-key
CLOUDFLARE_R2_SECRET_KEY=your-r2-secret-key
CLOUDFLARE_R2_BUCKET=devante-cli-storage

# Security
AUTH_ENABLED=true
JWT_SECRET=your-jwt-secret
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app

# Other Services
SEARXNG_INSTANCE=https://your-searxng-instance.com
```

### 3.4 Deploy

1. Railway will automatically deploy on push
2. Monitor the deployment logs
3. Once deployed, note your Railway URL

## Phase 4: Frontend Deployment (Vercel)

### 4.1 Prepare Frontend

1. Create `frontend/` directory structure
2. Move static files from `static/` to `frontend/`
3. Update API calls to use Railway backend URL
4. Configure environment variables

### 4.2 Create Vercel Project

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel` in the `frontend/` directory
3. Follow the prompts to set up the project

### 4.3 Configure Environment Variables

Add these in Vercel project settings:

```bash
VITE_API_URL=https://your-railway-app.railway.app
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### 4.4 Deploy

1. Run: `vercel --prod`
2. Note your Vercel domain

## Phase 5: Local AI Models (Ollama)

### 5.1 Install Ollama

```bash
# On Windows
winget install Ollama.Ollama

# On macOS
brew install ollama

# On Linux
curl -fsSL https://ollama.com/install.sh | sh
```

### 5.2 Configure Ollama for Remote Access

1. Start Ollama with remote access:
```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

2. Make sure your firewall allows port 11434

3. Test from Railway:
```bash
curl http://your-public-ip:11434/api/tags
```

### 5.3 Download Models

```bash
ollama pull llama2
ollama pull mistral
ollama pull codellama
```

## Phase 6: Integration & Testing

### 6.1 Update Supabase Redirect URLs

1. Add your Vercel domain to Supabase redirect URLs
2. Add your Railway URL to Supabase redirect URLs

### 6.2 Test Authentication Flow

1. Open your Vercel app
2. Try to sign up/login
3. Verify session creation in Supabase

### 6.3 Test AI Model Connection

1. Start a chat session
2. Send a message
3. Verify it connects to your local Ollama
4. Check Railway logs for connection errors

### 6.4 Test File Upload

1. Upload a document
2. Verify it's stored in Cloudflare R2
3. Check that it's accessible from the app

## Phase 7: Data Migration (Optional)

If you have existing data in SQLite:

### 7.1 Export SQLite Data

```bash
sqlite3 data/app.db .dump > backup.sql
```

### 7.2 Transform for Supabase

You'll need to transform the SQLite dump to match the Supabase schema. Key differences:
- SQLite uses INTEGER IDs, Supabase uses UUID
- SQLite has different timestamp formats
- Authentication data needs to be migrated to Supabase Auth

### 7.3 Import to Supabase

Use the Supabase dashboard or CLI to import the transformed data.

## Troubleshooting

### Railway Deployment Issues

- **Build fails**: Check requirements.txt and ensure all dependencies are listed
- **Runtime errors**: Check Railway logs for specific error messages
- **Database connection**: Verify DATABASE_URL format and credentials

### Supabase Issues

- **RLS policies**: Ensure policies allow proper access
- **Authentication**: Check redirect URLs and site URL configuration
- **Connection issues**: Verify Supabase URL and keys

### Ollama Connection Issues

- **Firewall**: Ensure port 11434 is accessible from Railway
- **Network**: Railway needs to reach your local machine (consider ngrok for testing)
- **Model availability**: Ensure models are downloaded locally

### Vercel Issues

- **API calls**: Verify CORS configuration on Railway
- **Environment variables**: Check that all required vars are set
- **Build errors**: Ensure frontend build process works locally

## Cost Estimates

**Monthly Costs (Free Tiers):**
- Supabase: $0 (500MB database, 1GB bandwidth)
- Railway: $0 (512MB RAM, $5 free credits)
- Vercel: $0 (100GB bandwidth, unlimited deployments)
- Cloudflare R2: ~$0.015/GB storage + $0.01/GB egress
- Ollama: $0 (local, your hardware)

**Estimated Total**: ~$0-5/month depending on storage and usage

## Next Steps

1. Complete Phase 1 (Supabase setup)
2. Complete Phase 2 (R2 setup)
3. Complete Phase 3 (Railway deployment)
4. Complete Phase 4 (Vercel deployment)
5. Complete Phase 5 (Ollama setup)
6. Test integration thoroughly
7. Migrate existing data if needed
8. Update DNS/custom domains if desired
9. Monitor and optimize costs

## Support

For issues with specific services:
- Supabase: [supabase.com/docs](https://supabase.com/docs)
- Railway: [docs.railway.app](https://docs.railway.app)
- Vercel: [vercel.com/docs](https://vercel.com/docs)
- Cloudflare R2: [developers.cloudflare.com/r2](https://developers.cloudflare.com/r2)
- Ollama: [ollama.com/docs](https://ollama.com/docs)
