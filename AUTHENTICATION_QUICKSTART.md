# Authentication System - Quick Start Guide

## ⚡ Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
The `.env` file is already created with default settings. In production, change:
```
SECRET_KEY=your-strong-random-key-here
```

Generate a strong key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Start Backend
```bash
python main.py
```
- Server runs on `http://localhost:8000`
- API docs available at `http://localhost:8000/docs`

### 4. Start Frontend
In the `frontend` directory:
```bash
python -m http.server 8080
```
- Frontend runs on `http://localhost:8080`

### 5. Access the Application
- **Login Page**: `http://localhost:8080/login.html`
- **Admin Dashboard**: `http://localhost:8080/index.html` (after login)
- **Student Dashboard**: `http://localhost:8080/student-dashboard.html` (after login)

## 👥 User Roles

### Admin/Teacher
- Full access to all features
- Can upload students
- Can generate seating arrangements
- Can view all results

**Login Tab**: "Admin / Teacher" tab on login page

### Student
- View-only access
- Can see their assigned seat
- Can view seat map
- **Cannot** create or modify arrangements

**Login Tab**: "Student" tab on login page

## 🚀 Creating Test Accounts

### Method 1: Using Web Interface
1. Go to `http://localhost:8080/login.html`
2. Click "Sign up as Admin/Teacher" or "Sign up as Student"
3. Fill in the form
4. Click "Create Account"
5. Login with new credentials

### Method 2: Direct JSON Edit (Not Recommended)
Edit `users_store.json` directly, but account creation via signup is recommended.

## 📝 Test Credentials

After signup, use created credentials. Default structure:
```
Username: admin_user_1
Password: admin_password_123
Role: admin
```

## 🔑 Features

### Authentication Features
✅ User registration with role selection  
✅ Secure password hashing (bcrypt)  
✅ JWT token-based authentication  
✅ 24-hour token expiration  
✅ Automatic logout on token expiry  
✅ Separate student dashboard  
✅ Role-based access control  

### Admin Features
✅ Upload student lists (CSV)  
✅ Create exam halls  
✅ Generate seating arrangements  
✅ View all arrangements  
✅ Download PDF reports  
✅ View seat maps  

### Student Features
✅ Login to personal dashboard  
✅ View assigned seat  
✅ View exam details (date, subject)  
✅ View seat map  
✅ View student ID and email  

## 🔐 Security

- Passwords hashed with bcrypt (salted)
- JWT tokens signed with HS256
- Tokens expire after 24 hours
- Authorization headers required for protected endpoints
- CORS enabled for development

## 🐛 Troubleshooting

### Issue: Can't login
**Solution**: 
- Check username is correct (case-sensitive)
- Verify password is typed correctly
- Ensure user was created successfully

### Issue: Token expired
**Solution**:
- Login again
- Tokens expire after 24 hours
- Use "Login" button to refresh

### Issue: 401 Unauthorized
**Solution**:
- Token might be invalid or expired
- Clear browser localStorage and login again
- Check backend is running

### Issue: Signup fails with "username exists"
**Solution**:
- Choose a different username
- Usernames must be unique
- Try appending a number (e.g., teacher_01)

### Issue: Frontend can't connect to backend
**Solution**:
- Check backend is running on port 8000
- Check firewall isn't blocking localhost
- Verify no other service using port 8000

## 📞 API Endpoints

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Seating (Protected)
- `GET /api/health` - Health check
- `POST /api/students/upload` - Upload CSV
- `GET /api/halls` - Get halls
- `POST /api/halls` - Create hall
- `POST /api/generate-arrangement` - Generate seating
- `GET /api/arrangements` - Get arrangements
- `GET /api/seating/arrangement/{id}` - Get arrangement details

## 💾 Data Files

- `users_store.json` - User accounts
- `data_store.json` - Seating arrangements
- `.env` - Configuration
- `requirements.txt` - Python dependencies

## 🚀 Next Steps

1. **Create Admin Account**
   - Sign up with admin role
   - Login to admin dashboard

2. **Create Student Accounts**
   - Sign up with student role
   - Note down student ID

3. **Upload Student List**
   - Use admin dashboard
   - Upload CSV with student data

4. **Generate Arrangements**
   - Configure exam halls
   - Set exam constraints
   - Generate seating

5. **Students Check Seats**
   - Students login
   - View assigned seat
   - Download seat map if needed

## 📚 Documentation

- [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md) - Detailed auth documentation
- [README.md](README.md) - Project overview
- [PROJECT_SPECIFICATION.md](PROJECT_SPECIFICATION.md) - System specification

## 🎯 Tips

1. **Test Both Roles**: Create both admin and student accounts to test both flows
2. **Check Browser Console**: If something breaks, check browser dev tools (F12)
3. **Check Backend Logs**: Backend prints errors to console
4. **Use Private Browsing**: For testing different login states
5. **Clear localStorage**: If having token issues, clear localStorage (F12 → Application)

## ⚙️ Configuration

Edit `.env` to change:
```
SECRET_KEY                  # JWT signing key
API_HOST                    # Backend host
API_PORT                    # Backend port
FRONTEND_URL                # Frontend URL
BACKEND_URL                 # Backend URL
DATABASE_FILE               # Seating data file
USERS_DATABASE_FILE         # User data file
```

## 🔍 File Locations

- Auth Module: `auth.py`
- User Database: `users_db.py`
- Backend: `main.py`
- Login Page: `frontend/login.html`
- Signup Page: `frontend/signup.html`
- Student Dashboard: `frontend/student-dashboard.html`
- Auth Manager: `frontend/js/auth.js`
- Admin Dashboard: `frontend/index.html`

## 📊 System Status

**Status**: ✅ PRODUCTION READY

**Components Implemented**:
- ✅ User registration
- ✅ User authentication
- ✅ JWT tokens
- ✅ Role-based access
- ✅ Password hashing
- ✅ Login/Signup UI
- ✅ Student dashboard
- ✅ Admin dashboard
- ✅ Token validation
- ✅ Logout functionality

## 💡 Common Tasks

### Change Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy output and set in `.env`

### Reset Database
Remove `users_store.json` - it will be recreated on next user creation

### View All Users
Edit `frontend/js/app.js` and use admin panel (feature to be added)

### Delete User Account
Manually edit `users_store.json` and remove user entry

## 📞 Support

For issues:
1. Check logs in terminal
2. Check browser console (F12)
3. Review documentation files
4. Clear cache and try again

---

**Ready to go!** 🚀 Start with the quick setup above.
