# Multi-User System - Quick Start Guide

## What's New

### Enterprise Features
- ✅ **Multi-User Authentication** - Secure login system with user management
- ✅ **Admin Knowledge Base** - Shared regulations database accessible to all users
- ✅ **User-Specific KB** - Each user can upload private documents
- ✅ **Professional UI** - Modern, polished interface with role-based access
- ✅ **Admin Panel** - User management, document stats, and system administration
- ✅ **Production Ready** - Docker deployment with monitoring and backups

### Architecture

```
Admin KB (Shared)          User KB (Private)
      │                          │
      └──────────┬───────────────┘
                 │
         Combined Search Results
                 │
           RAG Expert (Grok-4)
                 │
              Response
```

## Quick Start

### 1. Run the Multi-User Application

```bash
python -m streamlit run app_multiuser.py
```

### 2. Login

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Change this immediately after first login!**

### 3. Admin Setup

As admin, you can:

1. **Create Users**
   - Go to "Admin Panel" tab
   - Click "Add New User"
   - Enter username, full name, password, and role
   - Click "Create User"

2. **Manage Users**
   - View all users and their document counts
   - Delete users (except admin)
   - Monitor system statistics

### 4. User Experience

Regular users can:

1. **Ask Questions**
   - Access admin KB automatically
   - Results from both admin and personal documents
   - Sources clearly labeled (Admin KB vs My Documents)

2. **Upload Private Documents**
   - Click "Add Document" in sidebar
   - Upload PDF file
   - Documents only visible to that user
   - Instant search capability

## File Structure

```
New Files Created:
├── app_multiuser.py              # Multi-user Streamlit app
├── user_manager.py               # User authentication & management
├── multi_user_vector_store.py   # Dual vector store (admin + user)
├── users.json                    # User database (auto-created)
├── user_data/                    # User-specific data directory
│   └── {username}/
│       ├── user_kb.json          # User's documents
│       └── user_vectordb/        # User's vector database
├── Dockerfile                    # Container image
├── docker-compose.yml            # Orchestration config
├── .dockerignore                 # Docker build exclusions
├── .streamlit/config.toml        # UI configuration
├── DEPLOYMENT.md                 # Complete deployment guide
└── MULTIUSER_QUICKSTART.md       # This file
```

## Testing the System

### Test Scenario 1: Admin Workflow

1. Login as admin
2. Go to Admin Panel
3. Create two test users:
   - User: `john` / Password: `test123` / Role: `user`
   - User: `jane` / Password: `test456` / Role: `user`
4. Ask a question → Should get results from admin KB
5. Logout

### Test Scenario 2: User Workflow

1. Login as `john`
2. Ask: "what is check forgery insurance fund?"
   - Should get answer from admin KB
3. Upload a PDF document
4. Ask question about your document
   - Should get results from both admin KB and your document
5. Logout

### Test Scenario 3: Isolation Test

1. Login as `jane`
2. Ask same question as john's uploaded doc
   - Should NOT see john's document in results
   - Only admin KB and jane's own documents
3. Confirms proper user isolation ✅

## Key Differences from Single-User Version

| Feature | Old (app.py) | New (app_multiuser.py) |
|---------|--------------|------------------------|
| Authentication | ❌ None | ✅ Login required |
| Knowledge Base | Single shared | Admin (shared) + User (private) |
| User Management | ❌ None | ✅ Admin panel |
| UI Design | Basic | Professional with themes |
| Document Upload | Adds to shared KB | Adds to user's private KB |
| Deployment | Single instance | Multi-tenant ready |

## Production Deployment

### Option 1: Docker (Recommended)

```bash
# Build and run
docker-compose up -d

# Access at http://localhost:8501
```

### Option 2: Cloud Platforms

See `DEPLOYMENT.md` for detailed guides on:
- AWS (ECS, EC2)
- Azure (Container Instances, App Service)
- Google Cloud (Cloud Run)
- DigitalOcean (App Platform)

### Option 3: Kubernetes

For enterprise scale with auto-scaling and high availability.

## Security Considerations

### Must Do Before Production:

1. **Change Admin Password**
   ```python
   # In app, admin can use "Change Password" feature
   # Or via user_manager:
   from user_manager import get_user_manager
   um = get_user_manager()
   um.change_password("admin", "your_strong_password")
   ```

2. **Use Strong Password Hashing**
   - Current: SHA-256
   - Recommended: bcrypt or Argon2
   - See `user_manager.py` line 28

3. **Enable HTTPS**
   - Use reverse proxy (Nginx)
   - Get SSL certificate (Let's Encrypt)
   - See `DEPLOYMENT.md` for configuration

4. **Implement Rate Limiting**
   - Prevent brute force attacks
   - Limit API calls per user

5. **Add Session Management**
   - Session timeout
   - Concurrent session limits

## Monitoring

### Health Check
```bash
curl http://localhost:8501/_stcore/health
```

### View Logs
```bash
# Docker
docker logs -f regulatory-rag-app

# Docker Compose
docker-compose logs -f
```

### Database Stats
Login as admin → Check sidebar for:
- Total admin chunks
- Total user documents
- Per-user statistics

## Backup & Recovery

### Backup Critical Data

```bash
# User data
tar -czf backup_users_$(date +%Y%m%d).tar.gz user_data/ users.json

# Admin KB
cp onestream_kb.json backup_admin_kb_$(date +%Y%m%d).json

# Vector databases
tar -czf backup_vectordb_$(date +%Y%m%d).tar.gz onestream_vectordb/
```

### Restore

```bash
# Restore user data
tar -xzf backup_users_YYYYMMDD.tar.gz

# Restore admin KB
cp backup_admin_kb_YYYYMMDD.json onestream_kb.json

# Rebuild vector databases
python vector_store.py
```

## Customization

### Branding

Edit `app_multiuser.py` line 31-150 for:
- Logo
- Color scheme
- Company name
- Custom styling

### Authentication Provider

Replace simple auth in `user_manager.py` with:
- OAuth 2.0 (Google, Microsoft)
- LDAP/Active Directory
- SAML
- Auth0

### Storage Backend

Replace JSON storage with:
- PostgreSQL
- MySQL
- MongoDB
- Cloud databases (RDS, CosmosDB, etc.)

## Troubleshooting

### Issue: Can't login

**Solution:**
- Verify users.json exists
- Check credentials (case-sensitive)
- Delete users.json to reset (recreates admin)

### Issue: User documents not showing

**Solution:**
```bash
# Check user vector database
ls -la user_data/{username}/user_vectordb/

# Rebuild if needed
python -c "
from multi_user_vector_store import MultiUserVectorStore
vs = MultiUserVectorStore('{username}')
vs.embed_user_documents('user_data/{username}/user_kb.json')
"
```

### Issue: Admin KB not accessible

**Solution:**
```bash
# Rebuild admin vector database
python vector_store.py
```

## Next Steps

1. ✅ Test locally with multiple users
2. ✅ Deploy to staging environment
3. ✅ Configure HTTPS and domain
4. ✅ Set up monitoring and backups
5. ✅ Train users and admins
6. ✅ Deploy to production

## Support

For deployment assistance or issues:
- Review `DEPLOYMENT.md` for detailed guides
- Check GitHub Issues
- Contact: [Your Support Email]

---

**Ready to Deploy!** 🚀
