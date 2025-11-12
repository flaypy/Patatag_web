# 🚀 Guia Rápido de Início - PATATAG

Comece a usar o sistema de rastreamento em **5 minutos**!

---

## Passo 1: Instalar Dependências

```bash
pip install -r requirements.txt
```

---

## Passo 2: Iniciar o Servidor

```bash
python app.py
```

O servidor estará em: **http://localhost:5000**

---

## Passo 3: Testar a API (SEM ESP32)

Execute o script de teste para criar dados de exemplo:

```bash
python test_api.py
```

Este script irá:
- ✅ Criar usuário de teste
- ✅ Criar um pet chamado "Rex"
- ✅ Enviar 10 localizações GPS simuladas
- ✅ Criar uma cerca virtual

**Credenciais criadas:**
- Email: `teste@teste.com`
- Senha: `123456`

---

## Passo 4: Visualizar no Navegador

Acesse: **http://localhost:5000**

1. Faça login com as credenciais acima
2. Vá para "Mapa Geral"
3. Veja a localização do pet "Rex"

---

## Próximos Passos (Quando tiver o ESP32)

### Hardware Necessário

- ESP32
- NEO-6M V2 GPS Module
- Jumpers

### Conexões

```
NEO-6M → ESP32
--------------
VCC    → 3.3V
GND    → GND
TX     → GPIO 16
RX     → GPIO 17
```

### Configurar ESP32

1. **Abrir Arduino IDE**

2. **Instalar bibliotecas:**
   - TinyGPSPlus
   - ArduinoJson

3. **Abrir arquivo:** `esp32_gps_tracker.ino`

4. **Configurar WiFi e API:**
   ```cpp
   const char* WIFI_SSID = "SEU_WIFI";
   const char* WIFI_PASSWORD = "SUA_SENHA";
   const char* API_URL = "http://SEU_IP:5000/api/gps/update";
   const char* API_KEY = "COPIE_DA_WEB";
   ```

5. **Obter API Key:**
   - Acesse a web
   - Crie um novo pet
   - **Copie a API Key** (aparece só uma vez!)

6. **Fazer upload** para o ESP32

7. **Abrir Serial Monitor** (115200 baud)

8. **Aguardar:**
   - WiFi conectar (~10s)
   - GPS fix (~5-10 min na primeira vez)

---

## Estrutura de Arquivos Importantes

```
FlaskProject/
│
├── app.py                    # Servidor principal
├── test_api.py              # Script de teste (use este!)
├── esp32_gps_tracker.ino    # Código para ESP32
│
├── README.md                # Documentação completa
├── API_DOCUMENTATION.md     # Referência da API
├── QUICK_START.md          # Este arquivo
│
└── templates/
    └── mapa_exemplo.html    # Template com Leaflet integrado
```

---

## Comandos Úteis

### Criar usuário de teste
```bash
flask create-test-user
```

### Rodar testes da API
```bash
python test_api.py
```

### Ver logs em tempo real
```bash
python app.py
# Deixar rodando e abrir outro terminal
```

---

## Troubleshooting Rápido

### Erro "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Erro "Address already in use"
Porta 5000 ocupada. Altere em `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # Use porta diferente
```

### GPS não conecta
- Aguarde 10 minutos na primeira vez
- Coloque próximo à janela
- Verifique conexões TX/RX

### Mapa não carrega
- Verifique console do navegador (F12)
- Certifique-se que JavaScript está habilitado
- Teste com `mapa_exemplo.html`

---

## Links Úteis

- **Interface Web:** http://localhost:5000
- **Documentação API:** `API_DOCUMENTATION.md`
- **README Completo:** `README.md`

---

## Checklist de Teste

Antes de usar o ESP32, teste tudo com o script:

- [ ] Servidor Flask rodando
- [ ] Script `test_api.py` executado com sucesso
- [ ] Login na web funcionando
- [ ] Mapa exibindo localização do pet "Rex"
- [ ] Histórico de localizações visível
- [ ] Cerca virtual aparecendo no mapa

**Se tudo acima funcionar, está pronto para o ESP32!**

---

## Próximas Funcionalidades

Já implementado:
- ✅ Rastreamento GPS em tempo real
- ✅ Histórico de localizações
- ✅ Cercas virtuais (geofencing)
- ✅ Alertas de bateria baixa
- ✅ Múltiplos pets por usuário
- ✅ Interface web responsiva

Planejado:
- [ ] App mobile
- [ ] Notificações push
- [ ] Compartilhamento de localização
- [ ] Análise de padrões

---

**Pronto! Seu sistema de rastreamento está funcionando! 🎉**

Qualquer dúvida, consulte `README.md` ou `API_DOCUMENTATION.md`
