
#%%

import streamlit as st
import pandas as pd
import requests
#%%

# Configuración de la página web
st.set_page_config(page_title="Quiniela Mundialista Oficina", layout="wide")

st.title("🏆 App Web del Mundial")
st.write("Suerte amigos :3")

# --- 🟢 COPIA Y PEGA AQUÍ EL ENLACE DE TU GOOGLE SHEET 🟢 ---
URL_HOJA_CALCULO = "https://docs.google.com/spreadsheets/d/1Z0LT1Kt_AOnumF_XM0LQcWyXdDGMB1TRzdQ0WiVK2BU/edit?usp=sharing"

# Lista de personas con beneficio de desempate (+0.1 puntos invisibles)
PERSONAS_DESEMPATE = [
    "noel guerrero", 
    "ricardo avila", 
    "pablo", 
    "ivan", 
    "raul quintero fernandez", 
    "karla", 
    "ulises cruz porchini"
]
#%%
# Función para transformar el enlace normal en un enlace de descarga CSV para Pandas
def obtener_url_csv(url, pestaña):
    try:
        base_url = url.split("/edit")[0]
        return f"{base_url}/gviz/tq?tqx=out:csv&sheet={pestaña}"
    except:
        return ""
    
URL_ELECCIONES = obtener_url_csv(URL_HOJA_CALCULO, "elecciones")
URL_RESULTADOS = obtener_url_csv(URL_HOJA_CALCULO, "resultados")

def normalizar_nombre(nombre_equipo):
    nombre_equipo = str(nombre_equipo).strip().lower()
    reemplazos = {"é": "e", "á": "a", "í": "i", "ó": "o", "ú": "u"}
    for original, reemplazo in reemplazos.items():
        nombre_equipo = nombre_equipo.replace(original, reemplazo)
    return nombre_equipo

#%%
# --- 1. LEER LOS RESULTADOS DEL ADMINISTRADOR DESDE GOOGLE SHEETS ---
puntos_por_equipo = {}

try:
    # Leemos la pestaña de resultados directamente de internet
    df_resultados = pd.read_csv(URL_RESULTADOS)
    
    # Recorremos el tablero fila por fila (un equipo por celda)
    for index, row in df_resultados.iterrows():
        fase = str(row['Fase']).strip().lower()
        equipo = str(row['Equipo']).strip() # Lee la celda del equipo único
        
        # Si la celda no está vacía, procesamos
        if equipo and equipo != "nan":
            eq_normalizado = normalizar_nombre(equipo)
            
            # Asignamos los puntos correspondientes según la fase escrita en la columna A
            if "dieciseisavos" in fase: puntos = 1
            elif "octavos" in fase: puntos = 3
            elif "cuartos" in fase: puntos = 6
            elif "semis" in fase: puntos = 10
            elif "final" in fase: puntos = 15
            else: puntos = 0
            
            # Guardamos el puntaje más alto asignado a ese equipo
            if puntos > 0:
                if eq_normalizado in puntos_por_equipo:
                    if puntos > puntos_por_equipo[eq_normalizado]:
                        puntos_por_equipo[eq_normalizado] = puntos
                else:
                    puntos_por_equipo[eq_normalizado] = puntos
                    
except Exception as e:
    st.error("Esperando configuración correcta de la pestaña 'resultados' en Google Sheets...")


#%%
# --- 2. CARGAR LAS ELECCIONES DESDE GOOGLE SHEETS ---
try:
    df_elecciones = pd.read_csv(URL_ELECCIONES)
except Exception as e:
    st.error("No se pudo conectar a la pestaña 'elecciones' de Google Sheets. Verifica el enlace compartido.")
    st.stop()

#%%
# --- 3. CÁLCULO DEL RANKING CON DESEMPATE INVISIBLE ---
ranking = []

for index, row in df_elecciones.iterrows():
    nombre_original = str(row['Nombre']).strip()
    nombre_normalizado = normalizar_nombre(nombre_original)
    
    equipos_elegidos = [normalizar_nombre(row[col]) for col in df_elecciones.columns[1:9]]
    
    # Puntos base ganados por los equipos elegidos
    puntos_totales = 0
    for eq in equipos_elegidos:
        puntos_totales += puntos_por_equipo.get(eq, 0)
    
    # 🤫 CRITERIO SECRETO: Si la persona está en la lista de desempate, le sumamos 0.1 de forma interna
    if nombre_normalizado in PERSONAS_DESEMPATE:
        puntos_totales += 0.1
        
    ranking.append({"Nombre": nombre_original, "Puntos": puntos_totales})

# Ordenamos de mayor a menor (aquí los decimales 0.1 hacen que ganen la posición superior)
df_ranking = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False).reset_index(drop=True)
df_ranking.index = df_ranking.index + 1

# 👁️ TRUCO VISUAL: Convertimos la columna a números enteros antes de mostrar la tabla, borrando el .1
df_ranking_visual = df_ranking.copy()
df_ranking_visual["Puntos"] = df_ranking_visual["Puntos"].astype(int)

#%%
# --- INTERFAZ VISUAL ---
st.header("📊 Tabla de Posiciones")
# Formato destacado para las tarjetas superiores (también ocultando el decimal)
col1, col2, col3 = st.columns(3)
if len(df_ranking) > 0 and df_ranking.iloc[0]['Puntos'] > 0:
    with col1: st.metric(label="🥇 1er Lugar", value=df_ranking.iloc[0]['Nombre'], delta=f"{int(df_ranking.iloc[0]['Puntos'])} pts")
if len(df_ranking) > 1 and df_ranking.iloc[1]['Puntos'] > 0:
    with col2: st.metric(label="🥈 2do Lugar", value=df_ranking.iloc[1]['Nombre'], delta=f"{int(df_ranking.iloc[1]['Puntos'])} pts")
if len(df_ranking) > 2 and df_ranking.iloc[2]['Puntos'] > 0:
    with col3: st.metric(label="🥉 3er Lugar", value=df_ranking.iloc[2]['Nombre'], delta=f"{int(df_ranking.iloc[2]['Puntos'])} pts")

# Mostramos la tabla limpia sin decimales
st.dataframe(df_ranking_visual, use_container_width=True)


st.markdown("---")
st.header("📋 Elecciones de los Participantes")
st.dataframe(df_elecciones, use_container_width=True)


















