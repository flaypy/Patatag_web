/*
 * PATATAG - Rastreador GPS para Pets
 * ESP32 + NEO-6M GPS Module
 *
 * Conexões do NEO-6M V2:
 * - VCC -> 3.3V ou 5V do ESP32
 * - GND -> GND do ESP32
 * - TX  -> GPIO 16 (RX2 do ESP32)
 * - RX  -> GPIO 17 (TX2 do ESP32)
 *
 * Autor: Sistema Patatag
 * Data: 2025
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>
#include <ArduinoJson.h>

// ==========================================
// CONFIGURAÇÕES - ALTERE AQUI
// ==========================================

// WiFi
const char* WIFI_SSID = "Celular de Lucas";
const char* WIFI_PASSWORD = "lucaspaiolo123456789";

// API
const char* API_URL = "http://SEU_SERVIDOR:5000/api/gps/update";
const char* API_KEY = "SUA_API_KEY_AQUI";  // Você recebe isso ao criar o pet no sistema

// Configurações de envio
const unsigned long SEND_INTERVAL = 30000;  // Enviar a cada 30 segundos
const unsigned long GPS_TIMEOUT = 60000;    // Timeout para obter fix GPS

// ==========================================
// OBJETOS GLOBAIS
// ==========================================

TinyGPSPlus gps;
HardwareSerial GPS_Serial(2);  // UART2 do ESP32

unsigned long lastSendTime = 0;
unsigned long lastGPSCheck = 0;
bool wifiConnected = false;

// ==========================================
// SETUP
// ==========================================

void setup() {
  Serial.begin(115200);
  GPS_Serial.begin(9600, SERIAL_8N1, 16, 17);  // RX=16, TX=17

  Serial.println("\n=================================");
  Serial.println("PATATAG GPS Tracker v1.0");
  Serial.println("ESP32 + NEO-6M");
  Serial.println("=================================\n");

  // Conectar WiFi
  connectWiFi();

  Serial.println("Aguardando sinal GPS...");
  Serial.println("(Isso pode levar alguns minutos na primeira vez)");
}

// ==========================================
// LOOP PRINCIPAL
// ==========================================

void loop() {
  // Ler dados do GPS
  while (GPS_Serial.available() > 0) {
    gps.encode(GPS_Serial.read());
  }

  // Verificar conexão WiFi
  if (WiFi.status() != WL_CONNECTED) {
    wifiConnected = false;
    Serial.println("WiFi desconectado! Reconectando...");
    connectWiFi();
  } else {
    wifiConnected = true;
  }

  // Enviar dados se o intervalo passou
  unsigned long currentTime = millis();
  if (currentTime - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = currentTime;

    if (gps.location.isValid()) {
      sendGPSData();
    } else {
      Serial.println("Aguardando fix GPS...");
      displayGPSInfo();
    }
  }

  delay(100);
}

// ==========================================
// FUNÇÕES
// ==========================================

void connectWiFi() {
  Serial.print("Conectando ao WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi conectado!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    wifiConnected = true;
  } else {
    Serial.println("\nFalha ao conectar WiFi!");
    wifiConnected = false;
  }
}

void sendGPSData() {
  if (!wifiConnected) {
    Serial.println("WiFi não conectado. Pulando envio.");
    return;
  }

  if (!gps.location.isValid()) {
    Serial.println("GPS sem fix válido. Pulando envio.");
    return;
  }

  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");

  // Criar JSON com os dados
  StaticJsonDocument<512> doc;

  doc["api_key"] = API_KEY;
  doc["latitude"] = gps.location.lat();
  doc["longitude"] = gps.location.lng();

  if (gps.altitude.isValid()) {
    doc["altitude"] = gps.altitude.meters();
  }

  if (gps.speed.isValid()) {
    doc["speed"] = gps.speed.kmph();
  }

  if (gps.satellites.isValid()) {
    doc["satellites"] = gps.satellites.value();
  }

  if (gps.hdop.isValid()) {
    doc["hdop"] = gps.hdop.hdop();
  }

  // Adicionar nível de bateria (simulado - você pode adicionar um sensor real)
  doc["battery"] = getBatteryLevel();

  // Serializar JSON
  String jsonData;
  serializeJson(doc, jsonData);

  Serial.println("\n--- Enviando dados ---");
  Serial.println(jsonData);

  // Enviar requisição POST
  int httpResponseCode = http.POST(jsonData);

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("Código de resposta: ");
    Serial.println(httpResponseCode);
    Serial.print("Resposta: ");
    Serial.println(response);

    if (httpResponseCode == 200) {
      Serial.println("✓ Localização enviada com sucesso!");
      displayCurrentLocation();
    } else {
      Serial.println("✗ Erro ao enviar localização");
    }
  } else {
    Serial.print("✗ Erro na requisição HTTP: ");
    Serial.println(http.errorToString(httpResponseCode));
  }

  http.end();
}

void displayCurrentLocation() {
  Serial.println("\n--- Localização Atual ---");
  Serial.print("Lat: ");
  Serial.print(gps.location.lat(), 6);
  Serial.print(" | Lon: ");
  Serial.println(gps.location.lng(), 6);

  if (gps.altitude.isValid()) {
    Serial.print("Altitude: ");
    Serial.print(gps.altitude.meters());
    Serial.println(" m");
  }

  if (gps.speed.isValid()) {
    Serial.print("Velocidade: ");
    Serial.print(gps.speed.kmph());
    Serial.println(" km/h");
  }

  if (gps.satellites.isValid()) {
    Serial.print("Satélites: ");
    Serial.println(gps.satellites.value());
  }

  if (gps.hdop.isValid()) {
    Serial.print("HDOP (precisão): ");
    Serial.println(gps.hdop.hdop());
  }

  Serial.println("------------------------\n");
}

void displayGPSInfo() {
  Serial.print("Satélites: ");
  if (gps.satellites.isValid()) {
    Serial.print(gps.satellites.value());
  } else {
    Serial.print("0");
  }

  Serial.print(" | Caracteres processados: ");
  Serial.print(gps.charsProcessed());

  Serial.print(" | Sentenças com falha: ");
  Serial.println(gps.failedChecksum());

  if (gps.charsProcessed() < 10) {
    Serial.println("⚠ Nenhum dado GPS recebido. Verifique as conexões!");
  }
}

int getBatteryLevel() {
  // Esta é uma função simulada
  // Para obter o nível real da bateria, você precisará:
  // 1. Adicionar um divisor de tensão no pino ADC do ESP32
  // 2. Ler o valor analógico e converter para porcentagem
  // 3. Ou usar um módulo específico de gerenciamento de bateria

  // Exemplo com ADC (você precisa ajustar conforme seu hardware):
  // int analogValue = analogRead(35);  // GPIO 35 como exemplo
  // int batteryPercent = map(analogValue, 0, 4095, 0, 100);
  // return constrain(batteryPercent, 0, 100);

  // Por enquanto, retorna um valor fixo
  return 85;
}

// ==========================================
// COMANDOS DE DEPURAÇÃO
// ==========================================

/*
 * Monitor Serial:
 * - Abra o Serial Monitor em 115200 baud
 * - Você verá as informações de conexão e GPS
 *
 * Troubleshooting:
 *
 * 1. "Nenhum dado GPS recebido":
 *    - Verifique as conexões TX/RX
 *    - Verifique se o módulo está alimentado (LED deve piscar)
 *    - Deixe o módulo com visão clara do céu
 *
 * 2. "Aguardando fix GPS...":
 *    - O primeiro fix pode levar 5-10 minutos
 *    - Mantenha o módulo em área externa ou próximo à janela
 *    - Aguarde ver 4+ satélites
 *
 * 3. "WiFi não conectado":
 *    - Verifique SSID e senha
 *    - Verifique se o ESP32 está no alcance do WiFi
 *
 * 4. "Erro ao enviar localização":
 *    - Verifique se o servidor está rodando
 *    - Verifique a API_KEY
 *    - Verifique a URL da API
 */
