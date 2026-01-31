# ✅ Signup/Login Testing Guide

## Quick Test (2 minutes)

### Prerequisites
- Backend running: `python main.py` on port 8000
- Frontend running: `python -m http.server 8080 --directory frontend` 

### Test 1: Admin Signup ✅

1. **Go to**: `http://localhost:8080/signup.html?role=admin`

2. **Fill form**:
   ```
   Full Name:       Admin User 1
   Username:        admin_user_1
   Email:           admin@test.com
   Password:        Admin@123
   Confirm:         Admin@123
   ```

3. **Click**: "Create Account"

4. **Expected Result**:
   - ✅ Success message appears
   - ✅ Redirects to login page
   - ✅ Takes ~1-2 seconds

### Test 2: Admin Login ✅

1. **Go to**: `http://localhost:8080/login.html`

2. **Select**: Admin/Teacher tab (should be selected)

3. **Enter**:
   ```
   Username: admin_user_1
   Password: Admin@123
   ```

4. **Click**: "Login"

5. **Expected Result**:
   - ✅ Success message: "✅ Login successful! Redirecting..."
   - ✅ Redirects to `index.html`
   - ✅ Can see admin dashboard
   - ✅ Username shown in navbar

### Test 3: Student Signup ✅

1. **Go to**: `http://localhost:8080/signup.html?role=student`

2. **Fill form**:
   ```
   Full Name:       Student User 1
   Username:        student_user_1
   Email:           student@test.com
   Password:        Student@123
   Confirm:         Student@123
   Student ID:      STU001
   ```

3. **Click**: "Create Account"

4. **Expected Result**:
   - ✅ Student ID field is visible
   - ✅ Success message appears
   - ✅ Redirects to login page

### Test 4: Student Login ✅

1. **Go to**: `http://localhost:8080/login.html`

2. **Select**: "Student" tab

3. **Enter**:
   ```
   Username: student_user_1
   Password: Student@123
   ```

4. **Click**: "Login"

5. **Expected Result**:
   - ✅ Success message appears
   - ✅ Redirects to `student-dashboard.html`
   - ✅ Can see student dashboard
   - ✅ Shows "Welcome, student_user_1!"

---

## Error Testing

### Test Error: Invalid Email

1. **Go to**: Signup page
2. **Fill**:
   ```
   Email: notanemail
   ```
3. **Click**: "Create Account"
4. **Expected**: 
   - ❌ Error: "Valid email address is required"
   - No server call made

### Test Error: Short Password

1. **Go to**: Signup page
2. **Fill**:
   ```
   Password: Test
   Confirm:  Test
   ```
3. **Click**: "Create Account"
4. **Expected**: 
   - ❌ Error: "Password must be at least 6 characters"

### Test Error: Mismatched Passwords

1. **Go to**: Signup page
2. **Fill**:
   ```
   Password: Test@1234
   Confirm:  Test@5678
   ```
3. **Click**: "Create Account"
4. **Expected**: 
   - ❌ Error: "Passwords do not match"

### Test Error: Duplicate Username

1. **Try** to create account with existing username
2. **Expected**:
   - ❌ Error: "Username 'admin_user_1' already exists"
   - Loading stops
   - Can try different username

### Test Error: Student ID Required (for student signup)

1. **Go to**: `http://localhost:8080/signup.html?role=student`
2. **Fill all** but leave Student ID empty
3. **Click**: "Create Account"
4. **Expected**: 
   - ❌ Error: "Student ID is required"

### Test Error: Wrong Password on Login

1. **Go to**: Login page
2. **Enter**:
   ```
   Username: admin_user_1
   Password: WrongPassword
   ```
3. **Click**: "Login"
4. **Expected**: 
   - ❌ Error: "Invalid username or password"
   - Not redirected

---

## Console Testing (F12)

### To View Console Logs:

1. **Press**: F12
2. **Click**: "Console" tab
3. **Perform** signup/login

### What You'll See:

**For Signup Success:**
```
Submitting signup form for role: admin
Payload: {name: "Admin User 1", username: "admin_user_1", ...}
Response status: 200
Response data: {success: true, message: "User 'admin_user_1' created..."}
```

**For Login Success:**
```
Admin login attempt for: admin_user_1
Login response status: 200
Login response: {access_token: "eyJ...", token_type: "Bearer", ...}
```

**For Error:**
```
Signup error: Error: Username 'admin_user_1' already exists
```

---

## Database Testing

### View Created Users:

**PowerShell:**
```powershell
Get-Content users_store.json
```

**Should show:**
```json
{
  "users": {
    "1": {
      "user_id": 1,
      "username": "admin_user_1",
      "password_hash": "bcrypt_hash_...",
      "email": "admin@test.com",
      "role": "admin",
      "name": "Admin User 1",
      "student_id": null,
      "created_at": "2026-01-31T...",
      "is_active": true
    }
  }
}
```

---

## Performance Testing

### Measure Response Times:

**Open F12 Console and monitor Network tab:**
1. Press `F12`
2. Click "Network" tab
3. Perform signup
4. Look for `api/auth/signup` request
5. Check:
   - **Status**: 200 (success) or 400 (error)
   - **Time**: Should be <1 second
   - **Size**: Usually <1 KB

---

## Integration Testing

### Test Full Flow:

1. **Create** 2 admin accounts
   - `admin_test_1`
   - `admin_test_2`

2. **Create** 2 student accounts
   - `student_test_1` (STU001)
   - `student_test_2` (STU002)

3. **Login** as admin_test_1
   - Should see dashboard
   - Logout

4. **Login** as student_test_1
   - Should see student dashboard
   - Logout

5. **Login** as admin_test_2
   - Should see dashboard again
   - Logout

6. **Login** as student_test_2
   - Should see student dashboard
   - Logout

✅ **If all redirects work**: Integration is complete!

---

## Regression Testing

### Old Functionality:

1. **Admin Dashboard** still loads
2. **Can upload CSV** (if implemented)
3. **Can create halls** (if implemented)
4. **Can generate seating** (if implemented)
5. **Can view results** (if implemented)

---

## Summary

**All the following should work:**

✅ Sign up as admin  
✅ Sign up as student (with Student ID)  
✅ Login as admin → sees admin dashboard  
✅ Login as student → sees student dashboard  
✅ Error messages display correctly  
✅ Console logs show request/response  
✅ Users saved in database  
✅ Logout works  
✅ Can't use duplicate username  
✅ Password validation works  

**If any test fails**, check:
1. Backend is running
2. Frontend is on port 8080
3. Check F12 console for error messages
4. Look at backend terminal for errors

---

## Timestamps Checklist

After each successful signup, user should have `created_at` timestamp.

Example: `"created_at": "2026-01-31T14:30:45.123456"`

If missing, check backend `users_db.py` for timestamp generation.

---

## Success! ✅

When all tests pass, you have:
- ✅ Working signup (admin + student)
- ✅ Working login (both roles)
- ✅ Proper redirects
- ✅ Database persistence
- ✅ Error handling
- ✅ Console logging
- ✅ Full authentication system

**You're ready to use the system!** 🚀
