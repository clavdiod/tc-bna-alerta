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

def guardar_historico(fecha, cotizaciones):
    os.makedirs("data", exist_ok=True)
    if os.path.exists(HISTORICO):
        data = json.load(open(HISTORICO))
    else:
        data = []
    data.append({"fecha": fecha, "cotizaciones": cotizaciones})
    json.dump(data, open(HISTORICO, "w"), indent=2)

def enviar_mail(fecha, cotizaciones):
    # armar el texto en formato tabla
    lineas = [f"{fecha}\tCompra\tVenta"]
    for moneda, valores in cotizaciones.items():
        lineas.append(f"{moneda}\t{valores['compra']}\t{valores['venta']}")
    mensaje = "Subject: Alerta TC BNA\n\n" + "\n".join(lineas)
    
    # enviar mail con sendmail
    subprocess.run(["sendmail", "isaac.dabul@zurich.com"], input=mensaje.encode())


def main():
    fecha, cotizaciones = obtener_cotizaciones()
    ultima_fecha = open(FECHA_FILE).read().strip() if os.path.exists(FECHA_FILE) else ""
    
if fecha != ultima_fecha:
    guardar_historico(fecha, cotizaciones)
    open(FECHA_FILE, "w").write(fecha)
    enviar_mail(fecha, cotizaciones)
elif ultima_fecha == "":
    # primera vez: guarda un valor inicial y manda mail
    guardar_historico(fecha, cotizaciones)
    open(FECHA_FILE, "w").write(fecha)
    enviar_mail(fecha, cotizaciones)


if __name__ == "__main__":
    main()
