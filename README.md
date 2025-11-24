<img src="[https://github.com/user-attachments/assets/fedb1de5-0a4a-449b-b82c-1408b836ee4f](https://i.imgur.com/Nwtd8hc.png")" />

# 🐾 PATATAG - Rastreador GPS para Pets

Sistema completo de rastreamento de pets em tempo real usando **ESP32** + **NEO-6M GPS** + **Flask** + **Leaflet Maps**

---

## 📋 Sobre o Projeto

O Patatag é um sistema de rastreamento GPS para pets desenvolvido como Trabalho de Conclusão de Curso (TCC) no curso de Desenvolvimento de Software Multiplataforma da Fatec Praia Grande.

O sistema permite:

- ✅ Monitorar localização em tempo real
- ✅ Visualizar histórico de movimentação
- ✅ Criar cercas virtuais (geofencing)
- ✅ Receber alertas quando o pet sair da zona segura
- ✅ Monitorar nível de bateria do dispositivo
- ✅ Interface web responsiva e moderna

---

## 🛠 Tecnologias Utilizadas

### Backend
- Python 3.8+
- Flask (Framework web)
- SQLAlchemy (ORM)
- SQLite (Banco de dados)

### Frontend
- HTML5 + TailwindCSS
- JavaScript (Vanilla)
- Leaflet.js (Mapas interativos)
- Server-Sent Events (Tempo real)

### IoT
- ESP32
- NEO-6M V2 GPS Module
- Arduino IDE / PlatformIO

---

## 🚀 Instalação e Setup

### 1. Clonar o Repositório

```bash
cd FlaskProject
```

### 2. Criar Ambiente Virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Executar o Servidor

```bash
python app.py
```

O servidor estará disponível em: `http://localhost:5000`

### 5. Criar Usuário de Teste (Opcional)

```bash
flask create-test-user
```

**Credenciais:**
- Email: `teste@teste.com`
- Senha: `123456`

---

## 📱 Configurar ESP32

### Hardware Necessário

- ESP32 (qualquer modelo)
- NEO-6M V2 GPS Module
- Bateria LiPo 3.7V (recomendado)
- Jumpers

### Conexões

```
NEO-6M V2    →    ESP32
--------------------------
VCC          →    3.3V
GND          →    GND
TX           →    GPIO 16 (RX2)
RX           →    GPIO 17 (TX2)
```

### Software

1. **Instalar Arduino IDE**
   - Download: https://www.arduino.cc/en/software

2. **Instalar Bibliotecas**
   - TinyGPSPlus (Mikal Hart)
   - ArduinoJson (Benoit Blanchon)

3. **Configurar ESP32**
   - Abrir `esp32_gps_tracker.ino`
   - Editar configurações:
     ```cpp
     const char* WIFI_SSID = "SEU_WIFI";
     const char* WIFI_PASSWORD = "SUA_SENHA";
     const char* API_URL = "http://SEU_IP:5000/api/gps/update";
     const char* API_KEY = "API_KEY_DO_SEU_PET";
     ```

4. **Upload**
   - Conectar ESP32 via USB
   - Selecionar a placa correta
   - Fazer upload do código

5. **Testar**
   - Abrir Serial Monitor (115200 baud)
   - Aguardar conexão WiFi
   - Aguardar fix GPS (pode levar 5-10 min)

---

## 🌐 Uso da Aplicação Web

### 1. Acessar a Aplicação

```
http://localhost:5000
```

### 2. Criar Conta

- Clique em "Cadastrar"
- Preencha seus dados
- Faça login

### 3. Adicionar Pet

- Clique em "Adicionar Pet"
- Preencha as informações do pet
- **IMPORTANTE:** Guarde a API Key gerada!

### 4. Configurar ESP32

- Use a API Key no código do ESP32
- Faça upload do código
- Aguarde o dispositivo conectar

### 5. Visualizar no Mapa

- Acesse "Mapa Geral"
- Veja a localização em tempo real
- Explore o histórico e cercas virtuais

---

## 📡 API REST

### Endpoints Principais

#### Autenticação
- `POST /api/register` - Registrar usuário
- `POST /api/login` - Fazer login
- `POST /api/logout` - Fazer logout

#### Pets
- `GET /api/pets` - Listar pets
- `POST /api/pets` - Criar pet
- `GET /api/pets/{id}` - Obter pet
- `PUT /api/pets/{id}` - Atualizar pet
- `DELETE /api/pets/{id}` - Deletar pet

