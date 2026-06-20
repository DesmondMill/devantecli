"""Supabase client integration for Odysseus"""

import logging
import os
from typing import Optional

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None
    create_client = None

logger = logging.getLogger(__name__)


class SupabaseManager:
    """Manages Supabase client connection and operations"""

    def __init__(self):
        self._client: Optional[Client] = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize Supabase client from environment variables"""
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase Python client not installed - Supabase features disabled")
            return False

        supabase_url = os.getenv("SUPABASE_URL", "").strip()
        supabase_key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "").strip()

        if not supabase_url or not supabase_key:
            logger.info("Supabase credentials not configured - using default SQLite")
            return False

        try:
            self._client = create_client(supabase_url, supabase_key)
            self._initialized = True
            logger.info(f"Supabase client initialized for project: {supabase_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            return False

    @property
    def client(self) -> Optional[Client]:
        """Get the Supabase client, initializing if necessary"""
        if not self._initialized:
            self.initialize()
        return self._client

    @property
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured"""
        return self._initialized and self._client is not None

    def get_database_url(self) -> str:
        """Get the Supabase PostgreSQL connection URL"""
        db_url = os.getenv("DATABASE_URL", "").strip()
        if db_url and "supabase" in db_url.lower():
            return db_url

        # Try to construct from Supabase URL if DATABASE_URL not set
        supabase_url = os.getenv("SUPABASE_URL", "").strip()
        if supabase_url and "supabase.co" in supabase_url:
            # Extract project reference from URL
            project_ref = supabase_url.replace("https://", "").replace(".supabase.co", "")
            # Default to postgresql:// protocol
            return f"postgresql://postgres:[password]@db.{project_ref}.supabase.co:5432/postgres"

        return ""


# Global instance
supabase_manager = SupabaseManager()


def get_supabase_client() -> Optional[Client]:
    """Get the global Supabase client instance"""
    return supabase_manager.client


def is_supabase_configured() -> bool:
    """Check if Supabase is properly configured"""
    return supabase_manager.is_configured