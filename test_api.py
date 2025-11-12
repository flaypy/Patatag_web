"""
Script de teste para a API do Patatag
Execute este script para testar a API sem precisar do ESP32
"""

import requests
import time
import random
import json

# Configuracoes
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "teste@teste.com"
TEST_PASSWORD = "123456"

# Sessao para manter cookies
session = requests.Session()


def print_response(response, title="Response"):
    """Imprime resposta formatada"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*50}\n")


def test_register():
    """Testar registro de usuario"""
    print("[1] Testando registro de usuario...")

    data = {
        "name": "Usuario Teste",
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }

    response = session.post(f"{BASE_URL}/api/register", json=data)
    print_response(response, "Registro")
    return response.status_code in [200, 201]


def test_login():
    """Testar login"""
    print("[2] Testando login...")

    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }

    response = session.post(f"{BASE_URL}/api/login", json=data)
    print_response(response, "Login")
    return response.status_code == 200


def test_create_pet():
    """Criar pet de teste"""
    print("[3] Criando pet de teste...")

    data = {
        "name": "Rex",
        "species": "Cachorro",
        "breed": "Labrador",
        "photo_url": "https://placedog.net/200/200"
    }

    response = session.post(f"{BASE_URL}/api/pets", json=data)
    print_response(response, "Criar Pet")

    if response.status_code in [200, 201]:
        pet_data = response.json()
        api_key = pet_data.get('api_key')
        pet_id = pet_data.get('pet', {}).get('id')
        print(f"[OK] Pet criado com sucesso!")
        print(f"Pet ID: {pet_id}")
        print(f"API Key: {api_key}")
        return pet_id, api_key

    return None, None


def test_send_gps_data(api_key, num_points=5):
    """Enviar dados GPS de teste"""
    print(f"[4] Enviando {num_points} pontos GPS...")

    # Coordenadas base (Sao Paulo)
    base_lat = -23.550520
    base_lng = -46.633308

    for i in range(num_points):
        # Simular movimento aleatorio (raio de ~500m)
        lat = base_lat + random.uniform(-0.005, 0.005)
        lng = base_lng + random.uniform(-0.005, 0.005)

        data = {
            "api_key": api_key,
            "latitude": lat,
            "longitude": lng,
            "altitude": 760 + random.uniform(-10, 10),
            "speed": random.uniform(0, 5),
            "satellites": random.randint(6, 12),
            "hdop": random.uniform(0.8, 2.0),
            "battery": 100 - (i * 5)  # Simular descarga de bateria
        }

        response = session.post(f"{BASE_URL}/api/gps/update", json=data)

        if response.status_code == 200:
            print(f"  [OK] Ponto {i+1}/{num_points} enviado: ({lat:.6f}, {lng:.6f})")
        else:
            print(f"  [ERRO] Erro no ponto {i+1}: {response.status_code}")

        time.sleep(1)  # Aguardar 1 segundo entre envios

    print(f"[OK] {num_points} pontos GPS enviados com sucesso!")


def test_get_location(pet_id):
    """Obter ultima localizacao"""
    print("[5] Obtendo ultima localizacao...")

    response = session.get(f"{BASE_URL}/api/pets/{pet_id}/location")
    print_response(response, "Ultima Localizacao")
    return response.status_code == 200


def test_get_history(pet_id):
    """Obter historico"""
    print("[6] Obtendo historico...")

    response = session.get(f"{BASE_URL}/api/pets/{pet_id}/history?limit=10")
    print_response(response, "Historico")
    return response.status_code == 200


def test_create_geofence(pet_id):
    """Criar cerca virtual"""
    print("[7] Criando cerca virtual...")

    data = {
        "name": "Casa",
        "center_lat": -23.550520,
        "center_lng": -46.633308,
        "radius_meters": 100
    }

    response = session.post(f"{BASE_URL}/api/pets/{pet_id}/geofence", json=data)
    print_response(response, "Criar Cerca Virtual")
    return response.status_code in [200, 201]


def test_get_pets():
    """Listar todos os pets"""
    print("[8] Listando todos os pets...")

    response = session.get(f"{BASE_URL}/api/pets")
    print_response(response, "Listar Pets")
    return response.status_code == 200


def run_all_tests():
    """Executar todos os testes"""
    print("\n" + "="*60)
    print("INICIANDO TESTES DA API PATATAG")
    print("="*60)

    try:
        # Teste 1: Registro (pode falhar se usuario ja existe)
        test_register()

        # Teste 2: Login
        if not test_login():
            print("[ERRO] Falha no login. Abortando testes.")
            return

        # Teste 3: Criar pet
        pet_id, api_key = test_create_pet()
        if not pet_id or not api_key:
            print("[ERRO] Falha ao criar pet. Abortando testes.")
            return

        # Teste 4: Listar pets
        test_get_pets()

        # Teste 5: Enviar dados GPS
        test_send_gps_data(api_key, num_points=10)

        # Teste 6: Obter ultima localizacao
        test_get_location(pet_id)

        # Teste 7: Obter historico
        test_get_history(pet_id)

        # Teste 8: Criar cerca virtual
        test_create_geofence(pet_id)

        print("\n" + "="*60)
        print("[SUCESSO] TODOS OS TESTES CONCLUIDOS!")
        print("="*60)
        print(f"\nAcesse http://localhost:5000/mapa para ver o mapa")
        print(f"Pet ID: {pet_id}")
        print(f"API Key: {api_key}")

    except requests.exceptions.ConnectionError:
        print("\n[ERRO] Nao foi possivel conectar ao servidor.")
        print("   Certifique-se de que o servidor esta rodando em http://localhost:5000")
    except Exception as e:
        print(f"\n[ERRO] ERRO INESPERADO: {e}")


if __name__ == "__main__":
    run_all_tests()
