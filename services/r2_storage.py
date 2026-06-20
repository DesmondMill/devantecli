"""
Cloudflare R2 Storage Integration for Devante CLI
Handles file storage operations with Cloudflare R2
"""

import os
import boto3
from typing import Optional, BinaryIO
from dotenv import load_dotenv

load_dotenv()


class R2StorageClient:
    """Client for interacting with Cloudflare R2 storage"""
    
    def __init__(self):
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
        self.access_key = os.getenv('CLOUDFLARE_R2_ACCESS_KEY')
        self.secret_key = os.getenv('CLOUDFLARE_R2_SECRET_KEY')
        self.bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET', 'devante-cli-storage')
        
        # R2 endpoint
        self.endpoint = os.getenv(
            'CLOUDFLARE_R2_ENDPOINT',
            f'https://{self.account_id}.r2.cloudflarestorage.com'
        )
        
        # Initialize S3 client (R2 is S3-compatible)
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name='auto'
        )
    
    def upload_file(self, file_data: BinaryIO, filename: str, 
                   content_type: str = 'application/octet-stream',
                   metadata: dict = None) -> str:
        """
        Upload a file to R2 storage
        
        Args:
            file_data: File-like object to upload
            filename: Name for the file in storage
            content_type: MIME type of the file
            metadata: Optional metadata dictionary
            
        Returns:
            URL of the uploaded file
        """
        extra_args = {'ContentType': content_type}
        if metadata:
            extra_args['Metadata'] = metadata
        
        self.s3_client.upload_fileobj(
            file_data,
            self.bucket_name,
            filename,
            ExtraArgs=extra_args
        )
        
        return f"{self.endpoint}/{self.bucket_name}/{filename}"
    
    def download_file(self, filename: str) -> bytes:
        """
        Download a file from R2 storage
        
        Args:
            filename: Name of the file in storage
            
        Returns:
            File content as bytes
        """
        response = self.s3_client.get_object(
            Bucket=self.bucket_name,
            Key=filename
        )
        return response['Body'].read()
    
    def delete_file(self, filename: str) -> None:
        """
        Delete a file from R2 storage
        
        Args:
            filename: Name of the file in storage
        """
        self.s3_client.delete_object(
            Bucket=self.bucket_name,
            Key=filename
        )
    
    def file_exists(self, filename: str) -> bool:
        """
        Check if a file exists in R2 storage
        
        Args:
            filename: Name of the file in storage
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            return True
        except:
            return False
    
    def list_files(self, prefix: str = '') -> list:
        """
        List files in R2 storage with optional prefix filter
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            List of file information dictionaries
        """
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix
        )
        
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    'name': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'url': f"{self.endpoint}/{self.bucket_name}/{obj['Key']}"
                })
        
        return files
    
    def get_file_url(self, filename: str, expires_in: int = 3600) -> str:
        """
        Generate a presigned URL for file access
        
        Args:
            filename: Name of the file in storage
            expires_in: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL for the file
        """
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': filename},
            ExpiresIn=expires_in
        )
    
    def get_file_metadata(self, filename: str) -> dict:
        """
        Get metadata for a file
        
        Args:
            filename: Name of the file in storage
            
        Returns:
            Dictionary containing file metadata
        """
        response = self.s3_client.head_object(
            Bucket=self.bucket_name,
            Key=filename
        )
        
        return {
            'content_type': response.get('ContentType'),
            'size': response.get('ContentLength'),
            'last_modified': response.get('LastModified'),
            'metadata': response.get('Metadata', {}),
            'etag': response.get('ETag')
        }


# Global instance
r2_storage = R2StorageClient()
