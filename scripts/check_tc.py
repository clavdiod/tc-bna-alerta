import requests
from bs4 import BeautifulSoup
import os, subprocess, json

URL = "https://www.bna.com.ar/Personas"
HISTORICO = "data/historico.json"
FECHA_FILE = "data/ultima_fecha.txt"

def obtener_cotizaciones():
    r = requests.get(URL, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    tabla = soup.find("table", {"id": "cotizacionDivisas"})
    fecha = soup.find("div", {"class": "fecha"}).text.strip()
    cotizaciones = {}
    for fila in tabla.find_all("tr")[1:]:
        cols = [c.text.strip() for c in fila.find_all("td")]
        if len(cols) >= 3:
            moneda, compra, venta = cols[0], cols[1], cols[2]
            cotizaciones[moneda] = {"compra": compra, "venta": venta}
    return fecha, cotizaciones

def enviar_alerta(fecha, cotizaciones):
    mensaje = f"""Subject: Actualización TC BNA {fecha}
To: isaac.dabul@zurich.com
From: alerta@tc-bna.com

Nueva fecha detectada: {fecha}
Cotizaciones: {cotizaciones}
"""
    subprocess.run(["sendmail", "isaac.dabul@zurich.com"], input=mensaje.encode())

def guardar_historico(fecha, cotizaciones):
    os.makedirs("data", exist_ok=True)
    if os.path.exists(HISTORICO):
        data = json.load(open(HISTORICO))
    else:
        data = []
    data.append({"fecha": fecha, "cotizaciones": cotizaciones})
    json.dump(data, open(HISTORICO, "w"), indent=2)

def main():
    fecha, cotizaciones = obtener_cotizaciones()
    ultima_fecha = open(FECHA_FILE).read().strip() if os.path.exists(FECHA_FILE) else ""
    if fecha != ultima_fecha:
        guardar_historico(fecha, cotizaciones)
        enviar_alerta(fecha, cotizaciones)
        open(FECHA_FILE, "w").write(fecha)

if __name__ == "__main__":
    main()
