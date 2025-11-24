const API_BASE_URL = window.location.origin;

// ==========================================
// BASE DO CLIENTE
// ==========================================
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {},
        credentials: 'include'
    };

    if (data instanceof FormData) {
        options.body = data;
    } else if (data && method !== 'GET') {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const responseData = await response.json();
        if (!response.ok) throw new Error(responseData.error || 'Erro na requisição');
        return responseData;
    } catch (error) {
        console.error('Erro na API:', error);
        throw error;
    }
}

// ==========================================
// FUNÇÕES DA API (Garanta que getAlerts está aqui!)
// ==========================================

// Autenticação
async function register(name, email, password) { return await apiRequest('/api/register', 'POST', { name, email, password }); }
async function login(email, password) { return await apiRequest('/api/login', 'POST', { email, password }); }
async function logout() { return await apiRequest('/api/logout', 'POST'); }
async function updateUserProfile(data) { return await apiRequest('/api/user', 'PUT', data); }
async function uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);
    return await apiRequest('/api/upload', 'POST', formData);
}

// Pets
async function getPets() { return await apiRequest('/api/pets'); }
async function getPet(id) { return await apiRequest(`/api/pets/${id}`); }
async function createPet(name, species, breed, photoUrl) {
    return await apiRequest('/api/pets', 'POST', { name, species, breed, photo_url: photoUrl });
}
async function updatePet(id, data) { return await apiRequest(`/api/pets/${id}`, 'PUT', data); }
async function deletePet(id) { return await apiRequest(`/api/pets/${id}`, 'DELETE'); }

// Localização
async function getPetLocation(id) { return await apiRequest(`/api/pets/${id}/location`); }
async function getPetHistory(id) { return await apiRequest(`/api/pets/${id}/history`); }

// Cercas Virtuais
async function getGeofences(id) { return await apiRequest(`/api/pets/${id}/geofence`); }
async function createGeofence(id, name, lat, lng, rad) {
    return await apiRequest(`/api/pets/${id}/geofence`, 'POST', { name, center_lat: lat, center_lng: lng, radius_meters: rad });
}
async function deleteGeofence(zoneId) { return await apiRequest(`/api/geofence/${zoneId}`, 'DELETE'); }

// Alertas (AQUI ESTÁ O QUE FALTAVA)
async function getAlerts() { return await apiRequest('/api/alerts'); }
async function markAlertAsRead(id) { return await apiRequest(`/api/alerts/${id}/read`, 'POST'); }