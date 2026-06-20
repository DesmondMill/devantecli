"""Railway client integration for Odysseus"""

import logging
import os
from typing import Optional, Dict, Any

import httpx

logger = logging.getLogger(__name__)


class RailwayManager:
    """Manages Railway API interactions"""

    def __init__(self):
        self._project_id: Optional[str] = None
        self._service_url: Optional[str] = None
        self._api_token: Optional[str] = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize Railway client from environment variables"""
        self._project_id = os.getenv("RAILWAY_PROJECT_ID", "").strip()
        self._service_url = os.getenv("RAILWAY_SERVICE_URL", "").strip()
        self._api_token = os.getenv("RAILWAY_API_TOKEN", "").strip()

        if not self._project_id or not self._service_url:
            logger.info("Railway credentials not configured")
            return False

        self._initialized = True
        logger.info(f"Railway manager initialized for project: {self._project_id}")
        return True

    @property
    def is_configured(self) -> bool:
        """Check if Railway is properly configured"""
        return self._initialized

    @property
    def project_id(self) -> Optional[str]:
        """Get Railway project ID"""
        if not self._initialized:
            self.initialize()
        return self._project_id

    @property
    def service_url(self) -> Optional[str]:
        """Get Railway service URL"""
        if not self._initialized:
            self.initialize()
        return self._service_url

    async def check_service_health(self) -> Dict[str, Any]:
        """Check if the Railway service is healthy"""
        if not self._service_url:
            return {
                "ok": false,
                "message": "Railway service URL not configured"
            }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try health endpoint first
                health_url = f"{self._service_url.rstrip('/')}/health"
                response = await client.get(health_url)

                if response.status_code == 200:
                    return {
                        "ok": True,
                        "message": "Railway service is healthy",
                        "status_code": response.status_code
                    }

                # Fallback to root endpoint
                response = await client.get(self._service_url)
                if response.status_code < 500:
                    return {
                        "ok": True,
                        "message": f"Railway service is accessible (HTTP {response.status_code})",
                        "status_code": response.status_code
                    }
                else:
                    return {
                        "ok": False,
                        "message": f"Railway service error: HTTP {response.status_code}",
                        "status_code": response.status_code
                    }
        except httpx.TimeoutException:
            return {
                "ok": False,
                "message": "Railway service connection timeout"
            }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Railway service connection error: {str(e)}"
            }

    async def get_deployment_status(self) -> Dict[str, Any]:
        """Get deployment status from Railway API"""
        if not self._api_token or not self._project_id:
            return {
                "ok": False,
                "message": "Railway API token or project ID not configured"
            }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "Authorization": f"Bearer {self._api_token}",
                    "Content-Type": "application/json"
                }

                # Get project deployments
                url = f"https://backboard.railway.app/graphql/v2"
                query = """
                query($projectId: String!) {
                    project(id: $projectId) {
                        deployments(first: 5, orderBy: {updatedAt: DESC}) {
                            edges {
                                node {
                                    id
                                    status
                                    createdAt
                                    updatedAt
                                    domain
                                }
                            }
                        }
                    }
                }
                """

                response = await client.post(
                    url,
                    json={"query": query, "variables": {"projectId": self._project_id}},
                    headers=headers
                )

                if response.status_code == 200:
                    data = response.json()
                    if "data" in data and "project" in data["data"]:
                        deployments = data["data"]["project"]["deployments"]["edges"]
                        return {
                            "ok": True,
                            "deployments": [edge["node"] for edge in deployments],
                            "message": f"Found {len(deployments)} recent deployments"
                        }
                    else:
                        return {
                            "ok": False,
                            "message": "Invalid response from Railway API"
                        }
                else:
                    return {
                        "ok": False,
                        "message": f"Railway API error: HTTP {response.status_code}"
                    }
        except Exception as e:
            return {
                "ok": False,
                "message": f"Failed to get deployment status: {str(e)}"
            }


# Global instance
railway_manager = RailwayManager()


def get_railway_manager() -> RailwayManager:
    """Get the global Railway manager instance"""
    return railway_manager