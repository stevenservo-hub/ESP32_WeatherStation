import dht
import network
import socket
from machine import Pin

ssid = ''
password = ''

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    pass

sensor = dht.DHT11(Pin(14))

def read_sensor():
    sensor.measure()
    return sensor.temperature(), sensor.humidity()

html = """<!DOCTYPE html>
<html>
    <head> <title>ESP32 Weather Station</title> </head>
    <body>
        <h1>ESP32 Weather Station</h1>
        <table border="1"> <tr><th>Measurement</th><th>Value</th></tr> %s </table>
    </body>
</html>
"""

def make_table_row(name, value):
    return '<tr><td>{}</td><td>{}</td></tr>'.format(name, value)

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

while True:
    cl, addr = s.accept()
    cl_file = cl.makefile('rwb', 0)
    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break

    temperature, humidity = read_sensor()
    rows = make_table_row('Temperature', '{} C'.format(temperature))
    rows += make_table_row('Humidity', '{} %'.format(humidity))

    response = html % rows
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()

