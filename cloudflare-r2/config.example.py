"""
Cloudflare R2 Configuration for Devante CLI
Replace with your actual Cloudflare R2 credentials
"""

import os
from dotenv import load_dotenv

load_dotenv()

R2_CONFIG = {
    'account_id': os.getenv('CLOUDFLARE_ACCOUNT_ID', ''),
    'access_key_id': os.getenv('CLOUDFLARE_R2_ACCESS_KEY', ''),
    'secret_access_key': os.getenv('CLOUDFLARE_R2_SECRET_KEY', ''),
    'bucket_name': os.getenv('CLOUDFLARE_R2_BUCKET', 'devante-cli-storage'),
    'endpoint': os.getenv('CLOUDFLARE_R2_ENDPOINT', ''),
}

# For local testing with MinIO or similar S3-compatible storage
LOCAL_R2_CONFIG = {
    'endpoint_url': os.getenv('LOCAL_R2_ENDPOINT', 'http://localhost:9000'),
    'access_key_id': os.getenv('LOCAL_R2_ACCESS_KEY', 'minioadmin'),
    'secret_access_key': os.getenv('LOCAL_R2_SECRET_KEY', 'minioadmin'),
    'bucket_name': os.getenv('LOCAL_R2_BUCKET', 'devante-cli-test'),
}
