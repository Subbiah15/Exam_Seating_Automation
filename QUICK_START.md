# Quick Start Guide - Authentication System

## 🎯 Start Here

### **Access the System**
- **Main Page**: http://localhost:8080/test-auth.html
- **Login Page**: http://localhost:8080/login.html
- **Backend API**: http://localhost:8000

---

## 👨‍💼 For Admin/Teacher

### **Create Account:**
1. Go to: http://localhost:8080/login.html
2. Click: "Sign up as Admin/Teacher"
3. Fill in:
   - Full Name: `John Smith`
   - Username: `john_admin` (unique, 3-20 chars)
   - Email: `john@example.com`
   - Password: `SecurePass123` (min 6 chars)
4. Click: "Create Account"
5. **Redirected to Login** ✓
6. Enter same username/password
7. **Redirected to Dashboard** ✓

### **In Dashboard:**
- Upload student data (CSV/Excel)
- Configure exam halls
- Set seating rules
- Generate arrangements
- Download PDF results

---

## 👨‍🎓 For Students

### **Create Account:**
1. Go to: http://localhost:8080/login.html
2. Click: "Sign up as Student"
3. Fill in:
   - Full Name: `Alice Johnson`
   - Username: `alice_std` (unique, 3-20 chars)
   - Email: `alice@example.com`
   - Password: `StudentPass456` (min 6 chars)
   - Student ID: `STU001` (or any format)
4. Click: "Create Account"
5. **Redirected to Login** ✓
6. Enter same username/password
7. **Redirected to Student Dashboard** ✓

### **In Dashboard:**
- View student profile
- See assigned seat
- Check exam details
- Download seat map

---

## 🔧 Server Management

### **Check Status:**
```powershell
# Check if backend is running
Invoke-WebRequest -Uri "http://localhost:8000/docs"

# Check if frontend is running
Invoke-WebRequest -Uri "http://localhost:8080/login.html"
```

### **Restart Servers:**
```powershell
# Kill all Python processes
Get-Process python | Stop-Process -Force

# Restart backend (in PowerShell)
cd c:\Users\HP\Desktop\Subbu\Working_Projects\Exam_Seating_Engine
.\venv\Scripts\Activate.ps1
uvicorn main:app --port 8000 --reload
```

### **Frontend HTTP Server:**
```powershell
# Already running on port 8080
# To restart:
cd c:\Users\HP\Desktop\Subbu\Working_Projects\Exam_Seating_Engine\frontend
python -m http.server 8080
```

---

## 🧪 Quick Test Scenarios

### **Scenario 1: Admin Creates Account and Logs In**
```
1. Admin signup: http://localhost:8080/login.html → "Sign up as Admin/Teacher"
2. Fill details with role="admin"
3. Signup completes → Redirects to login
4. Login with same credentials
5. Success → Redirects to http://localhost:8080/index.html
6. Navbar shows: "Welcome, username! (admin)"
```

### **Scenario 2: Student Creates Account and Logs In**
```
1. Student signup: http://localhost:8080/login.html → "Sign up as Student"
2. Fill details including Student ID with role="student"
3. Signup completes → Redirects to login
4. Login with same credentials
5. Success → Redirects to http://localhost:8080/student-dashboard.html
6. Navbar shows: "Welcome, username! (student)"
```

### **Scenario 3: Access Control Test**
```
1. Login as student
2. Try to access: http://localhost:8080/index.html
3. Result: Alert shown → Redirected to student-dashboard.html
4. Login as admin
5. Try to access: http://localhost:8080/student-dashboard.html
6. Result: Redirected to index.html (with role check in HTML)
```

---

## 📱 Browser Console Testing

Open browser DevTools (F12) → Console tab:

```javascript
// Check if user is logged in
console.log(auth.isAuthenticated());

// Get current user info
console.log(auth.getCurrentUser());

// Check role
console.log(auth.role);

// Logout
auth.logout();

// Get auth header
console.log(auth.getAuthHeader());
```

---

## 🔐 Security Notes

1. **Passwords** are hashed with bcrypt (never stored as plain text)
2. **JWT tokens** expire after 24 hours
3. **localStorage** stores token (check browser DevTools → Application → LocalStorage)
4. **CORS** enabled for frontend-backend communication
5. **Role-based access** enforced on both frontend and backend

---

## 📊 Database

Users are stored in: `users_store.json`

### **Example User Entry:**
```json
{
  "user_id": 1,
  "username": "john_admin",
  "password_hash": "$2b$12$...",
  "email": "john@example.com",
  "role": "admin",
  "name": "John Smith",
  "student_id": null,
  "created_at": "2026-01-31T10:30:00",
  "is_active": true
}
```

---

## ❌ Troubleshooting

### **Issue: "Cannot GET /login.html"**
- **Solution**: Make sure frontend server is running on port 8080
- **Fix**: Run `python -m http.server 8080 --directory frontend`

### **Issue: "Connection refused" when signing up**
- **Solution**: Backend server not running
- **Fix**: Run `uvicorn main:app --port 8000 --reload`

### **Issue: "Username already exists"**
- **Solution**: Username was already created
- **Fix**: Choose a different username or delete the user from `users_store.json`

### **Issue: Stuck on signup after clicking "Create Account"**
- **Solution**: Should be fixed now, but if persists:
- **Fix**: Check browser console for errors, reload page, try different username

### **Issue: Login not working**
- **Solution**: Check credentials are correct
- **Fix**: Make sure you signed up first, then login with same username/password

---

## 🎓 Role Permissions

| Feature | Admin | Teacher | Student |
|---------|-------|---------|---------|
| Access Dashboard | ✅ | ✅ | ❌ |
| Upload Students | ✅ | ✅ | ❌ |
| Create Halls | ✅ | ✅ | ❌ |
| Generate Seating | ✅ | ✅ | ❌ |
| View Results | ✅ | ✅ | ❌ |
| View Own Seat | ✅ | ✅ | ✅ |
| Student Dashboard | ❌ | ❌ | ✅ |
| Logout | ✅ | ✅ | ✅ |

---

## 📞 API Endpoints

### **Signup**
```
POST /api/auth/signup
Content-Type: application/json

{
  "name": "User Name",
  "username": "username",
  "email": "user@example.com",
  "password": "password",
  "role": "admin|teacher|student",
  "student_id": "STU001"  // Only for students
}

Response: 200 OK
{
  "success": true,
  "message": "User created successfully",
  "user_id": 1,
  "username": "username",
  "role": "admin"
}
```

### **Login**
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "username",
  "password": "password"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAi...",
  "token_type": "Bearer",
  "role": "admin",
  "user_id": 1,
  "username": "username"
}
```

### **Get User Info**
```
GET /api/auth/me
Authorization: Bearer <token>

Response: 200 OK
{
  "user_id": 1,
  "username": "username",
  "email": "user@example.com",
  "role": "admin",
  "name": "User Name"
}
```

---

## ✅ Everything is Working!

Your authentication system is fully operational. Start by visiting:

### **http://localhost:8080/test-auth.html**

Or directly login: **http://localhost:8080/login.html**

---

**Last Updated**: January 31, 2026  
**Status**: ✅ All Systems Operational
