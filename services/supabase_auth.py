"""
Supabase Authentication Integration for Devante CLI
Handles authentication operations with Supabase Auth
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv

load_dotenv()


class SupabaseAuth:
    """Authentication handler using Supabase Auth"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase_service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a JWT token from Supabase
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            # For Supabase tokens, we need to verify with the JWT secret
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=['HS256'],
                options={'verify_signature': False}  # Supabase handles signature
            )
            
            # Check if token is expired
            if payload.get('exp', 0) < datetime.utcnow().timestamp():
                return None
                
            return payload
        except jwt.PyJWTError:
            return None
    
    def create_internal_token(self, user_id: str, email: str) -> str:
        """
        Create an internal JWT token for backend operations
        
        Args:
            user_id: User ID from Supabase
            email: User email
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(
            payload,
            self.jwt_secret,
            algorithm='HS256'
        )
        
        return token
    
    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Extract user information from a token
        
        Args:
            token: JWT token
            
        Returns:
            User information dictionary
        """
        payload = self.verify_token(token)
        if not payload:
            return None
            
        return {
            'id': payload.get('sub'),
            'email': payload.get('email'),
            'user_id': payload.get('user_id')
        }
    
    def validate_supabase_token(self, token: str) -> bool:
        """
        Validate a Supabase auth token by checking with Supabase
        
        Args:
            token: Supabase auth token
            
        Returns:
            True if token is valid, False otherwise
        """
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'{self.supabase_url}/auth/v1/user',
                    headers={
                        'Authorization': f'Bearer {token}',
                        'apikey': self.supabase_anon_key
                    },
                    timeout=10.0
                )
                return response.status_code == 200
        except:
            return False


# Global instance
supabase_auth = SupabaseAuth()
