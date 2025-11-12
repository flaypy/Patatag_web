/**
 * Patatag API Client
 * Funções para interagir com a API do backend
 */

const API_BASE_URL = window.location.origin;

// ==========================================
// UTILITÁRIOS
// ==========================================

async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include' // Para incluir cookies de sessão
    };

    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const responseData = await response.json();

        if (!response.ok) {
            throw new Error(responseData.error || 'Erro na requisição');
        }

        return responseData;
    } catch (error) {
        console.error('Erro na API:', error);
        throw error;
    }
}

// ==========================================
// AUTENTICAÇÃO
// ==========================================

async function register(name, email, password) {
    return await apiRequest('/api/register', 'POST', { name, email, password });
}

async function login(email, password) {
    return await apiRequest('/api/login', 'POST', { email, password });
}

async function logout() {
    return await apiRequest('/api/logout', 'POST');
}

// ==========================================
// PETS
// ==========================================

async function getPets() {
    return await apiRequest('/api/pets');
}

async function getPet(petId) {
    return await apiRequest(`/api/pets/${petId}`);
}

async function createPet(name, species, breed, photoUrl) {
    return await apiRequest('/api/pets', 'POST', {
        name,
        species,
        breed,
        photo_url: photoUrl
    });
}

async function updatePet(petId, data) {
    return await apiRequest(`/api/pets/${petId}`, 'PUT', data);
}

async function deletePet(petId) {
    return await apiRequest(`/api/pets/${petId}`, 'DELETE');
}

// ==========================================
// LOCALIZAÇÃO
// ==========================================

async function getPetLocation(petId) {
    return await apiRequest(`/api/pets/${petId}/location`);
}

async function getPetHistory(petId, page = 1, limit = 100, startDate = null, endDate = null) {
    let url = `/api/pets/${petId}/history?page=${page}&limit=${limit}`;

    if (startDate) {
        url += `&start_date=${startDate}`;
    }
    if (endDate) {
        url += `&end_date=${endDate}`;
    }

    return await apiRequest(url);
}

// ==========================================
// GEOFENCING
// ==========================================

async function getGeofences(petId) {
    return await apiRequest(`/api/pets/${petId}/geofence`);
}

async function createGeofence(petId, name, centerLat, centerLng, radiusMeters) {
    return await apiRequest(`/api/pets/${petId}/geofence`, 'POST', {
        name,
        center_lat: centerLat,
        center_lng: centerLng,
        radius_meters: radiusMeters
    });
}

async function deleteGeofence(zoneId) {
    return await apiRequest(`/api/geofence/${zoneId}`, 'DELETE');
}

// ==========================================
// ALERTAS
// ==========================================

async function getAlerts() {
    return await apiRequest('/api/alerts');
}

async function markAlertAsRead(alertId) {
    return await apiRequest(`/api/alerts/${alertId}/read`, 'POST');
}

// ==========================================
// TEMPO REAL (Server-Sent Events)
// ==========================================

function subscribeToLocationUpdates(petId, onUpdate) {
    const eventSource = new EventSource(`${API_BASE_URL}/api/pets/${petId}/stream`);

    eventSource.onmessage = (event) => {
        const location = JSON.parse(event.data);
        onUpdate(location);
    };

    eventSource.onerror = (error) => {
        console.error('Erro no SSE:', error);
        eventSource.close();
    };

    return eventSource;
}

// ==========================================
// UTILITÁRIOS DE UI
// ==========================================

function showNotification(message, type = 'info') {
    // Implementação simples - você pode melhorar isso
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'error' ? '#EF4444' : type === 'success' ? '#10B981' : '#3B82F6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
}

function formatDistance(meters) {
    if (meters < 1000) {
        return `${Math.round(meters)} m`;
    }
    return `${(meters / 1000).toFixed(2)} km`;
}

function getTimeSince(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return 'Agora mesmo';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} minutos atrás`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} horas atrás`;
    return `${Math.floor(seconds / 86400)} dias atrás`;
}

// Adicionar estilos para animações
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);
