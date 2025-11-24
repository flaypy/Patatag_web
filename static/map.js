// Variáveis globais para controle do mapa
let map = null;
let petMarker = null;
let historyLine = null;
let geofenceCircles = [];
let eventSource = null;

// ==========================================
// 1. INICIALIZAÇÃO
// ==========================================

window.initMap = function(containerId = 'map', centerLat = -23.550520, centerLng = -46.633308, zoom = 13) {
    if (!document.getElementById(containerId)) return;

    if (map !== null) {
        map.remove();
        map = null;
    }

    try {
        map = L.map(containerId).setView([centerLat, centerLng], zoom);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19,
        }).addTo(map);

        window.map = map; 
        console.log("Mapa inicializado!");
        return map;
    } catch (e) {
        console.error("Erro ao criar mapa:", e);
    }
};

// ==========================================
// 2. MARCADORES (ATUALIZADO COM FOTO)
// ==========================================

window.updatePetMarker = function(lat, lng, petName = 'Pet', status = 'online', photoUrl = null) {
    if (!map) return;

    const borderColor = status === 'online' ? '#10B981' : '#EF4444'; // Verde ou Vermelho

    // Define o conteúdo HTML do ícone
    let iconHtml;

    if (photoUrl && photoUrl !== '') {
        // Se tiver foto, usa a imagem
        iconHtml = `
            <div style="
                width: 48px; 
                height: 48px;
                border-radius: 50%;
                border: 4px solid ${borderColor};
                background-image: url('${photoUrl}');
                background-size: cover;
                background-position: center;
                box-shadow: 0 4px 10px rgba(0,0,0,0.4);
                transition: all 0.3s ease;
            "></div>
        `;
    } else {
        // Se não tiver foto, usa o emoji padrão
        iconHtml = `
            <div style="
                background-color: ${borderColor};
                width: 40px;
                height: 40px;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 20px;
            ">
                🐾
            </div>
        `;
    }

    // Criar ícone customizado
    const petIcon = L.divIcon({
        className: 'custom-pet-marker', // Classe CSS vazia para evitar estilos padrão do Leaflet atrapalhando
        html: iconHtml,
        iconSize: [48, 48],
        iconAnchor: [24, 24],
        popupAnchor: [0, -24]
    });

    // Remover marcador anterior
    if (petMarker) {
        map.removeLayer(petMarker);
    }

    // Adicionar novo marcador
    petMarker = L.marker([lat, lng], { icon: petIcon }).addTo(map);
    
    petMarker.bindPopup(`
        <div style="text-align: center;">
            <div style="margin-bottom: 5px; font-weight: bold; font-size: 14px;">${petName}</div>
            <span style="
                display: inline-block;
                padding: 2px 8px;
                border-radius: 12px;
                background-color: ${status === 'online' ? '#DCFCE7' : '#FEE2E2'};
                color: ${status === 'online' ? '#166534' : '#991B1B'};
                font-size: 11px;
                font-weight: 600;
            ">
                ${status === 'online' ? 'Conectado' : 'Offline'}
            </span>
        </div>
    `);

    map.setView([lat, lng], 15);
};

// ==========================================
// 3. LÓGICA DE CARREGAMENTO (ATUALIZADO)
// ==========================================

window.loadPetOnMap = async function(petId) {
    if (!petId) return;

    try {
        // 1. Busca dados do Pet (incluindo a URL da foto)
        const petData = await window.getPet(petId); 
        
        // 2. Busca localização
        try {
            const locData = await window.getPetLocation(petId);
            
            // 3. Atualiza marcador PASSANDO A FOTO
            window.updatePetMarker(
                locData.latitude, 
                locData.longitude, 
                petData.name, 
                petData.is_online ? 'online' : 'offline',
                petData.photo_url // <--- AQUI ESTÁ O SEGREDO
            );
            
            return petData; // Devolve os dados para o HTML usar na sidebar
        } catch (e) {
            console.log("Pet sem localização recente");
            return petData;
        }

    } catch (error) {
        console.error("Erro ao carregar pet:", error);
        throw error;
    }
};

// ==========================================
// 4. LIMPEZA E UTILITÁRIOS
// ==========================================

window.clearMap = function() {
    if (petMarker) {
        map.removeLayer(petMarker);
        petMarker = null;
    }
    if (historyLine) {
        map.removeLayer(historyLine);
        historyLine = null;
    }
    window.clearGeofences();
};

// Funções de Cerca Virtual (Mantidas iguais)
window.showAllGeofences = function(zones) {
    window.clearGeofences();
    if(!map) return;
    zones.forEach(zone => {
        const circle = L.circle([zone.center_lat, zone.center_lng], {
            color: '#3B82F6', fillColor: '#3B82F6', fillOpacity: 0.2, radius: zone.radius_meters
        }).addTo(map);
        circle.bindPopup(`<b>${zone.name}</b>`);
        geofenceCircles.push(circle);
    });
};

window.clearGeofences = function() {
    if(!map) return;
    geofenceCircles.forEach(c => map.removeLayer(c));
    geofenceCircles = [];
};

window.showLocationHistory = function(locations) {
    if (!map || !locations.length) return;
    if (historyLine) map.removeLayer(historyLine);
    const points = locations.map(l => [l.latitude, l.longitude]);
    historyLine = L.polyline(points, { color: '#F97316', weight: 4 }).addTo(map);
    map.fitBounds(historyLine.getBounds());
};