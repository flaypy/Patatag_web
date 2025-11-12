# PATATAG - Documentação da API

Sistema de rastreamento GPS para pets usando ESP32 + NEO-6M V2

---

## Sumário

- [Começando](#começando)
- [Autenticação](#autenticação)
- [Endpoints](#endpoints)
  - [Usuários](#usuários)
  - [Pets](#pets)
  - [Localização GPS](#localização-gps)
  - [Cercas Virtuais (Geofencing)](#cercas-virtuais)
  - [Alertas](#alertas)
  - [Tempo Real](#tempo-real)
- [Códigos de Status](#códigos-de-status)
- [Exemplos de Uso](#exemplos-de-uso)

---

## Começando

### Instalação e Setup

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Inicializar banco de dados:**
```bash
python app.py
# O banco será criado automaticamente na primeira execução
```

3. **Rodar o servidor:**
```bash
python app.py
# Servidor rodará em http://localhost:5000
```

4. **Criar usuário de teste (opcional):**
```bash
flask create-test-user
# Email: teste@teste.com | Senha: 123456
```

### URL Base

```
http://localhost:5000
```

Para produção, substitua pela URL do seu servidor.

---

## Autenticação

A API usa sessões baseadas em cookies. Após fazer login, o cookie de sessão será incluído automaticamente nas requisições.

### Registrar Novo Usuário

**POST** `/api/register`

```json
{
  "name": "João Silva",
  "email": "joao@email.com",
  "password": "senha123"
}
```

**Resposta (201):**
```json
{
  "message": "Usuário cadastrado com sucesso",
  "user": {
    "id": 1,
    "name": "João Silva",
    "email": "joao@email.com",
    "created_at": "2025-01-06T12:00:00"
  }
}
```

### Login

**POST** `/api/login`

```json
{
  "email": "joao@email.com",
  "password": "senha123"
}
```

**Resposta (200):**
```json
{
  "message": "Login realizado com sucesso",
  "user": {
    "id": 1,
    "name": "João Silva",
    "email": "joao@email.com"
  }
}
```

### Logout

**POST** `/api/logout`

**Resposta (200):**
```json
{
  "message": "Logout realizado com sucesso"
}
```

---

## Endpoints

### Pets

#### Listar Todos os Pets

**GET** `/api/pets`

**Resposta (200):**
```json
{
  "pets": [
    {
      "id": 1,
      "name": "Luke",
      "species": "Cachorro",
      "breed": "Golden Retriever",
      "photo_url": "https://...",
      "device_id": "ESP32_A1B2C3",
      "is_online": true,
      "battery_level": 85,
      "last_seen": "2025-01-06T12:30:00",
      "last_location": {
        "latitude": -23.550520,
        "longitude": -46.633308,
        "timestamp": "2025-01-06T12:30:00"
      }
    }
  ]
}
```

#### Obter Pet Específico

**GET** `/api/pets/{pet_id}`

#### Criar Novo Pet

**POST** `/api/pets`

```json
{
  "name": "Luke",
  "species": "Cachorro",
  "breed": "Golden Retriever",
  "photo_url": "https://..."
}
```

**Resposta (201):**
```json
{
  "message": "Pet criado com sucesso",
  "pet": { ... },
  "api_key": "xYz123...",
  "device_id": "ESP32_A1B2C3"
}
```

**⚠️ IMPORTANTE:** Guarde a `api_key`! Ela só é mostrada uma vez e será usada no ESP32.

#### Atualizar Pet

**PUT** `/api/pets/{pet_id}`

```json
{
  "name": "Luke Updated",
  "breed": "Golden Retriever"
}
```

#### Deletar Pet

**DELETE** `/api/pets/{pet_id}`

---

### Localização GPS

#### Enviar Localização (ESP32)

**POST** `/api/gps/update`

**Autenticação:** API Key

```json
{
  "api_key": "sua_api_key_aqui",
  "latitude": -23.550520,
  "longitude": -46.633308,
  "altitude": 760.0,
  "speed": 0.0,
  "satellites": 8,
  "hdop": 1.2,
  "battery": 85
}
```

**Resposta (200):**
```json
{
  "message": "Localização atualizada com sucesso",
  "location_id": 123
}
```

**Campos obrigatórios:**
- `api_key`: Chave de autenticação do dispositivo
- `latitude`: Latitude em graus decimais (-90 a 90)
- `longitude`: Longitude em graus decimais (-180 a 180)

**Campos opcionais:**
- `altitude`: Altitude em metros
- `speed`: Velocidade em km/h
- `satellites`: Número de satélites conectados
- `hdop`: Precisão horizontal (HDOP)
- `battery`: Nível de bateria (0-100)

#### Obter Última Localização

**GET** `/api/pets/{pet_id}/location`

**Resposta (200):**
```json
{
  "id": 123,
  "pet_id": 1,
  "latitude": -23.550520,
  "longitude": -46.633308,
  "altitude": 760.0,
  "speed": 0.0,
  "satellites": 8,
  "hdop": 1.2,
  "timestamp": "2025-01-06T12:30:00"
}
```

#### Obter Histórico de Localizações

**GET** `/api/pets/{pet_id}/history`

**Parâmetros de Query:**
- `page` (int): Página (padrão: 1)
- `limit` (int): Itens por página (padrão: 100)
- `start_date` (ISO 8601): Data inicial
- `end_date` (ISO 8601): Data final

**Exemplo:**
```
GET /api/pets/1/history?page=1&limit=50&start_date=2025-01-01T00:00:00Z
```

**Resposta (200):**
```json
{
  "locations": [ ... ],
  "total": 250,
  "pages": 5,
  "current_page": 1
}
```

---

### Cercas Virtuais

#### Listar Cercas do Pet

**GET** `/api/pets/{pet_id}/geofence`

**Resposta (200):**
```json
{
  "zones": [
    {
      "id": 1,
      "pet_id": 1,
      "name": "Casa",
      "center_lat": -23.550520,
      "center_lng": -46.633308,
      "radius_meters": 100,
      "is_active": true,
      "created_at": "2025-01-06T12:00:00"
    }
  ]
}
```

#### Criar Cerca Virtual

**POST** `/api/pets/{pet_id}/geofence`

```json
{
  "name": "Casa",
  "center_lat": -23.550520,
  "center_lng": -46.633308,
  "radius_meters": 100
}
```

#### Deletar Cerca Virtual

**DELETE** `/api/geofence/{zone_id}`

---

### Alertas

#### Listar Alertas

**GET** `/api/alerts`

**Resposta (200):**
```json
{
  "alerts": [
    {
      "id": 1,
      "pet_id": 1,
      "alert_type": "geofence",
      "message": "Seu pet saiu da zona 'Casa'!",
      "is_read": false,
      "created_at": "2025-01-06T12:00:00"
    }
  ]
}
```

**Tipos de alerta:**
- `geofence`: Pet saiu da cerca virtual
- `battery`: Bateria baixa (≤20%)
- `offline`: Dispositivo offline

#### Marcar Alerta como Lido

**POST** `/api/alerts/{alert_id}/read`

---

### Tempo Real

#### Stream de Localização (SSE)

**GET** `/api/pets/{pet_id}/stream`

Retorna um stream de Server-Sent Events com atualizações em tempo real.

**Exemplo de uso (JavaScript):**
```javascript
const eventSource = new EventSource('/api/pets/1/stream');

eventSource.onmessage = (event) => {
  const location = JSON.parse(event.data);
  console.log('Nova localização:', location);
};
```

---

## Códigos de Status

- **200 OK**: Sucesso
- **201 Created**: Recurso criado com sucesso
- **400 Bad Request**: Dados inválidos ou incompletos
- **401 Unauthorized**: Não autenticado ou API key inválida
- **404 Not Found**: Recurso não encontrado
- **500 Internal Server Error**: Erro no servidor

---

## Exemplos de Uso

### Exemplo: Fluxo Completo

#### 1. Registrar usuário
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"name":"João","email":"joao@email.com","password":"123456"}'
```

#### 2. Fazer login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","password":"123456"}' \
  -c cookies.txt
```

#### 3. Criar pet
```bash
curl -X POST http://localhost:5000/api/pets \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name":"Luke","species":"Cachorro","breed":"Golden Retriever"}'
```

**Guardar a API key retornada!**

#### 4. Configurar ESP32

Editar o arquivo `esp32_gps_tracker.ino`:
```cpp
const char* WIFI_SSID = "MinhaRede";
const char* WIFI_PASSWORD = "minha_senha";
const char* API_URL = "http://MEU_SERVIDOR:5000/api/gps/update";
const char* API_KEY = "API_KEY_RECEBIDA_NO_PASSO_3";
```

#### 5. Upload do código para ESP32

Use a Arduino IDE ou PlatformIO para fazer upload.

#### 6. Visualizar no mapa

Acesse: `http://localhost:5000/mapa`

---

## Bibliotecas Necessárias para ESP32

No Arduino IDE, instale as seguintes bibliotecas:

1. **TinyGPSPlus** by Mikal Hart
2. **ArduinoJson** by Benoit Blanchon

Instale via: *Sketch > Include Library > Manage Libraries*

---

## Segurança

### Recomendações para Produção:

1. **Alterar SECRET_KEY:**
   ```python
   # config.py
   SECRET_KEY = 'gere-uma-chave-segura-aleatoria'
   ```

2. **Usar HTTPS:**
   - Configure SSL/TLS no servidor
   - Atualize ESP32 para usar HTTPS

3. **Banco de dados:**
   - Use PostgreSQL ou MySQL em vez de SQLite
   - Configure backups regulares

4. **Rate Limiting:**
   - Implemente limite de requisições
   - Use Flask-Limiter

5. **Validação:**
   - Validar todas as entradas
   - Sanitizar dados do usuário

---

## Troubleshooting

### ESP32 não conecta ao WiFi
- Verifique SSID e senha
- Verifique sinal WiFi
- Use Serial Monitor (115200 baud)

### GPS sem fix
- Aguarde 5-10 minutos na primeira vez
- Mantenha em área externa
- Verifique conexões TX/RX

### Erro "API key inválida"
- Verifique se copiou a API key corretamente
- Verifique se o pet está cadastrado
- Teste com curl primeiro

### Localização não aparece no mapa
- Verifique console do navegador (F12)
- Verifique se o JavaScript está carregando
- Verifique se há dados no banco

---

## Suporte

Para dúvidas e problemas:
1. Verifique os logs do servidor
2. Verifique Serial Monitor do ESP32
3. Verifique console do navegador

---

## Licença

Este projeto é de código aberto e pode ser usado livremente.

---

**Desenvolvido com ❤️ para pets seguros**
