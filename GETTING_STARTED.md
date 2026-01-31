# 🚀 Getting Started with Authentication

## In 3 Steps (literally)

### Step 1: Start Backend
```bash
cd c:\Users\HP\Desktop\Subbu\Working_Projects\Exam_Seating_Engine
python main.py
```

Output should show:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start Frontend (in new terminal)
```bash
cd c:\Users\HP\Desktop\Subbu\Working_Projects\Exam_Seating_Engine\frontend
python -m http.server 8080
```

Output should show:
```
Serving HTTP on 0.0.0.0 port 8080
```

### Step 3: Open Browser
```
http://localhost:8080/login.html
```

**BOOM! 🎉 Authentication system is running!**

---

## First Time Setup (Testing)

### Test Admin Account

1. **Go to**: `http://localhost:8080/login.html`
2. **Click**: "Sign up as Admin/Teacher" link at bottom
3. **Fill in**:
   - Full Name: `Test Admin`
   - Username: `admin_test`
   - Email: `admin@test.com`
   - Password: `Test@1234`
   - Confirm: `Test@1234`
4. **Click**: "Create Account"
5. **Redirected**: Back to login page
6. **Enter**:
   - Username: `admin_test`
   - Password: `Test@1234`
7. **Click**: "Login"
8. **Result**: 🎉 Logged into Admin Dashboard!

### Test Student Account

1. **Go to**: `http://localhost:8080/login.html`
2. **Switch to**: "Student" tab
3. **Click**: "Sign up as Student" link
4. **Fill in**:
   - Full Name: `Test Student`
   - Username: `student_test`
   - Email: `student@test.com`
   - Password: `Test@1234`
   - Confirm: `Test@1234`
   - Student ID: `STU001`
5. **Click**: "Create Account"
6. **Login with**:
   - Username: `student_test`
   - Password: `Test@1234`
7. **Result**: 🎉 Student Dashboard (no seating yet)

---

## Features to Try

### As Admin:
✅ Upload student CSV  
✅ Create exam halls  
✅ Generate seating  
✅ View results  
✅ Download PDF  
✅ View seat maps  

### As Student:
✅ View dashboard  
✅ See seating assignment (after admin generates)  
✅ View seat map  
✅ Logout safely  

---

## File Locations

```
All files in: c:\Users\HP\Desktop\Subbu\Working_Projects\Exam_Seating_Engine\

Key Files:
- auth.py                    ← Authentication logic
- users_db.py              ← User storage
- main.py                  ← Backend API
- .env                     ← Configuration
- frontend/login.html      ← Login page
- frontend/signup.html     ← Signup page
- frontend/student-dashboard.html ← Student view
- frontend/js/auth.js      ← Token management
```

---

## Common Errors & Fixes

### ❌ "Can't connect to localhost:8000"
**Fix**: Make sure backend is running (`python main.py`)

### ❌ "Can't connect to localhost:8080"
**Fix**: Make sure frontend server is running (`python -m http.server 8080`)

### ❌ "Login fails - username or password wrong"
**Fix**: Check username exists and password is correct (case-sensitive)

### ❌ "Page shows blank/white screen"
**Fix**: 
- Press F12 to open developer console
- Check for errors
- Refresh page (Ctrl+R)

### ❌ "Still on login page after login"
**Fix**: Token might not be saved
- Clear browser cache (Ctrl+Shift+Delete)
- Try again

---

## Quick Command Reference

```bash
# Start backend
python main.py

# Start frontend (different terminal)
cd frontend
python -m http.server 8080

# Stop server
Ctrl+C

# View stored users (optional)
cat users_store.json  # or on Windows: type users_store.json
```

---

## API Testing (Optional)

### Login via API
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin_test\",\"password\":\"Test@1234\"}"
```

Response will include token:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "role": "admin",
  "user_id": 1,
  "username": "admin_test"
}
```

### Use Token to Get User Info
```bash
# Replace TOKEN with the access_token from above
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/auth/me
```

---

## Next Steps After Setup

1. **Admin Setup**
   - Upload test student list
   - Create exam halls
   - Generate seating arrangement

2. **View Results**
   - As admin: See all seating
   - As student: See your seat

3. **Try Features**
   - Download PDF report
   - View seat map
   - Check exam details

4. **Explore**
   - Create more users
   - Test with real data
   - Customize settings

---

## Documentation

For more details:
- 📖 [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md) - Full documentation
- ⚡ [AUTHENTICATION_QUICKSTART.md](AUTHENTICATION_QUICKSTART.md) - Detailed setup
- ✅ [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) - Complete checklist

---

## 🎯 Success Indicators

You'll know everything works when:

✅ Backend starts without errors  
✅ Frontend loads at localhost:8080  
✅ Login page displays with two tabs  
✅ Can create admin account  
✅ Can create student account  
✅ Admin sees dashboard  
✅ Student sees student dashboard  
✅ Logout button works  
✅ Can login again  

---

## 🆘 Need Help?

1. Check the documentation files
2. Look at browser console (F12)
3. Check backend terminal for error messages
4. Verify all required packages installed: `pip list | grep jose`
5. Verify ports 8000 and 8080 are available

---

## 🎉 You're All Set!

Everything is ready. Just:
1. Run the backend
2. Run the frontend
3. Open the browser
4. Create an account
5. Login and explore!

**Total setup time**: ~2 minutes  
**Complexity**: ⭐☆☆☆☆ (Very Simple)  
**Fun level**: ⭐⭐⭐⭐⭐ (Very Fun!)

Enjoy! 🚀
