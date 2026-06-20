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

    return router