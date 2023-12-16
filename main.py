
from umqttsimple import MQTTClient
import machine, neopixel, time
import network
from machine import Pin, time_pulse_us

ssid = "UFRN"
password = ""
station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())


# configura leds das vagas 1 e 2
n = 1

p1 = 13
np1 = neopixel.NeoPixel(machine.Pin(p1), n)

p2 = 25
np2 = neopixel.NeoPixel(machine.Pin(p2), n)

# configura os pinos GPIO para o sensor HC-SR04 das vagas 1 e 2
pin_trigger_1 = Pin(27, Pin.OUT)
pin_echo_1 = Pin(26, Pin.IN)

pin_trigger_2 = Pin(14, Pin.OUT)
pin_echo_2 = Pin(12, Pin.IN)

# configuração mqtt
mqtt_broker = "lar.ect.ufrn.br"
mqtt_port = 1883
mqtt_user = "mqtt"
mqtt_password = "lar_mqtt"
mqtt_client_id = "esp32projeto"
mqtt_topic = "projeto/vaga"

def on_message(topic, msg):
    print("Mensagem recebida no tópico {}: {}".format(topic, msg))
    
#conecta ao broker mqtt
client = MQTTClient(mqtt_client_id, mqtt_broker, mqtt_port, mqtt_user, mqtt_password)
client.set_callback(on_message)
client.connect()

def medir_distancia(pin_echo, pin_trigger):
    # Enviar pulso de trigger
    pin_trigger.value(1)
    time.sleep_us(10)
    pin_trigger.value(0)

    # Medir o tempo de retorno do pulso echo
    tempo_pulse = time_pulse_us(pin_echo, 1, 30000)  # Timeout de 30ms
    distancia_cm = (tempo_pulse / 2) / 29.1  # Convertendo para centímetros

    return distancia_cm

def situacao_vaga(distancia):
    message = ""
    if (distancia < 8.0):
        message = "Ocupada"
    else:
        message = "Livre"
        
    return message
    
# medir distância das vagas e imprimir o resultado
cont = 0
while cont < 10:
    distancia_vaga1 = medir_distancia(pin_echo_1, pin_trigger_1)
    distancia_vaga2 = medir_distancia(pin_echo_2, pin_trigger_2)
    
    situacao_vaga1 = situacao_vaga(distancia_vaga1)
    situacao_vaga2 = situacao_vaga(distancia_vaga2)
    
    if situacao_vaga1 == "Ocupada":
        np1[0] = (255, 0, 0)
        np1.write()
        message = "Vaga 1 ocupada"
        client.publish(mqtt_topic, message)
    else:
        np1[0] = (0, 255, 0)
        np1.write()
        message = "Vaga 1 livre"
        client.publish(mqtt_topic, message)
        
    if situacao_vaga2 == "Ocupada":
        np2[0] = (255, 0, 0)
        np2.write()
        message = "Vaga 2 ocupada"
        client.publish(mqtt_topic, message)
    else:
        np2[0] = (0, 255, 0)
        np2.write()
        message = "Vaga 2 livre"
        client.publish(mqtt_topic, message)

    cont= cont+1
    print("Distância vaga 1:", distancia_vaga1, "cm")
    print("Distância vaga 2:", distancia_vaga2, "cm")
    time.sleep(2)