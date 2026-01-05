import streamlit as st
import pandas as pd
import google.generativeai as genai
import datetime
import time


genai.configure(api_key="AIzaSyB-4O4lWJJp8Kv43w3On59ZTYveiGXSFpU")
model = genai.GenerativeModel("models/gemini-2.0-flash")

def calcular_tono(fecha_vencimiento, deuda):
    hoy = datetime.date.today()
    dias_restantes = (fecha_vencimiento - hoy).days
    
    if dias_restantes > 10 and deuda < 10000:
        return "cordial"
    elif dias_restantes >= 3:
        return "intermedio"
    else:
        return "firme"

def generar_mensaje(nombre, deuda, deuda_vencida, estado_servicio, tono, fecha_vencimiento):
    prompt = f"""
    Actúa como un agente de cobranza de la empresa Sistemas Latinos.
    Cliente: {nombre}
    Deuda total: {deuda} pesos
    Deuda vencida: {deuda_vencida} pesos
    Estado de servicio: {estado_servicio}
    Fecha de vencimiento: {fecha_vencimiento}
    Tono sugerido: {tono}

    Instrucciones adicionales:
    - El pago realizado después de la fecha de vencimiento generará mora.
    - La falta de pago pasado el mes en curso puede provocar la suspensión del servicio.
    - Si el cliente ya realizó el pago, debe enviar el comprobante cuanto antes para corroborar que fue procesado.
    - Si quiere transferir el monto adeudado debera hacerlo al alias "sistemaslatinos" a nombre de Light Speed SA.

    Genera un mensaje respetuoso pero adaptado al tono indicado.
    Firma el mensaje con: "Atentamente, Sistemas Latinos".
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error al generar mensaje: {e}"

def main():
    st.title("Agente de Cobranza con IA (Gemini) - Sistemas Latinos")
    st.write("Sube un archivo CSV con clientes y su historial de pagos.")

    fecha_vencimiento = st.date_input("Fecha próximo vencimiento")
    archivo = st.file_uploader("Subir CSV", type=["csv"])

    if archivo is not None and fecha_vencimiento:
        df = pd.read_csv(archivo)

        # Limpieza de columnas numéricas ($ y puntos de miles)
        df["Deuda"] = pd.to_numeric(
            df["Deuda"].astype(str).str.replace("$", "").str.replace(".", ""), errors="coerce"
        )
        df["Deuda Vencida"] = pd.to_numeric(
            df["Deuda Vencida"].astype(str).str.replace("$", "").str.replace(".", ""), errors="coerce"
        )

        st.write("Datos cargados:", df.head())

        mensajes = []
        for _, row in df.iterrows():
            tono = calcular_tono(fecha_vencimiento, row["Deuda"])
            mensaje = generar_mensaje(
                row["Nombre"], 
                row["Deuda"], 
                row["Deuda Vencida"], 
                row["Estado Servicio"], 
                tono,
                fecha_vencimiento
            )
            mensajes.append(mensaje)

            # Rate limit  (para evitar problemas con la API)
            time.sleep(8)

        df["Mensaje Cobranza"] = mensajes

        st.write("Mensajes generados:", df[["Nombre", "Teléfono", "Mensaje Cobranza"]])

        # Descargar resultados
        csv_resultado = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Descargar mensajes en CSV",
            data=csv_resultado,
            file_name="mensajes_cobranza.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()