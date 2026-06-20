"""
Supabase Client Integration for Devante CLI
Handles database operations and authentication with Supabase
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
from dotenv import load_dotenv

load_dotenv()


class SupabaseClient:
    """Client for interacting with Supabase database and auth"""
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.client = httpx.AsyncClient(
            base_url=self.url,
            headers={
                'apikey': self.service_role_key,
                'Authorization': f'Bearer {self.service_role_key}',
                'Content-Type': 'application/json'
            },
            timeout=30.0
        )
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    # Database Operations
    async def create_session(self, user_id: str, title: str = "New Chat") -> Dict[str, Any]:
        """Create a new chat session"""
        response = await self.client.post(
            '/rest/v1/sessions',
            json={
                'user_id': user_id,
                'title': title
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user"""
        response = await self.client.get(
            '/rest/v1/sessions',
            params={
                'user_id': f'eq.{user_id}',
                'order': 'updated_at.desc'
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific session"""
        response = await self.client.get(
            f'/rest/v1/sessions?id=eq.{session_id}'
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        return data[0] if data else None
    
    async def update_session(self, session_id: str, title: str) -> Dict[str, Any]:
        """Update session title"""
        response = await self.client.patch(
            f'/rest/v1/sessions?id=eq.{session_id}',
            json={'title': title}
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_session(self, session_id: str) -> None:
        """Delete a session"""
        response = await self.client.delete(
            f'/rest/v1/sessions?id=eq.{session_id}'
        )
        response.raise_for_status()
    
    async def create_message(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new message in a session"""
        response = await self.client.post(
            '/rest/v1/messages',
            json={
                'session_id': session_id,
                'role': role,
                'content': content,
                'metadata': metadata or {}
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a session"""
        response = await self.client.get(
            '/rest/v1/messages',
            params={
                'session_id': f'eq.{session_id}',
                'order': 'created_at.asc'
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def create_document(self, user_id: str, title: str, content: str = None, 
                            file_path: str = None, file_type: str = None, 
                            file_size: int = None, storage_path: str = None) -> Dict[str, Any]:
        """Create a new document"""
        response = await self.client.post(
            '/rest/v1/documents',
            json={
                'user_id': user_id,
                'title': title,
                'content': content,
                'file_path': file_path,
                'file_type': file_type,
                'file_size': file_size,
                'storage_path': storage_path
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a user"""
        response = await self.client.get(
            '/rest/v1/documents',
            params={
                'user_id': f'eq.{user_id}',
                'order': 'updated_at.desc'
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_document(self, document_id: str) -> None:
        """Delete a document"""
        response = await self.client.delete(
            f'/rest/v1/documents?id=eq.{document_id}'
        )
        response.raise_for_status()
    
    async def create_note(self, user_id: str, title: str, content: str = None,
                         is_completed: bool = False, due_date: datetime = None) -> Dict[str, Any]:
        """Create a new note"""
        response = await self.client.post(
            '/rest/v1/notes',
            json={
                'user_id': user_id,
                'title': title,
                'content': content,
                'is_completed': is_completed,
                'due_date': due_date.isoformat() if due_date else None
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_notes(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all notes for a user"""
        response = await self.client.get(
            '/rest/v1/notes',
            params={
                'user_id': f'eq.{user_id}',
                'order': 'created_at.desc'
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def update_note(self, note_id: str, **kwargs) -> Dict[str, Any]:
        """Update a note"""
        response = await self.client.patch(
            f'/rest/v1/notes?id=eq.{note_id}',
            json=kwargs
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_note(self, note_id: str) -> None:
        """Delete a note"""
        response = await self.client.delete(
            f'/rest/v1/notes?id=eq.{note_id}'
        )
        response.raise_for_status()
    
    # Authentication Operations
    async def sign_up(self, email: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """Sign up a new user"""
        response = await self.client.post(
            '/auth/v1/signup',
            json={
                'email': email,
                'password': password,
                'data': {'full_name': full_name} if full_name else {}
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in a user"""
        response = await self.client.post(
            '/auth/v1/token?grant_type=password',
            json={
                'email': email,
                'password': password
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def sign_out(self, access_token: str) -> None:
        """Sign out a user"""
        response = await self.client.post(
            '/auth/v1/logout',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        response.raise_for_status()
    
    async def get_user(self, access_token: str) -> Dict[str, Any]:
        """Get current user"""
        response = await self.client.get(
            '/auth/v1/user',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        response.raise_for_status()
        return response.json()
    
    async def reset_password(self, email: str) -> None:
        """Send password reset email"""
        response = await self.client.post(
            '/auth/v1/recover',
            json={'email': email}
        )
        response.raise_for_status()


# Global instance
supabase = SupabaseClient()
