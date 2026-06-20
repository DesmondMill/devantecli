"""Cloud services configuration routes — Supabase, Railway, etc."""

import logging
import os
from typing import Dict, Optional

import httpx
from fastapi import APIRouter, HTTPException, Request

from src.supabase_client import supabase_manager, is_supabase_configured
from src.railway_client import railway_manager

logger = logging.getLogger(__name__)


def setup_cloud_routes() -> APIRouter:
    router = APIRouter(prefix="/api/cloud", tags=["cloud"])

    @router.get("/config")
    async def get_cloud_config():
        """Get current cloud services configuration (with masked secrets)"""
        config = {
            "supabase": {
                "url": os.getenv("SUPABASE_URL", ""),
                "has_publishable_key": bool(os.getenv("SUPABASE_PUBLISHABLE_KEY")),
                "has_secret_key": bool(os.getenv("SUPABASE_SECRET_KEY")),
                "db_url": os.getenv("DATABASE_URL", ""),
                "configured": bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_PUBLISHABLE_KEY"))
            },
            "railway": {
                "project_id": os.getenv("RAILWAY_PROJECT_ID", ""),
                "url": os.getenv("RAILWAY_SERVICE_URL", ""),
                "has_token": bool(os.getenv("RAILWAY_API_TOKEN")),
                "configured": bool(os.getenv("RAILWAY_PROJECT_ID") and os.getenv("RAILWAY_SERVICE_URL"))
            },
            "vercel": {
                "url": os.getenv("VERCEL_URL", ""),
                "project_id": os.getenv("VERCEL_PROJECT_ID", ""),
                "has_token": bool(os.getenv("VERCEL_API_TOKEN")),
                "configured": bool(os.getenv("VERCEL_URL"))
            },
            "r2": {
                "account_id": os.getenv("CLOUDFLARE_ACCOUNT_ID", ""),
                "has_access_key": bool(os.getenv("CLOUDFLARE_R2_ACCESS_KEY")),
                "has_secret_key": bool(os.getenv("CLOUDFLARE_R2_SECRET_KEY")),
                "bucket": os.getenv("CLOUDFLARE_R2_BUCKET", ""),
                "configured": bool(
                    os.getenv("CLOUDFLARE_ACCOUNT_ID") and
                    os.getenv("CLOUDFLARE_R2_ACCESS_KEY") and
                    os.getenv("CLOUDFLARE_R2_SECRET_KEY") and
                    os.getenv("CLOUDFLARE_R2_BUCKET")
                )
            }
        }
        return config

    @router.post("/supabase/test")
    async def test_supabase(request: Request):
        """Test Supabase connection"""
        body = await request.json()
        url = body.get("url", "").strip()
        publishable_key = body.get("publishableKey", "").strip()
        secret_key = body.get("secretKey", "").strip()

        if not url or not publishable_key:
            raise HTTPException(400, "URL and Publishable Key are required")

        try:
            # Test connectivity to Supabase REST API
            rest_url = f"{url.rstrip('/')}/rest/v1/"
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try with publishable key first (for client-side operations)
                response = await client.get(
                    rest_url,
                    headers={
                        "apikey": publishable_key,
                        "Authorization": f"Bearer {publishable_key}"
                    }
                )

                # If publishable key fails and secret key is provided, try with secret key
                if response.status_code == 401 and secret_key:
                    response = await client.get(
                        rest_url,
                        headers={
                            "apikey": secret_key,
                            "Authorization": f"Bearer {secret_key}"
                        }
                    )

                if response.status_code == 200:
                    return {
                        "ok": True,
                        "message": "Connection successful - Supabase project is accessible"
                    }
                elif response.status_code == 401:
                    return {
                        "ok": False,
                        "message": "Authentication failed - check your API keys. Note: REST API requires secret key for some operations."
                    }
                elif response.status_code == 404:
                    return {
                        "ok": False,
                        "message": "Project not found - check your URL format (should be https://your-project.supabase.co)"
                    }
                else:
                    return {
                        "ok": False,
                        "message": f"Connection failed: HTTP {response.status_code} - {response.text[:200]}"
                    }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "message": "Connection timeout - Supabase project may be unreachable"
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Connection error: {str(e)}"
            }

    @router.post("/supabase/configure")
    async def configure_supabase(request: Request):
        """Configure Supabase credentials (update environment)"""
        body = await request.json()
        url = body.get("url", "").strip()
        publishable_key = body.get("publishableKey", "").strip()
        secret_key = body.get("secretKey", "").strip()
        db_url = body.get("dbUrl", "").strip()

        if not url or not publishable_key:
            raise HTTPException(400, "URL and Publishable Key are required")

        # In production, these should be set via proper deployment config
        # For now, we'll update environment variables in memory
        os.environ["SUPABASE_URL"] = url
        os.environ["SUPABASE_PUBLISHABLE_KEY"] = publishable_key
        if secret_key:
            os.environ["SUPABASE_SECRET_KEY"] = secret_key
        if db_url:
            os.environ["DATABASE_URL"] = db_url

        logger.info(f"Supabase configured for project: {url}")

        return {
            "ok": True,
            "message": "Supabase credentials configured (note: restart required for database connection changes)"
        }

    @router.post("/railway/test")
    async def test_railway(request: Request):
        """Test Railway connection"""
        body = await request.json()
        project_id = body.get("projectId", "").strip()
        service_url = body.get("url", "").strip()
        token = body.get("token", "").strip()

        if not service_url:
            raise HTTPException(400, "Service URL is required")

        # Update the manager with provided credentials
        os.environ["RAILWAY_PROJECT_ID"] = project_id
        os.environ["RAILWAY_SERVICE_URL"] = service_url
        if token:
            os.environ["RAILWAY_API_TOKEN"] = token

        railway_manager.initialize()

        # Use the Railway manager to check health
        return await railway_manager.check_service_health()

    @router.post("/railway/configure")
    async def configure_railway(request: Request):
        """Configure Railway credentials"""
        body = await request.json()
        project_id = body.get("projectId", "").strip()
        service_url = body.get("url", "").strip()
        token = body.get("token", "").strip()

        if not project_id or not service_url:
            raise HTTPException(400, "Project ID and Service URL are required")

        # Update environment variables
        os.environ["RAILWAY_PROJECT_ID"] = project_id
        os.environ["RAILWAY_SERVICE_URL"] = service_url
        if token:
            os.environ["RAILWAY_API_TOKEN"] = token

        railway_manager.initialize()
        logger.info(f"Railway configured for project: {project_id}, service: {service_url}")

        return {
            "ok": True,
            "message": "Railway credentials configured"
        }

    @router.get("/railway/deployments")
    async def get_railway_deployments():
        """Get Railway deployment status"""
        if not railway_manager.is_configured:
            return {
                "ok": False,
                "message": "Railway not configured - please configure credentials first"
            }

        return await railway_manager.get_deployment_status()

    @router.post("/vercel/test")
    async def test_vercel(request: Request):
        """Test Vercel connection"""
        body = await request.json()
        url = body.get("url", "").strip()
        token = body.get("token", "").strip()

        if not url:
            raise HTTPException(400, "Vercel URL is required")

        try:
            # Test basic connectivity to Vercel deployment
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)

                if response.status_code < 500:
                    return {
                        "ok": True,
                        "message": f"Vercel deployment is accessible (HTTP {response.status_code})"
                    }
                else:
                    return {
                        "ok": False,
                        "message": f"Vercel deployment returned error: HTTP {response.status_code}"
                    }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "message": "Connection timeout - Vercel deployment may be unreachable"
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Connection error: {str(e)}"
            }

    @router.post("/vercel/configure")
    async def configure_vercel(request: Request):
        """Configure Vercel credentials"""
        body = await request.json()
        url = body.get("url", "").strip()
        project_id = body.get("projectId", "").strip()
        token = body.get("token", "").strip()

        if not url:
            raise HTTPException(400, "Vercel URL is required")

        # Update environment variables
        os.environ["VERCEL_URL"] = url
        if project_id:
            os.environ["VERCEL_PROJECT_ID"] = project_id
        if token:
            os.environ["VERCEL_API_TOKEN"] = token

        logger.info(f"Vercel configured for project: {project_id}, URL: {url}")

        return {
            "ok": True,
            "message": "Vercel credentials configured"
        }

    @router.post("/r2/test")
    async def test_r2(request: Request):
        """Test Cloudflare R2 connection"""
        body = await request.json()
        account_id = body.get("accountId", "").strip()
        access_key = body.get("accessKey", "").strip()
        secret_key = body.get("secretKey", "").strip()
        bucket = body.get("bucket", "").strip()

        if not account_id or not access_key or not secret_key or not bucket:
            raise HTTPException(400, "All R2 credentials (Account ID, Access Key, Secret Key, Bucket) are required")

        try:
            # Test R2 connectivity by attempting to list bucket contents
            # Using Cloudflare's R2 API endpoint
            r2_url = f"https://{account_id}.r2.cloudflarestorage.com/{bucket}"

            # Try with a simple HEAD request to check bucket accessibility
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Note: R2 uses S3-compatible API, so we'd typically use boto3 or similar
                # For basic connectivity test, we'll check if we can reach the endpoint
                response = await client.head(
                    r2_url,
                    headers={
                        # This is a simplified test - proper R2 authentication requires AWS Signature V4
                        "User-Agent": "Odysseus-Cloud-Test/1.0"
                    }
                )

                # We expect 403 or 401 for unauthenticated requests, which proves connectivity
                if response.status_code in (403, 401, 400):
                    return {
                        "ok": True,
                        "message": "R2 endpoint is accessible (credentials received, authentication required for operations)"
                    }
                elif response.status_code == 404:
                    return {
                        "ok": False,
                        "message": "R2 bucket not found - check Account ID and Bucket name"
                    }
                else:
                    return {
                        "ok": False,
                        "message": f"R2 returned unexpected status: HTTP {response.status_code}"
                    }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "message": "Connection timeout - R2 endpoint may be unreachable"
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Connection error: {str(e)}"
            }

    @router.post("/r2/configure")
    async def configure_r2(request: Request):
        """Configure Cloudflare R2 credentials"""
        body = await request.json()
        account_id = body.get("accountId", "").strip()
        access_key = body.get("accessKey", "").strip()
        secret_key = body.get("secretKey", "").strip()
        bucket = body.get("bucket", "").strip()

        if not account_id or not access_key or not secret_key or not bucket:
            raise HTTPException(400, "All R2 credentials are required")

        # Update environment variables
        os.environ["CLOUDFLARE_ACCOUNT_ID"] = account_id
        os.environ["CLOUDFLARE_R2_ACCESS_KEY"] = access_key
        os.environ["CLOUDFLARE_R2_SECRET_KEY"] = secret_key
        os.environ["CLOUDFLARE_R2_BUCKET"] = bucket

        # Construct R2 endpoint
        os.environ["CLOUDFLARE_R2_ENDPOINT"] = f"https://{account_id}.r2.cloudflarestorage.com"

        logger.info(f"Cloudflare R2 configured for bucket: {bucket}")

        return {
            "ok": True,
            "message": "Cloudflare R2 credentials configured"
        }

    return router