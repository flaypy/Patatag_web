from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import secrets
import json
import time
from math import radians, cos, sin, asin, sqrt

from models import db, User, Pet, Location, GeofenceZone, Alert
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensões
db.init_app(app)
CORS(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcula distância entre duas coordenadas em metros"""
    R = 6371000  # Raio da Terra em metros
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c


def check_geofence_violations(pet_id, latitude, longitude):
    """Verifica se o pet saiu de alguma cerca virtual"""
    zones = GeofenceZone.query.filter_by(pet_id=pet_id, is_active=True).all()

    for zone in zones:
        distance = haversine_distance(
            zone.center_lat, zone.center_lng,
            latitude, longitude
        )

        if distance > zone.radius_meters:
            # Pet saiu da cerca
            alert = Alert(
                pet_id=pet_id,
                alert_type='geofence',
                message=f'Seu pet saiu da zona "{zone.name}"!'
            )
            db.session.add(alert)

    db.session.commit()


def check_battery_alert(pet_id, battery_level):
    """Cria alerta se a bateria estiver baixa"""
    if battery_level <= 20:
        # Verifica se já existe alerta de bateria não lido
        existing = Alert.query.filter_by(
            pet_id=pet_id,
            alert_type='battery',
            is_read=False
        ).first()

        if not existing:
            alert = Alert(
                pet_id=pet_id,
                alert_type='battery',
                message=f'Bateria baixa: {battery_level}%'
            )
            db.session.add(alert)
            db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ============================================
# ROTAS DE AUTENTICAÇÃO
# ============================================

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return render_template('login_web.html')


@app.route('/cadastro')
def cadastro():
    return render_template('cadastro_web.html')


@app.route('/api/register', methods=['POST'])
def api_register():
    """Registrar novo usuário"""
    data = request.json

    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Nome, email e senha são obrigatórios'}), 400

    # Verificar se o email já existe
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email já cadastrado'}), 400

    user = User(
        name=data['name'],
        email=data['email']
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    login_user(user, remember=True)

    return jsonify({
        'message': 'Usuário cadastrado com sucesso',
        'user': user.to_dict()
    }), 201


@app.route('/api/login', methods=['POST'])
def api_login():
    """Fazer login"""
    data = request.json

    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Email ou senha incorretos'}), 401

    login_user(user, remember=True)

    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict()
    }), 200


@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    """Fazer logout"""
    logout_user()
    return jsonify({'message': 'Logout realizado com sucesso'}), 200


# ============================================
# ROTAS DO DASHBOARD
# ============================================

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('home_pets_web.html')


@app.route('/mapa')
@app.route('/mapa/<int:pet_id>')
@login_required
def mapa(pet_id=None):
    return render_template('mapa_web.html')


@app.route('/adicionar-pet')
@login_required
def adicionar_pet():
    return render_template('adicionar_pet_web.html')


@app.route('/perfil')
@login_required
def perfil():
    return render_template('perfil_web.html')


# ============================================
# API - PETS
# ============================================

@app.route('/api/pets', methods=['GET'])
@login_required
def get_pets():
    """Listar todos os pets do usuário"""
    pets = Pet.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'pets': [pet.to_dict(include_last_location=True) for pet in pets]
    }), 200


@app.route('/api/pets/<int:pet_id>', methods=['GET'])
@login_required
def get_pet(pet_id):
    """Obter detalhes de um pet específico"""
    pet = Pet.query.filter_by(id=pet_id, user_id=current_user.id).first()

    if not pet:
        return jsonify({'error': 'Pet não encontrado'}), 404

    return jsonify(pet.to_dict(include_last_location=True)), 200


@app.route('/api/pets', methods=['POST'])
@login_required
def create_pet():
    """Criar novo pet"""
    data = request.json

    if not data.get('name'):
        return jsonify({'error': 'Nome do pet é obrigatório'}), 400

    # Gerar device_id e api_key únicos
    device_id = f"ESP32_{secrets.token_hex(6).upper()}"
    api_key = secrets.token_urlsafe(32)

    pet = Pet(
        name=data['name'],
        species=data.get('species', 'Cachorro'),
        breed=data.get('breed', ''),
        photo_url=data.get('photo_url', ''),
        device_id=device_id,
        api_key=api_key,
        user_id=current_user.id
    )

    db.session.add(pet)
    db.session.commit()

    return jsonify({
        'message': 'Pet criado com sucesso',
        'pet': pet.to_dict(),
        'api_key': api_key,  # Mostrar apenas na criação
        'device_id': device_id
    }), 201


@app.route('/api/pets/<int:pet_id>', methods=['PUT'])
@login_required
def update_pet(pet_id):
    """Atualizar dados do pet"""
    pet = Pet.query.filter_by(id=pet_id, user_id=current_user.id).first()

    if not pet:
        return jsonify({'error': 'Pet não encontrado'}), 404

    data = request.json

    if 'name' in data:
        pet.name = data['name']
    if 'species' in data:
        pet.species = data['species']
    if 'breed' in data:
        pet.breed = data['breed']
    if 'photo_url' in data:
        pet.photo_url = data['photo_url']

    db.session.commit()

    return jsonify({
        'message': 'Pet atualizado com sucesso',
        'pet': pet.to_dict()
    }), 200


@app.route('/api/pets/<int:pet_id>', methods=['DELETE'])
@login_required
def delete_pet(pet_id):
    """Deletar pet"""
    pet = Pet.query.filter_by(id=pet_id, user_id=current_user.id).first()

    if not pet:
        return jsonify({'error': 'Pet não encontrado'}), 404

    db.session.delete(pet)
    db.session.commit()

    return jsonify({'message': 'Pet deletado com sucesso'}), 200


# ============================================
# API - LOCALIZAÇÃO (ESP32)
# ============================================

@app.route('/api/gps/update', methods=['POST'])
def update_gps():
    """
    Endpoint para o ESP32 enviar dados de localização
    Formato esperado:
    {
        "api_key": "chave_do_dispositivo",
        "latitude": -23.550520,
        "longitude": -46.633308,
        "altitude": 760.0,
        "speed": 0.0,
        "satellites": 8,
        "hdop": 1.2,
        "battery": 85
    }
    """
    data = request.json

    # Validar API key
    api_key = data.get('api_key')
    if not api_key:
        return jsonify({'error': 'API key não fornecida'}), 401

    pet = Pet.query.filter_by(api_key=api_key).first()
    if not pet:
        return jsonify({'error': 'API key inválida'}), 401

    # Validar dados obrigatórios
    if 'latitude' not in data or 'longitude' not in data:
        return jsonify({'error': 'Latitude e longitude são obrigatórios'}), 400

    try:
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Coordenadas inválidas'}), 400

    # Criar registro de localização
    location = Location(
        pet_id=pet.id,
        latitude=latitude,
        longitude=longitude,
        altitude=data.get('altitude'),
        speed=data.get('speed'),
        satellites=data.get('satellites'),
        hdop=data.get('hdop')
    )

    # Atualizar status do pet
    pet.is_online = True
    pet.last_seen = datetime.utcnow()

    if 'battery' in data:
        pet.battery_level = int(data['battery'])
        check_battery_alert(pet.id, pet.battery_level)

    db.session.add(location)
    db.session.commit()

    # Verificar cercas virtuais
    check_geofence_violations(pet.id, latitude, longitude)

    return jsonify({
        'message': 'Localização atualizada com sucesso',
        'location_id': location.id
    }), 200


# ============================================
# API - CONSULTA DE LOCALIZAÇÃO
# ============================================

@app.route('/api/pets/<int:pet_id>/location', methods=['GET'])
@login_required
def get_pet_location(pet_id):
    """Obter última localização do pet"""
    pet = Pet.query.filter_by(id=pet_id, user_id=current_user.id).first()

    if not pet:
        return jsonify({'error': 'Pet não encontrado'}), 404

    location = Location.query.filter_by(pet_id=pet_id).order_by(Location.timestamp.desc()).first()

    if not location:
        return jsonify({'error': 'Nenhuma localização registrada'}), 404

    return jsonify(location.to_dict()), 200


@app.route('/api/pets/<int:pet_id>/history', methods=['GET'])
@login_required
def get_pet_history(pet_id):
    """Obter histórico de localizações do pet"""
    pet = Pet.query.filter_by(id=pet_id, user_id=current_user.id).first()

    if not pet:
        return jsonify({'error': 'Pet não encontrado'}), 404

    # Parâmetros de paginação e filtros
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 100, type=int)
    start_date = request.args.get('start_date')  # ISO format
    end_date = request.args.get('end_date')

    query = Location.query.filter_by(pet_id=pet_id)

    # Filtros de data
    if start_date:
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Location.timestamp >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Location.timestamp <= end)
        except ValueError:
            pass

    # Ordenar e paginar
    locations = query.order_by(Location.timestamp.desc()).paginate(
        page=page, per_page=limit, error_out=False
    )

    return jsonify({
        'locations': [loc.to_dict() for loc in locations.items],
        'total': locations.total,
        'pages': locations.pages,
        'current_page': locations.page
    }), 200


# ============================================
# API - GEOFENCING (CERCAS VIRTUAIS)
# ============================================

@app.route('/api/pets/<int:pet_id>/geofence', methods=['GET'])
@login_required
def get_geofences(pet_id):
    """Listar cercas virtuais do pet"""
    pet = Pet.query.filter_by(id=pet_id, user_id=current_user.id).first()

    if not pet:
        return jsonify({'error': 'Pet não encontrado'}), 404

    zones = GeofenceZone.query.filter_by(pet_id=pet_id).all()
    return jsonify({
        'zones': [zone.to_dict() for zone in zones]
    }), 200


@app.route('/api/pets/<int:pet_id>/geofence', methods=['POST'])
@login_required
def create_geofence(pet_id):
    """Criar cerca virtual para o pet"""
    pet = Pet.query.filter_by(id=pet_id, user_id=current_user.id).first()

    if not pet:
        return jsonify({'error': 'Pet não encontrado'}), 404

    data = request.json

    if not all(k in data for k in ['name', 'center_lat', 'center_lng', 'radius_meters']):
        return jsonify({'error': 'Dados incompletos'}), 400

    zone = GeofenceZone(
        pet_id=pet_id,
        name=data['name'],
        center_lat=float(data['center_lat']),
        center_lng=float(data['center_lng']),
        radius_meters=float(data['radius_meters'])
    )

    db.session.add(zone)
    db.session.commit()

    return jsonify({
        'message': 'Cerca virtual criada com sucesso',
        'zone': zone.to_dict()
    }), 201


@app.route('/api/geofence/<int:zone_id>', methods=['DELETE'])
@login_required
def delete_geofence(zone_id):
    """Deletar cerca virtual"""
    zone = GeofenceZone.query.join(Pet).filter(
        GeofenceZone.id == zone_id,
        Pet.user_id == current_user.id
    ).first()

    if not zone:
        return jsonify({'error': 'Cerca não encontrada'}), 404

    db.session.delete(zone)
    db.session.commit()

    return jsonify({'message': 'Cerca deletada com sucesso'}), 200


# ============================================
# API - ALERTAS
# ============================================

@app.route('/api/alerts', methods=['GET'])
@login_required
def get_alerts():
    """Listar alertas do usuário"""
    alerts = Alert.query.join(Pet).filter(Pet.user_id == current_user.id).order_by(
        Alert.created_at.desc()
    ).limit(50).all()

    return jsonify({
        'alerts': [alert.to_dict() for alert in alerts]
    }), 200


@app.route('/api/alerts/<int:alert_id>/read', methods=['POST'])
@login_required
def mark_alert_read(alert_id):
    """Marcar alerta como lido"""
    alert = Alert.query.join(Pet).filter(
        Alert.id == alert_id,
        Pet.user_id == current_user.id
    ).first()

    if not alert:
        return jsonify({'error': 'Alerta não encontrado'}), 404

    alert.is_read = True
    db.session.commit()

    return jsonify({'message': 'Alerta marcado como lido'}), 200


# ============================================
# SERVER-SENT EVENTS (TEMPO REAL)
# ============================================

@app.route('/api/pets/<int:pet_id>/stream')
@login_required
def stream_pet_location(pet_id):
    """Stream de localização em tempo real usando SSE"""
    pet = Pet.query.filter_by(id=pet_id, user_id=current_user.id).first()

    if not pet:
        return jsonify({'error': 'Pet não encontrado'}), 404

    def generate():
        last_location_id = 0
        while True:
            # Buscar nova localização
            location = Location.query.filter(
                Location.pet_id == pet_id,
                Location.id > last_location_id
            ).order_by(Location.timestamp.desc()).first()

            if location:
                last_location_id = location.id
                data = json.dumps(location.to_dict())
                yield f"data: {data}\n\n"

            time.sleep(2)  # Verificar a cada 2 segundos

    return Response(generate(), mimetype='text/event-source')


# ============================================
# INICIALIZAÇÃO
# ============================================

@app.cli.command()
def init_db():
    """Criar as tabelas do banco de dados"""
    with app.app_context():
        db.create_all()
        print('Banco de dados criado!')


@app.cli.command()
def create_test_user():
    """Criar usuário de teste"""
    with app.app_context():
        user = User(name='Teste', email='teste@teste.com')
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()
        print(f'Usuário de teste criado! Email: teste@teste.com, Senha: 123456')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
