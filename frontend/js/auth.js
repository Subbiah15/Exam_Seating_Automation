/**
 * Authentication Module - Frontend JWT Token Management
 * Handles token storage, retrieval, and API communication
 */

class AuthManager {
    constructor() {
        this.token = localStorage.getItem('token');
        this.userId = localStorage.getItem('user_id');
        this.username = localStorage.getItem('username');
        this.role = localStorage.getItem('role');
    }
    
    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.token;
    }
    
    /**
     * Get current user info
     */
    getCurrentUser() {
        return {
            user_id: this.userId,
            username: this.username,
            role: this.role,
            isAuthenticated: this.isAuthenticated()
        };
    }
    
    /**
     * Get authorization header for API calls
     */
    getAuthHeader() {
        return this.token ? `Bearer ${this.token}` : null;
    }
    
    /**
     * Login user
     */
    async login(username, password) {
        try {
            const response = await fetch('http://127.0.0.1:8081/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }
            
            const data = await response.json();
            
            // Store token and user info
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('username', data.username);
            localStorage.setItem('role', data.role);
            
            // Update instance variables
            this.token = data.access_token;
            this.userId = data.user_id;
            this.username = data.username;
            this.role = data.role;
            
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }
    
    /**
     * Signup user
     */
    async signup(name, username, email, password, role, studentId = null) {
        try {
            const response = await fetch('http://127.0.0.1:8081/api/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name,
                    username,
                    email,
                    password,
                    role,
                    student_id: studentId
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Signup failed');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Signup error:', error);
            throw error;
        }
    }
    
    /**
     * Get current user from server
     */
    async getMe() {
        try {
            const authHeader = this.getAuthHeader();
            if (!authHeader) {
                throw new Error('Not authenticated');
            }
            
            const response = await fetch('http://127.0.0.1:8081/api/auth/me', {
                method: 'GET',
                headers: {
                    'Authorization': authHeader
                }
            });
            
            if (!response.ok) {
                if (response.status === 401) {
                    this.logout();
                    throw new Error('Token expired. Please login again.');
                }
                const error = await response.json();
                throw new Error(error.detail || 'Failed to get user info');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Get me error:', error);
            throw error;
        }
    }
    
    /**
     * Logout user
     */
    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('username');
        localStorage.removeItem('role');
        
        this.token = null;
        this.userId = null;
        this.username = null;
        this.role = null;
        
        // Redirect to login page
        window.location.href = 'login.html';
    }
    
    /**
     * Make authenticated API call
     */
    async apiFetch(url, options = {}) {
        const authHeader = this.getAuthHeader();
        
        const headers = {
            ...options.headers,
            'Content-Type': 'application/json'
        };
        
        if (authHeader) {
            headers['Authorization'] = authHeader;
        }
        
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        // Handle 401 - token expired
        if (response.status === 401) {
            this.logout();
            throw new Error('Session expired. Please login again.');
        }
        
        return response;
    }
    
    /**
     * Check if user is admin or teacher
     */
    isAdmin() {
        return this.role === 'admin' || this.role === 'teacher';
    }
    
    /**
     * Check if user is student
     */
    isStudent() {
        return this.role === 'student';
    }
}

// Create global instance
const auth = new AuthManager();

/**
 * Helper function to require authentication
 * Redirects to login if not authenticated
 */
function requireAuth() {
    if (!auth.isAuthenticated()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

/**
 * Helper function to require admin role
 * Redirects to dashboard if not admin
 */
function requireAdmin() {
    if (!auth.isAdmin()) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

/**
 * Helper function to require student role
 */
function requireStudent() {
    if (!auth.isStudent()) {
        window.location.href = 'student-dashboard.html';
        return false;
    }
    return true;
}

// Auto-logout on page unload if needed
window.addEventListener('beforeunload', () => {
    // Token persists in localStorage, no action needed
});
