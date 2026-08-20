import streamlit as st
import pandas as pd
from google import genai
import os
import json

st.title("📸 Registrador de Caja Chica")
st.write("Saca una foto a tu factura para registrarla automáticamente.")

API_KEY = st.sidebar.text_input("Ingresa tu Gemini API Key:", type="password")

if API_KEY:
    client = genai.Client(api_key=API_KEY)
    archivo_imagen = st.camera_input("Toma una foto") or st.file_uploader("O sube una imagen", type=["jpg", "png", "jpeg"])
    
    if archivo_imagen:
        bytes_imagen = archivo_imagen.read()
        st.info("🤖 Analizando factura con IA...")
        
        prompt = """
        Analiza esta imagen de factura de caja chica y extrae los siguientes datos en formato JSON estricto:
        {
            "Fecha": "DD/MM/AAAA",
            "Proveedor": "Nombre de la empresa",
            "Detalle": "Breve descripción de lo que se compró",
            "Monto Total": 0.00
        }
        Devuelve SOLO el objeto JSON, nada de texto extra.
        """
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    {'inline_data': {'mime_type': archivo_imagen.type, 'data': bytes_imagen}},
                    prompt
                ]
            )
            texto_limpio = response.text.replace("```json", "").replace("```", "").strip()
            datos_factura = json.loads(texto_limpio)
            
            st.success("¡Datos extraídos correctamente!")
            st.json(datos_factura)
            
            nombre_excel = "registro_caja_chica.xlsx"
            if os.path.exists(nombre_excel):
                df_existente = pd.read_excel(nombre_excel)
            else:
                df_existente = pd.DataFrame(columns=["Fecha", "Proveedor", "Detalle", "Monto Total"])
            
            nuevo_registro = pd.DataFrame([datos_factura])
            df_final = pd.concat([df_existente, nuevo_registro], ignore_index=True)
            df_final.to_excel(nombre_excel, index=False)
            
            st.success("Factura registrada en el sistema temporal.")
            
            with open(nombre_excel, "rb") as f:
                st.download_button(
                    label="📥 Descargar Reporte Excel",
                    data=f,
                    file_name=nombre_excel,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
        except Exception as e:
            st.error(f"Hubo un error al procesar la imagen: {e}")
else:
    st.warning("⚠️ Por favor, ingresa tu Gemini API Key en la barra lateral para comenzar.")
