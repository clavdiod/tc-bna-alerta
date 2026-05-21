import requests, os, json, time, smtplib
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

URL = "https://www.bna.com.ar/Personas"
HISTORICO_FILE = "data/historico.json"
FECHA_FILE = "data/ultima_fecha.txt"

def obtener_cotizaciones():
    r = requests.get(URL, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")

    # Buscar tabla de billetes/divisas
    tabla = soup.find("table", {"class": "cotizacion"})
    if tabla is None:
        print("⚠️ No se encontró la tabla de cotizaciones en la web del BNA.")
        return None, {}

    # Extraer fecha real del HTML (th con clase fechaCot)
    fecha_tag = tabla.find("th", {"class": "fechaCot"})
    if fecha_tag:
        fecha = fecha_tag.text.strip()
    else:
        fecha = time.strftime("%-d/%-m/%Y")

    filas = tabla.find_all("tr")[1:]
    cotizaciones = {}
    for fila in filas:
        cols = [c.text.strip() for c in fila.find_all("td")]
        if len(cols) >= 3:
            moneda, compra, venta = cols[0], cols[1], cols[2]
            cotizaciones[moneda] = {"compra": compra, "venta": venta}

    return fecha, cotizaciones

def guardar_historico(fecha, cotizaciones):
    nuevo = {"fecha": fecha, "cotizaciones": cotizaciones}
    if os.path.exists(HISTORICO_FILE):
        with open(HISTORICO_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(nuevo)
    with open(HISTORICO_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def enviar_mail(fecha, cotizaciones):
    lineas = [f"Fecha: {fecha}", "Moneda\tCompra\tVenta"]
    for moneda, valores in cotizaciones.items():
        lineas.append(f"{moneda}\t{valores['compra']}\t{valores['venta']}")
    cuerpo = "\n".join(lineas)

    msg = MIMEMultipart()
    msg["From"] = "github-actions@github.com"
    msg["To"] = "isaac.dabul@zurich.com"
    msg["Cc"] = "clavdio81@hotmail.com"
    msg["Subject"] = f"Alerta TC BNA - {fecha}"
    msg.attach(MIMEText(cuerpo, "plain"))

    try:
        with smtplib.SMTP("localhost") as server:
            server.sendmail(
                msg["From"],
                [msg["To"], msg["Cc"]],
                msg.as_string()
            )
        print("📧 Mail enviado correctamente.")
    except Exception as e:
        print(f"⚠️ Error al enviar mail: {e}")

def main():
    while True:
        fecha, cotizaciones = obtener_cotizaciones()
        if not cotizaciones:
            print("⚠️ No se pudieron obtener cotizaciones. Reintentando en 60 segundos...")
            time.sleep(60)
            continue

        ultima_fecha = ""
        if os.path.exists(FECHA_FILE):
            ultima_fecha = open(FECHA_FILE).read().strip()

        print(f"🔎 Fecha detectada en web: {fecha} | Última guardada: {ultima_fecha}")

        if fecha != ultima_fecha:
            guardar_historico(fecha, cotizaciones)
            open(FECHA_FILE, "w").write(fecha)
            enviar_mail(fecha, cotizaciones)
            print(f"✅ Nueva fecha {fecha} impactada en histórico y mail enviado.")
            break
        else:
            print(f"⏳ Fecha {fecha} ya registrada. Reintentando en 1 segundo...")
            time.sleep(1)

if __name__ == "__main__":
    main()
