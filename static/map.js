/**
 * Patatag Map Integration
 * Integração com Leaflet para exibir localização dos pets
 */

let map = null;
let petMarker = null;
let locationHistory = [];
let historyLine = null;
let geofenceCircles = [];
let eventSource = null;

// ==========================================
// INICIALIZAÇÃO DO MAPA
// ==========================================

function initMap(containerId = 'map', centerLat = -23.550520, centerLng = -46.633308, zoom = 13) {
    // Criar o mapa
    map = L.map(containerId).setView([centerLat, centerLng], zoom);

    // Adicionar camada de tiles (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
    }).addTo(map);

    return map;
}

// ==========================================
// MARCADORES E LOCALIZAÇÃO
// ==========================================

function updatePetMarker(lat, lng, petName = 'Pet', status = 'online') {
    const iconColor = status === 'online' ? 'green' : 'red';

    // Criar ícone customizado
    const petIcon = L.divIcon({
        className: 'custom-pet-marker',
        html: `
            <div style="
                background-color: ${iconColor === 'green' ? '#10B981' : '#EF4444'};
                width: 40px;
                height: 40px;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 18px;
            ">
                🐾
            </div>
        `,
        iconSize: [40, 40],
        iconAnchor: [20, 20],
        popupAnchor: [0, -20]
    });

    // Remover marcador anterior se existir
    if (petMarker) {
        map.removeLayer(petMarker);
    }

    // Criar novo marcador
    petMarker = L.marker([lat, lng], { icon: petIcon })
        .addTo(map)
        .bindPopup(`
            <div style="text-align: center;">
                <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: bold;">${petName}</h3>
                <p style="margin: 0; font-size: 12px; color: #666;">
                    Status: <span style="color: ${iconColor === 'green' ? '#10B981' : '#EF4444'}; font-weight: bold;">
                        ${status === 'online' ? 'Conectado' : 'Offline'}
                    </span>
                </p>
                <p style="margin: 4px 0 0 0; font-size: 11px; color: #999;">
                    Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}
                </p>
            </div>
        `);

    // Centralizar mapa no marcador com animação
    map.setView([lat, lng], map.getZoom(), { animate: true });

    return petMarker;
}

function animateMarkerToPosition(lat, lng, duration = 1000) {
    if (!petMarker) return;

    const startLatLng = petMarker.getLatLng();
    const endLatLng = L.latLng(lat, lng);

    const startTime = Date.now();

    function animate() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);

        const currentLat = startLatLng.lat + (endLatLng.lat - startLatLng.lat) * progress;
        const currentLng = startLatLng.lng + (endLatLng.lng - startLatLng.lng) * progress;

        petMarker.setLatLng([currentLat, currentLng]);

        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }

    animate();
}

// ==========================================
// HISTÓRICO DE LOCALIZAÇÃO
// ==========================================

function showLocationHistory(locations) {
    // Limpar histórico anterior
    if (historyLine) {
        map.removeLayer(historyLine);
    }

    if (!locations || locations.length === 0) {
        console.log('Nenhum histórico para exibir');
        return;
    }

    // Criar array de coordenadas
    const coordinates = locations.map(loc => [loc.latitude, loc.longitude]);

    // Criar linha do histórico
    historyLine = L.polyline(coordinates, {
        color: '#F97316',
        weight: 3,
        opacity: 0.7,
        smoothFactor: 1
    }).addTo(map);

    // Adicionar marcadores para pontos do histórico (a cada N pontos)
    const step = Math.max(1, Math.floor(locations.length / 10));
    locations.forEach((loc, index) => {
        if (index % step === 0 && index !== locations.length - 1) {
            L.circleMarker([loc.latitude, loc.longitude], {
                radius: 4,
                fillColor: '#F97316',
                color: 'white',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            })
            .addTo(map)
            .bindPopup(`
                <div style="font-size: 12px;">
                    <strong>${formatDate(loc.timestamp)}</strong><br>
                    Velocidade: ${loc.speed ? loc.speed.toFixed(1) + ' km/h' : 'N/A'}
                </div>
            `);
        }
    });

    // Ajustar zoom para mostrar todo o histórico
    map.fitBounds(historyLine.getBounds(), { padding: [50, 50] });

    locationHistory = locations;
}

function clearLocationHistory() {
    if (historyLine) {
        map.removeLayer(historyLine);
        historyLine = null;
    }
    locationHistory = [];
}

// ==========================================
// CERCAS VIRTUAIS (GEOFENCING)
// ==========================================

