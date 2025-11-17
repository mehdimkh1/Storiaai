const API_BASE_URL = 'https://storiaai-backend.onrender.com';

function getToken() {
    return localStorage.getItem('storia-token');
}

async function request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = getToken();

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers,
    };

    try {
        const response = await fetch(url, config);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        // Handle responses with no content
        if (response.status === 204) {
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error(`API request failed for endpoint: ${endpoint}`, error);
        throw error;
    }
}

// --- Authentication ---
export const login = (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    return request('/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
    });
};

export const register = (email, password) => {
    return request('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
    });
};

// --- Story Generation ---
export const generateStory = (storyRequest) => {
    return request('/generate_story', {
        method: 'POST',
        body: JSON.stringify(storyRequest),
    });
};

// --- Story Management ---
export const getMyStories = () => {
    return request('/stories/me');
};
