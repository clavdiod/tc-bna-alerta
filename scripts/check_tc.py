import requests
from bs4 import BeautifulSoup
import os, subprocess, json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://www.bna.com.ar/Personas"
HISTORICO = "data/historico.json"
FECHA_FILE = "data/ultima_fecha.txt"

def obtener_cotizaciones():
    r = requests.get(URL, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Buscar la tabla de DIVISAS
    tabla = soup.find("table", {"id": "cotizacionDivisas"})
    fecha = soup.find("div", {"class": "fecha"}).text.strip()
    
    cotizaciones = {}
    for fila in tabla.find_all("tr")[1:]:
        cols = [c.text.strip() for c in fila.find_all("td")]
        if len(cols) >= 3:
            moneda, compra, venta = cols[0], cols[1], cols[2]
            cotizaciones[moneda] = {"compra": compra, "venta": venta}
    return fecha, cotizaciones
