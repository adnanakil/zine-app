// Firebase Authentication Handler with v9+ SDK
let auth = null;
let analytics = null;
let currentUser = null;

// Initialize Firebase
function initializeFirebase(config) {
    if (!config || !config.apiKey) {
        console.warn('Firebase config not provided, running in development mode');
        return;
    }

    // Debug: Log configuration (sanitized) - Updated for clean env vars
    console.log('Initializing Firebase with config:', {
        ...config,
        apiKey: config.apiKey ? config.apiKey.substring(0, 10) + '...' : 'missing'
    });

    // Check for whitespace issues in config values
    Object.keys(config).forEach(key => {
        if (typeof config[key] === 'string' && config[key].includes('\n')) {
            console.warn(`Firebase config ${key} contains newlines:`, config[key]);
        }
    });

    // Load Firebase v9+ SDK modules dynamically
    const script = document.createElement('script');
    script.type = 'module';
    script.textContent = `
        import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
        import {
            getAuth,
            createUserWithEmailAndPassword,
            signInWithEmailAndPassword,
            signInWithPopup,
            GoogleAuthProvider,
            signOut as firebaseSignOut,
            onAuthStateChanged,
            updateProfile
        } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';
        import { getAnalytics, logEvent } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-analytics.js';

        try {
            // Initialize Firebase
            const app = initializeApp(${JSON.stringify(config)});
            const auth = getAuth(app);
            const analytics = ${config.measurementId ? `getAnalytics(app)` : 'null'};

            console.log('Firebase app initialized successfully');
        } catch (error) {
            console.error('Firebase initialization error:', error);
            window.firebaseInitError = error;
            return;
        }

        // Make auth functions available globally
        window.firebaseAuth = {
            auth,
            analytics,
            createUserWithEmailAndPassword,
            signInWithEmailAndPassword,
            signInWithPopup,
            GoogleAuthProvider,
            signOut: firebaseSignOut,
            onAuthStateChanged,
            updateProfile,
            logEvent: ${config.measurementId ? 'logEvent' : '() => {}'}
        };

        // Set up auth state observer
        onAuthStateChanged(auth, (user) => {
            window.currentFirebaseUser = user;
            if (user) {
                window.handleUserSignedIn(user);
            } else {
                window.handleUserSignedOut();
            }
        });
    `;
    document.head.appendChild(script);

    // Wait for Firebase to be initialized
    setTimeout(() => {
        if (window.firebaseAuth) {
            auth = window.firebaseAuth.auth;
            analytics = window.firebaseAuth.analytics;
            console.log('Firebase initialized successfully');
        }
    }, 1000);
}

// Sign up with email and password
async function signUpWithEmail(email, password, displayName) {
    try {
        if (!window.firebaseAuth) {
            throw new Error('Firebase not initialized');
        }

        const { auth, createUserWithEmailAndPassword, updateProfile, logEvent } = window.firebaseAuth;

        const userCredential = await createUserWithEmailAndPassword(auth, email, password);

        // Update display name
        if (displayName) {
            await updateProfile(userCredential.user, { displayName });
        }

        // Log analytics event
        logEvent(analytics, 'sign_up', { method: 'email' });

        // Get ID token
        const idToken = await userCredential.user.getIdToken();

        // Send to backend
        const response = await fetch('/auth/firebase-login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ idToken })
        });

        const data = await response.json();
        if (data.success) {
            window.location.href = '/';
        } else {
            throw new Error(data.error || 'Failed to create account');
        }
    } catch (error) {
        console.error('Sign up error:', error);
        showError(getErrorMessage(error));
    }
}

// Sign in with email and password
async function signInWithEmail(email, password) {
    try {
        if (!window.firebaseAuth) {
            throw new Error('Firebase not initialized');
        }

        const { auth, signInWithEmailAndPassword, logEvent } = window.firebaseAuth;

        const userCredential = await signInWithEmailAndPassword(auth, email, password);

        // Log analytics event
        logEvent(analytics, 'login', { method: 'email' });

        // Get ID token
        const idToken = await userCredential.user.getIdToken();

        // Send to backend
        const response = await fetch('/auth/firebase-login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ idToken })
        });

        const data = await response.json();
        if (data.success) {
            window.location.href = '/';
        } else {
            throw new Error(data.error || 'Failed to sign in');
        }
    } catch (error) {
        console.error('Sign in error:', error);
        showError(getErrorMessage(error));
    }
}

