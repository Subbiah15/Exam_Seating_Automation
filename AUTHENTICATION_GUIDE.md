# Authentication System Documentation

## Overview
The Exam Seating Engine now includes a complete JWT-based authentication system with role-based access control (RBAC). The system supports three user roles:
- **Admin**: Full access to all features
- **Teacher**: Full access to all features (same as admin)
- **Student**: View-only access to their assigned seat

## Architecture

### Backend Components

#### 1. **auth.py** (Core Authentication Module)
Location: `c:\Users\HP\Desktop\Subbu\Working_Projects\Exam_Seating_Engine\auth.py`

Provides:
- Password hashing using bcrypt via passlib
- JWT token creation and validation
- Token models and request/response schemas

**Key Functions:**
- `hash_password(password)` - Hash passwords securely
- `verify_password(plain, hashed)` - Verify plain text against hash
- `create_access_token(data)` - Create JWT token with 24-hour expiry
- `decode_token(token)` - Decode and validate JWT token

**Configuration:**
- Algorithm: HS256 (HMAC with SHA-256)
- Expiry: 24 hours
- Secret Key: From environment variable `SECRET_KEY`

#### 2. **users_db.py** (User Database Module)
Location: `c:\Users\HP\Desktop\Subbu\Working_Projects\Exam_Seating_Engine\users_db.py`

Provides:
- JSON-based user storage (upgradeable to SQL)
- User CRUD operations
- Thread-safe operations with locks

**User Schema:**
```json
{
  "user_id": 1,
  "username": "teacher_name",
  "password_hash": "bcrypt_hash",
  "email": "teacher@example.com",
  "role": "admin|teacher|student",
  "name": "Teacher Full Name",
  "student_id": null,
  "created_at": "2024-01-15T10:30:00",
  "is_active": true
}
```

**Key Functions:**
- `create_user(...)` - Create new user account
- `get_user_by_username(username)` - Lookup by username
- `get_user_by_id(user_id)` - Lookup by user ID
- `get_user_by_student_id(student_id)` - Lookup by student ID
- `get_all_users()` - Get all users (admin only)
- `get_all_students()` - Get all students

#### 3. **Authentication Endpoints** (in main.py)
Location: `c:\Users\HP\Desktop\Subbu\Working_Projects\Exam_Seating_Engine\main.py`

**Endpoints:**
1. `POST /api/auth/signup` - Create new user account
2. `POST /api/auth/login` - Authenticate user and get JWT token
3. `GET /api/auth/me` - Get current user info from token
4. `POST /api/auth/logout` - Logout endpoint

### Frontend Components

#### 1. **login.html**
Location: `c:\Users\HP\Desktop\Subbu\Working_Projects\Exam_Seating_Engine\frontend\login.html`

Features:
- Two separate login tabs (Admin/Teacher vs Student)
- Responsive design with gradient background
- Real-time form validation
- Error/success messages

#### 2. **signup.html**
Location: `c:\Users\HP\Desktop\Subbu\Working_Projects\Exam_Seating_Engine\frontend\signup.html`

Features:
- Role-based signup (determined by URL parameter)
- Student ID field shown only for students
- Password confirmation
- Form validation

#### 3. **js/auth.js** (Frontend Auth Manager)
Location: `c:\Users\HP\Desktop\Subbu\Working_Projects\Exam_Seating_Engine\frontend\js\auth.js`

**AuthManager Class:**
```javascript
class AuthManager {
    isAuthenticated()      // Check if user is logged in
    getCurrentUser()       // Get current user info
    getAuthHeader()        // Get Authorization header
    login(username, password)  // Login user
    signup(...)            // Create new account
    getMe()               // Get current user from server
    logout()              // Clear token and redirect
    apiFetch()            // Make authenticated API calls
    isAdmin()             // Check if user is admin/teacher
    isStudent()           // Check if user is student
}
```

Helper functions:
- `requireAuth()` - Redirect to login if not authenticated
- `requireAdmin()` - Redirect if not admin/teacher
- `requireStudent()` - Redirect if not student

#### 4. **student-dashboard.html**
Location: `c:\Users\HP\Desktop\Subbu\Working_Projects\Exam_Seating_Engine\frontend\student-dashboard.html`

Features:
- Student-only dashboard
- Display student information
- Show assigned seating with exam details
- View seat map button for each assignment
- Logout functionality

#### 5. **Configuration Files**

**.env File:**
```
SECRET_KEY=exam-seating-engine-secret-key-12345-change-in-production
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:8080
BACKEND_URL=http://localhost:8000
```

**requirements.txt (Updated):**
```
python-jose[cryptography]==3.3.0  # JWT token handling
passlib[bcrypt]==1.7.4             # Password hashing
python-dotenv==1.0.0               # Environment variables
```

## User Flow

### Signup Flow
1. User visits `signup.html?role=admin|teacher|student`
2. Fills in registration form
3. Frontend validates inputs
4. Submits to `POST /api/auth/signup`
5. Backend:
   - Checks if username exists
   - Hashes password with bcrypt
   - Creates user in JSON database
   - Returns success message
6. Frontend redirects to login page

