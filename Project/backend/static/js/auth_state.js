let accessToken = null;
let isRefreshing = false;
let refreshPromise = null;

async function refreshAccessToken() {
    if (isRefreshing) {
        return await refreshPromise;
    }
    isRefreshing = true;
    refreshPromise = fetch('/api/auth/refresh', { method: 'POST' })
        .then(async response => {
            if (!response.ok) throw new Error('Refresh failed');
            const data = await response.json();
            accessToken = data.access_token;
            return accessToken;
        })
        .catch(e => {
            accessToken = null;
            if (!['/login', '/register'].includes(window.location.pathname)) {
                window.location.href = '/login';
            }
            return null;
        })
        .finally(() => {
            isRefreshing = false;
        });
        
    return await refreshPromise;
}

async function authFetch(url, options = {}) {
    if (!accessToken) {
        const token = await refreshAccessToken();
        // Return a dummy rejected promise to bubble up correctly without executing further
        if (!token) return Promise.reject(new Error("Not authenticated")); 
    }
    
    options.headers = { ...options.headers, 'Authorization': `Bearer ${accessToken}` };
    let res = await fetch(url, options);
    
    if (res.status === 401) {
        const newToken = await refreshAccessToken();
        if (newToken) {
            options.headers['Authorization'] = `Bearer ${newToken}`;
            res = await fetch(url, options);
        }
    }
    
    return res;
}

async function handleLogout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    accessToken = null;
    window.location.href = '/login';
}

document.addEventListener("DOMContentLoaded", () => {
    // Inject Logout listener if there is a button
    const logoutBtn = document.getElementById('btnLogout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
});

if (!['/login', '/register'].includes(window.location.pathname)) {
    refreshAccessToken();
}