// Sign in with Google
async function signInWithGoogle() {
    try {
        if (!window.firebaseAuth) {
            throw new Error('Firebase not initialized');
        }

        const { auth, signInWithPopup, GoogleAuthProvider, logEvent } = window.firebaseAuth;

        const provider = new GoogleAuthProvider();
        const result = await signInWithPopup(auth, provider);

        // Log analytics event
        logEvent(analytics, 'login', { method: 'google' });

        // Get ID token
        const idToken = await result.user.getIdToken();

        // Send to backend
        const response = await fetch('/auth/firebase-login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ idToken })
        });

        const data = await response.json();
        if (data.success) {
            // Check if username needs to be set
            if (data.user && !data.user.username) {
                showUsernameModal(data.user);
            } else {
                window.location.href = '/';
            }
        } else {
            throw new Error(data.error || 'Failed to sign in');
        }
    } catch (error) {
        console.error('Google sign in error:', error);
        showError(getErrorMessage(error));
    }
}

// Sign out
async function signOut() {
    try {
        if (!window.firebaseAuth) {
            throw new Error('Firebase not initialized');
        }

        const { auth, signOut } = window.firebaseAuth;
        await signOut(auth);
        window.location.href = '/';
    } catch (error) {
        console.error('Sign out error:', error);
    }
}

// Handle user signed in
window.handleUserSignedIn = function(user) {
    console.log('User signed in:', user.email);

    // Update UI elements if needed
    const loginBtn = document.getElementById('loginBtn');
    const signupBtn = document.getElementById('signupBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    if (loginBtn) loginBtn.style.display = 'none';
    if (signupBtn) signupBtn.style.display = 'none';
    if (logoutBtn) logoutBtn.style.display = 'block';
}

// Handle user signed out
window.handleUserSignedOut = function() {
    console.log('User signed out');

    // Update UI elements if needed
    const loginBtn = document.getElementById('loginBtn');
    const signupBtn = document.getElementById('signupBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    if (loginBtn) loginBtn.style.display = 'block';
    if (signupBtn) signupBtn.style.display = 'block';
    if (logoutBtn) logoutBtn.style.display = 'none';
}

// Show username modal for new users
function showUsernameModal(user) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    `;

    modal.innerHTML = `
        <div class="modal-content" style="
            background: white;
            padding: 30px;
            border-radius: 8px;
            max-width: 400px;
            width: 90%;
        ">
            <h2>Choose Your Username</h2>
            <p>Welcome ${user.display_name || user.email}!</p>
            <input type="text" id="usernameInput" placeholder="Enter username"
                   pattern="[a-zA-Z0-9_]+" maxlength="20"
                   style="width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px;">
            <p id="usernameError" style="color: red; display: none; font-size: 14px;"></p>
            <button id="saveUsernameBtn" class="btn-primary" style="width: 100%; padding: 10px;">Save Username</button>
        </div>
    `;
    document.body.appendChild(modal);

    const input = document.getElementById('usernameInput');
    const errorEl = document.getElementById('usernameError');
    const saveBtn = document.getElementById('saveUsernameBtn');

    // Check username availability
    let checkTimeout;
    input.addEventListener('input', () => {
        clearTimeout(checkTimeout);
        checkTimeout = setTimeout(async () => {
            const username = input.value.trim();
            if (username.length < 3) {
                errorEl.textContent = 'Username must be at least 3 characters';
                errorEl.style.display = 'block';
                return;
            }

            const response = await fetch('/auth/check-username', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username })
            });

            const data = await response.json();
            if (!data.available) {
                errorEl.textContent = data.error || 'Username is taken';
                errorEl.style.display = 'block';
            } else {
                errorEl.style.display = 'none';
            }
        }, 500);
    });

    // Save username
    saveBtn.addEventListener('click', async () => {
        const username = input.value.trim();

        const response = await fetch('/auth/update-username', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });

        const data = await response.json();
        if (data.success) {
            window.location.href = '/';
        } else {
            errorEl.textContent = data.error;
            errorEl.style.display = 'block';
        }
    });
}

// Get user-friendly error messages
function getErrorMessage(error) {
    const errorCode = error.code;
    const errorMessages = {
        'auth/email-already-in-use': 'This email is already registered. Please sign in instead.',
        'auth/invalid-email': 'Please enter a valid email address.',
        'auth/weak-password': 'Password should be at least 6 characters.',
        'auth/user-not-found': 'No account found with this email.',
        'auth/wrong-password': 'Incorrect password. Please try again.',
        'auth/popup-closed-by-user': 'Sign-in cancelled.',
        'auth/network-request-failed': 'Network error. Please check your connection.',
        'auth/too-many-requests': 'Too many attempts. Please try again later.',
        'auth/user-disabled': 'This account has been disabled.'
    };

    return errorMessages[errorCode] || error.message || 'An error occurred. Please try again.';
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('authError');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    } else {
        alert(message);
    }
}

// Get current Firebase user
function getCurrentUser() {
    return window.currentFirebaseUser;
}

// Get ID token for API calls
async function getIdToken() {
    if (window.currentFirebaseUser) {
        return await window.currentFirebaseUser.getIdToken();
    }
    return null;
}