### Login Flow
1. User visits `login.html`
2. Selects appropriate tab (Admin/Teacher or Student)
3. Enters credentials
4. Submits to `POST /api/auth/login`
5. Backend:
   - Looks up user by username
   - Verifies password hash
   - Creates JWT token (24-hour expiry)
   - Returns token and user info
6. Frontend:
   - Stores token in `localStorage`
   - Stores user info (user_id, username, role)
   - Redirects to appropriate dashboard
7. Admin/Teacher → `index.html` (admin dashboard)
8. Student → `student-dashboard.html` (student dashboard)

### API Authentication
All protected endpoints require JWT token in `Authorization` header:
```
Authorization: Bearer <jwt_token>
```

The `auth.js` `apiFetch()` method automatically includes this header for all API calls.

### Token Validation
- `GET /api/auth/me` endpoint validates token
- If token is invalid or expired (401 response), user is logged out
- User is redirected to login page

## Database Storage

### users_store.json
```json
{
  "users": {
    "1": {
      "user_id": 1,
      "username": "admin",
      "password_hash": "bcrypt_hash_...",
      "email": "admin@example.com",
      "role": "admin",
      "name": "Administrator",
      "student_id": null,
      "created_at": "2024-01-15T10:00:00",
      "is_active": true
    },
    "2": {
      "user_id": 2,
      "username": "student001",
      "password_hash": "bcrypt_hash_...",
      "email": "student@example.com",
      "role": "student",
      "name": "John Doe",
      "student_id": "STU001",
      "created_at": "2024-01-15T10:30:00",
      "is_active": true
    }
  }
}
```

## Security Features

1. **Password Hashing**: Bcrypt with automatic salt generation
2. **JWT Tokens**: Signed with HS256 algorithm
3. **Token Expiry**: 24-hour expiration
4. **Environment Variables**: Secret key in `.env` file (not in code)
5. **CORS**: Configured for localhost development
6. **Headers**: Secure Authorization header usage

## Next Steps for Production

1. **Change SECRET_KEY**: Generate strong random key
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Use Database**: Replace JSON with proper SQL database (PostgreSQL, MySQL)

3. **HTTPS**: Enable SSL/TLS for all connections

4. **Email Verification**: Add email confirmation for signup

5. **Password Reset**: Implement password reset flow

6. **Rate Limiting**: Add login attempt limits

7. **Session Management**: Consider session-based auth alongside JWT

8. **Admin Panel**: Create admin interface for user management

9. **Audit Logging**: Log all authentication events

10. **2FA**: Consider two-factor authentication

## Testing

### Manual Testing
1. Start backend: `python main.py`
2. Start frontend: `python -m http.server 8080` (in frontend folder)
3. Navigate to `http://localhost:8080/frontend/login.html`
4. Try signup and login

### Test Accounts
Create test accounts using signup flow or directly in users_store.json

### API Testing
Use curl or Postman:
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Get current user
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <token>"
```

## Troubleshooting

### "Token expired" Error
- Check if 24 hours have passed since login
- Users must login again
- Token is cleared from localStorage

### "Invalid username or password"
- Verify username exists in users_store.json
- Check password hash matches user
- Ensure password is correct

### Login page not showing
- Check if running on correct port (8080)
- Verify file paths are correct
- Check browser console for JavaScript errors

### API 401 Unauthorized
- Verify Authorization header format: `Bearer <token>`
- Check token validity in `/api/auth/me`
- Ensure token not expired

## API Reference

### POST /api/auth/signup
**Request:**
```json
{
  "name": "John Doe",
  "username": "johndoe",
  "email": "john@example.com",
  "password": "secure_password",
  "role": "admin|teacher|student",
  "student_id": "STU001"  // Only for students
}
```

**Response:**
```json
{
  "success": true,
  "message": "User created successfully",
  "user_id": 1,
  "username": "johndoe",
  "role": "admin",
  "redirect": "/login.html"
}
```

### POST /api/auth/login
**Request:**
```json
{
  "username": "johndoe",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "role": "admin",
  "user_id": 1,
  "username": "johndoe"
}
```

### GET /api/auth/me
**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "user_id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "role": "admin",
  "name": "John Doe",
  "student_id": null,
  "created_at": "2024-01-15T10:00:00"
}
```

### POST /api/auth/logout
**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

## File Structure
```
Exam_Seating_Engine/
├── auth.py                    # Authentication utilities
├── users_db.py               # User database module
├── main.py                   # FastAPI application with auth endpoints
├── .env                      # Environment configuration
├── requirements.txt          # Python dependencies (updated)
├── frontend/
│   ├── index.html           # Admin dashboard
│   ├── login.html           # Login page
│   ├── signup.html          # Signup page
│   ├── student-dashboard.html # Student dashboard
│   ├── js/
│   │   ├── app.js           # Main application logic
│   │   └── auth.js          # Frontend authentication manager
│   └── css/
│       └── style.css        # Styles
└── users_store.json         # User database (auto-created)
```

## Summary
The authentication system provides:
- ✅ Secure JWT-based authentication
- ✅ Role-based access control (Admin, Teacher, Student)
- ✅ User registration and login
- ✅ Password hashing with bcrypt
- ✅ 24-hour token expiration
- ✅ Student dashboard for viewing assignments
- ✅ Admin dashboard for managing seating
- ✅ Responsive, modern UI
- ✅ Environment-based configuration

All components are integrated and ready for use!