function showGeofence(centerLat, centerLng, radiusMeters, name, color = '#3B82F6') {
    const circle = L.circle([centerLat, centerLng], {
        radius: radiusMeters,
        color: color,
        fillColor: color,
        fillOpacity: 0.1,
        weight: 2
    }).addTo(map);

    circle.bindPopup(`
        <div style="text-align: center;">
            <h4 style="margin: 0 0 8px 0;">${name}</h4>
            <p style="margin: 0; font-size: 12px;">
                Raio: ${formatDistance(radiusMeters)}
            </p>
        </div>
    `);

    geofenceCircles.push(circle);
    return circle;
}

function showAllGeofences(zones) {
    clearGeofences();

    zones.forEach(zone => {
        if (zone.is_active) {
            showGeofence(
                zone.center_lat,
                zone.center_lng,
                zone.radius_meters,
                zone.name
            );
        }
    });
}

function clearGeofences() {
    geofenceCircles.forEach(circle => map.removeLayer(circle));
    geofenceCircles = [];
}

// ==========================================
// TEMPO REAL
// ==========================================

function startRealtimeTracking(petId, petName) {
    // Parar tracking anterior se existir
    stopRealtimeTracking();

    eventSource = subscribeToLocationUpdates(petId, (location) => {
        console.log('Nova localização recebida:', location);

        if (petMarker) {
            animateMarkerToPosition(location.latitude, location.longitude);
        } else {
            updatePetMarker(location.latitude, location.longitude, petName, 'online');
        }

        // Atualizar popup com informações
        if (petMarker) {
            petMarker.getPopup().setContent(`
                <div style="text-align: center;">
                    <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: bold;">${petName}</h3>
                    <p style="margin: 0; font-size: 12px; color: #666;">
                        Status: <span style="color: #10B981; font-weight: bold;">Conectado</span>
                    </p>
                    <p style="margin: 4px 0 0 0; font-size: 11px; color: #999;">
                        Última atualização: ${getTimeSince(location.timestamp)}
                    </p>
                    ${location.speed ? `<p style="margin: 4px 0 0 0; font-size: 11px;">Velocidade: ${location.speed.toFixed(1)} km/h</p>` : ''}
                    ${location.satellites ? `<p style="margin: 4px 0 0 0; font-size: 11px;">Satélites: ${location.satellites}</p>` : ''}
                </div>
            `);
        }

        showNotification(`${petName} - Nova localização recebida!`, 'success');
    });

    console.log('Tracking em tempo real iniciado para pet:', petId);
}

function stopRealtimeTracking() {
    if (eventSource) {
        eventSource.close();
        eventSource = null;
        console.log('Tracking em tempo real parado');
    }
}

// ==========================================
// CARREGAMENTO DE DADOS
// ==========================================

async function loadPetOnMap(petId, showHistory = false) {
    try {
        // Buscar dados do pet
        const petData = await getPet(petId);
        const pet = petData;

        console.log('Pet carregado:', pet);

        // Buscar localização atual
        try {
            const locationData = await getPetLocation(petId);
            updatePetMarker(
                locationData.latitude,
                locationData.longitude,
                pet.name,
                pet.is_online ? 'online' : 'offline'
            );
        } catch (error) {
            console.error('Erro ao buscar localização:', error);
            showNotification('Nenhuma localização disponível para este pet', 'error');
        }

        // Buscar e exibir histórico se solicitado
        if (showHistory) {
            try {
                const historyData = await getPetHistory(petId, 1, 100);
                if (historyData.locations && historyData.locations.length > 0) {
                    showLocationHistory(historyData.locations);
                }
            } catch (error) {
                console.error('Erro ao buscar histórico:', error);
            }
        }

        // Buscar e exibir cercas virtuais
        try {
            const geofenceData = await getGeofences(petId);
            if (geofenceData.zones && geofenceData.zones.length > 0) {
                showAllGeofences(geofenceData.zones);
            }
        } catch (error) {
            console.error('Erro ao buscar cercas:', error);
        }

        // Iniciar tracking em tempo real
        startRealtimeTracking(petId, pet.name);

        return pet;

    } catch (error) {
        console.error('Erro ao carregar pet no mapa:', error);
        showNotification('Erro ao carregar dados do pet', 'error');
        throw error;
    }
}

// ==========================================
// LIMPEZA
// ==========================================

function clearMap() {
    if (petMarker) {
        map.removeLayer(petMarker);
        petMarker = null;
    }
    clearLocationHistory();
    clearGeofences();
    stopRealtimeTracking();
}

// ==========================================
// EXPORTAR FUNÇÕES GLOBAIS
// ==========================================

window.MapHelpers = {
    initMap,
    updatePetMarker,
    animateMarkerToPosition,
    showLocationHistory,
    clearLocationHistory,
    showGeofence,
    showAllGeofences,
    clearGeofences,
    startRealtimeTracking,
    stopRealtimeTracking,
    loadPetOnMap,
    clearMap
};
