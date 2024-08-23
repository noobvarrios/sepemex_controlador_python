import network
import urequests
import ujson
from machine import Pin,RTC
import time
import utime, machine


# Definición de pines
pin19 = Pin(19, Pin.OUT)
pin18 = Pin(18, Pin.OUT)
pin5  = Pin(5, Pin.OUT)
rtc = RTC()

# Conectar a una red Wi-Fi
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
#     wlan.connect("TecNM_Tuxtla", "")
#     wlan.connect("INFINITUM292B_5","25XCsZeTKZ")
    wlan.connect("INFINITUM292B_2.4", "25XCsZeTKZ")
    while not wlan.isconnected():
        pass
    print("Conectado a Wi-Fi")

#ACTIVAR SI EL ESP SE VA A CONECTAR SOLO POR VOLTAJE Y NO A COMPUTADORA. 
# def request_hora():
#     hora_request = urequests.get('https://worldtimeapi.org/api/timezone/America/Mexico_City')
#     json_data = ujson.loads(response.text)
#     print("Datos recibidos:", json_data)  # Para depuración
#     datos_objeto = response.json()
#     fecha_hora = str(datos_objeto["datetime"])
#     año = int(fecha_hora[0:4])
#     mes = int(fecha_hora[5:7])
#     día = int(fecha_hora[8:10])
#     hora = int(fecha_hora[11:13])
#     minutos = int(fecha_hora[14:16])
#     segundos = int(fecha_hora[17:19])
#     sub_segundos = int(round(int(fecha_hora[20:26]) / 10000))
#     #establecer tiempo del rtc 
#     rtc.datetime((año, mes, día, 0, hora, minutos, segundos, sub_segundos))

def hora_fecha_controlador():
    print("Fecha:{2:02d}/{1:02d}/{0:4d}".format(*rtc.datetime()))
    print("Hora: {4:02d}:{5:02d}:{6:02d}".format(*rtc.datetime()))

def hora_especifica_controlador():
    return "{4:02d}:{5:02d}:{6:02d}".format(*rtc.datetime())

# Obtener duraciones desde la API
def obtener_duraciones():
    response = urequests.get('http://adminsepemex02-001-site1.gtempurl.com/tiempos/listar', auth=('11187974', '60-dayfreetrial'))
    if response.status_code == 200:
        # Deserializar los datos JSON
        json_data = ujson.loads(response.text)
        print("Datos recibidos:", json_data)  # Para depuración

        # Verificar si json_data tiene los campos necesarios
        if isinstance(json_data, dict):
            if 'fld_TiempoVerde' in json_data and 'fld_TiempoAmarrillo' in json_data:
                verde_duration = int(json_data['fld_TiempoVerde'])
                amarillo_duration = int(json_data['fld_TiempoAmarrillo'])
                return verde_duration, amarillo_duration
            else:
                print("Error: Campos esperados no encontrados en la respuesta.")
                return None, None
        else:
            print("Error: La respuesta no contiene datos válidos.")
            return None, None
    else:
        print("Error:", response.status_code)
        return None, None
    
def controlar_semaforo(verde_duration, amarillo_duration, rojo_duration):
    # Estado verde
    for i in range(verde_duration):
        pin19.value(0)
        pin18.value(0)
        pin5.value(1)
        print(f"Verde: {i+1} segundos. Hora: ",hora_especifica_controlador())
        hora_especifica_controlador()
        time.sleep(1)
    # Estado amarillo
    for i in range(amarillo_duration):
        pin19.value(0)
        pin18.value(1)
        pin5.value(0)
        print(f"Amarillo: {i+1} segundos. Hora: ",hora_especifica_controlador())
        hora_especifica_controlador()
        time.sleep(1)
    # Estado rojo
    for i in range(rojo_duration):
        pin19.value(1)
        pin18.value(0)
        pin5.value(0)
        print(f"Rojo: {i+1} segundos. Hora: ",hora_especifica_controlador())
        time.sleep(1)

# Conectar a Wi-Fi una sola vez
conectar_wifi()
hora_fecha_controlador()
ciclos = 0 
verde_duration, amarillo_duration = obtener_duraciones()
rojo_duration = verde_duration + 2
while True: 
    ciclos += 1
    if ciclos == 5:
        verde_duration, amarillo_duration = obtener_duraciones()
        rojo_duration = verde_duration + 2
        ciclos = 0  # Reiniciar contador
    
    controlar_semaforo(verde_duration, amarillo_duration, rojo_duration)