#### GPS (ESP32)
- `POST /api/gps/update` - Enviar localização

#### Localização
- `GET /api/pets/{id}/location` - Última localização
- `GET /api/pets/{id}/history` - Histórico

#### Geofencing
- `GET /api/pets/{id}/geofence` - Listar cercas
- `POST /api/pets/{id}/geofence` - Criar cerca
- `DELETE /api/geofence/{id}` - Deletar cerca

#### Tempo Real
- `GET /api/pets/{id}/stream` - Stream SSE

**Documentação completa:** Veja `API_DOCUMENTATION.md`

---

## 📂 Estrutura do Projeto

```
FlaskProject/
│
├── app.py                      # Aplicação Flask principal
├── models.py                   # Modelos do banco de dados
├── config.py                   # Configurações
├── requirements.txt            # Dependências Python
│
├── templates/                  # Templates HTML
│   ├── login_web.html
│   ├── cadastro_web.html
│   ├── home_pets_web.html
│   ├── mapa_web.html
│   ├── adicionar_pet_web.html
│   └── perfil_web.html
│
├── static/                     # Arquivos estáticos
│   ├── api.js                 # Cliente API JavaScript
│   └── map.js                 # Integração com mapas
│
├── esp32_gps_tracker.ino      # Código para ESP32
│
├── patatag.db                 # Banco de dados SQLite
│
├── README.md                  # Este arquivo
└── API_DOCUMENTATION.md       # Documentação da API
```

---

## 🔒 Segurança

### Para Desenvolvimento

O projeto está configurado para desenvolvimento. **Não use em produção sem as seguintes alterações:**

### Para Produção

1. **Alterar SECRET_KEY** em `config.py`
2. **Usar HTTPS** (SSL/TLS)
3. **Banco de dados robusto** (PostgreSQL/MySQL)
4. **Implementar rate limiting**
5. **Validar todas as entradas**
6. **Configurar CORS adequadamente**
7. **Usar variáveis de ambiente** para credenciais

---

## 🐛 Troubleshooting

### ESP32 não conecta

- ✓ Verifique SSID e senha do WiFi
- ✓ Verifique se está no alcance do WiFi
- ✓ Abra Serial Monitor (115200 baud)

### GPS sem sinal

- ✓ Aguarde 5-10 minutos (primeira conexão)
- ✓ Use em área externa ou próximo a janela
- ✓ Verifique conexões TX/RX
- ✓ LED do NEO-6M deve piscar

### Localização não aparece

- ✓ Verifique API Key no ESP32
- ✓ Verifique se servidor está rodando
- ✓ Abra console do navegador (F12)
- ✓ Verifique logs do servidor

### Erro de permissão no Linux

```bash
sudo chmod 666 /dev/ttyUSB0
```

---

## 📊 Funcionalidades Futuras

- [ ] App mobile (React Native)
- [ ] Notificações push
- [ ] Suporte para múltiplos dispositivos por pet
- [ ] Análise de padrões de movimento
- [ ] Compartilhamento de localização
- [ ] Integração com Google Maps
- [ ] Modo offline com sincronização
- [ ] Dashboard com estatísticas

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abrir um Pull Request

---

## 📝 Licença

Este projeto é open source e está disponível sob a licença MIT.

---

## 👥 Autores

- **Lucas Paiolo**
- **Kevin Flay**
- **Gael Mormile**
- **Marcos Antonio**

---

## 🙏 Agradecimentos

Gostaríamos de expressar nossa profunda gratidão a todos que tornaram este projeto possível:

À **Fatec Praia Grande**, pela infraestrutura e pela excelência no ensino proporcionado no curso de Desenvolvimento de Software Multiplataforma.

À nossa orientadora, **Prof.ª Eulaliane Aparecida Gonçalves**, por todo o suporte, paciência e conhecimento compartilhado, fundamentais para a concretização deste trabalho.

---

## 📞 Suporte

Se você encontrar algum problema ou tiver dúvidas:

1. Verifique a documentação (`API_DOCUMENTATION.md`)
2. Veja a seção de Troubleshooting
3. Abra uma issue no repositório

---

**Feito com ❤️ para manter seus pets seguros!**

🐕 🐈 🐾
