# Firebase Integration Guide

This guide explains how to integrate Firebase for database, authentication, and storage to replace the removed Supabase, Railway, and Cloudflare R2 services.

## Overview

The project now uses SQLite as the default database. To use Firebase instead, you'll need to:

1. Set up a Firebase project
2. Configure Firebase Authentication
3. Configure Firebase Firestore (Database)
4. Configure Firebase Storage
5. Update the application code

## Firebase Setup

### 1. Create Firebase Project

1. Go to https://console.firebase.google.com/
2. Click "Add project" and follow the setup wizard
3. Enable Authentication, Firestore Database, and Storage

### 2. Get Firebase Configuration

1. In Firebase Console, go to Project Settings
2. Scroll down to "Your apps" section
3. Add a web app to get configuration values

### 3. Install Firebase SDK

```bash
pip install firebase-admin
```

### 4. Configure Environment Variables

Add these to your `.env` file:

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

### 5. Download Service Account Key

1. In Firebase Console → Project Settings → Service Accounts
2. Generate new private key
3. Save the JSON file as `firebase-service-account.json` in the project root

## Database Migration

If you want to migrate from SQLite to Firebase Firestore:

### Option 1: Start Fresh
- Use Firebase Firestore directly with no migration
- Existing SQLite data will remain but won't be synchronized

### Option 2: Manual Migration
- Export SQLite data to JSON
- Import into Firebase Firestore using Firebase Console or admin SDK
- Update application database configuration to use Firebase

## Authentication Integration

Firebase Authentication can replace any auth system:

### Supported Auth Methods:
- Email/Password
- Google Sign-In
- GitHub
- Anonymous
- Phone

### Implementation:
```python
from firebase_admin import auth

# Create user
user = auth.create_user(
    email='user@example.com',
    password='password'
)

# Verify ID token
decoded_token = auth.verify_id_token(id_token)
```

## Storage Integration

Firebase Storage replaces Cloudflare R2:

### Upload Files:
```python
from firebase_admin import storage

bucket = storage.bucket('your-bucket')
blob = bucket.blob('file-path')
blob.upload_from_filename(local_file)
```

### Configuration:
- Enable Firebase Storage in Firebase Console
- Set up security rules
- Configure CORS if needed for web access

## Application Configuration

To switch from SQLite to Firebase:

### 1. Update Database Configuration
- Modify `core/database.py` to use Firebase Firestore instead of SQLAlchemy
- Use `firebase_admin.firestore` client

### 2. Update Authentication
- Replace existing auth middleware with Firebase Auth
- Use Firebase ID tokens for session management

### 3. Update File Storage
- Replace any Cloudflare R2 storage code with Firebase Storage
- Update file upload routes to use Firebase Storage

## Benefits of Firebase

- **Real-time Database**: Real-time data synchronization
- **Authentication**: Built-in auth system with multiple providers
- **Storage**: Scalable file storage with CDN
- **Hosting**: Built-in web hosting (can replace Railway/Vercel)
- **Security**: Built-in security rules and permissions
- **Scalability**: Auto-scaling infrastructure

## Migration Checklist

- [ ] Create Firebase project
- [ ] Enable required services (Auth, Firestore, Storage)
- [ ] Generate service account key
- [ ] Install Firebase Admin SDK
- [ ] Configure environment variables
- [ ] Update database configuration code
- [ ] Update authentication system
- [ ] Update file storage system
- [ ] Test all functionality
- [ ] Deploy and verify

## Next Steps

1. Set up your Firebase project
2. Install the Firebase SDK: `pip install firebase-admin`
3. Configure environment variables
4. Update the application code to use Firebase services
5. Test the integration

## Resources

- Firebase Documentation: https://firebase.google.com/docs
- Firebase Admin SDK: https://firebase.google.com/docs/admin/setup
- Firestore Security Rules: https://firebase.google.com/docs/firestore/security
- Firebase Storage Security: https://firebase.google.com/docs/storage/security