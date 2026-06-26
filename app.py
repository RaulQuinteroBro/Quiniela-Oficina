
#%%

import streamlit as st
import pandas as pd
import requests
#%%

# Configuración de la página web
st.set_page_config(page_title="Quiniela Mundialista Oficina", layout="wide")

st.title("🏆 App Web del Mundial")
st.write("Suerte amigos :3")
#%%
# --- CONFIGURACIÓN DE LA API ---
# --- DICCIONARIO TRADUCTOR (Para que el sistema entienda Español/Inglés y acentos) ---
def normalizar_nombre(nombre_equipo):
    nombre_equipo = str(nombre_equipo).strip().lower()
    # Quitar acentos comunes por si escriben México o España
    reemplazos = {"é": "e", "á": "a", "í": "i", "ó": "o", "ú": "u"}
    for original, reemplazo in reemplazos.items():
        nombre_equipo = nombre_equipo.replace(original, reemplazo)
    return nombre_equipo


# --- PANEL DE ADMINISTRACIÓN EN LA BARRA LATERAL ---
st.sidebar.header("⚙️ Panel de Administración (No Tocar)")
st.sidebar.write("Selecciona los equipos que vayan clasificando en cada fase:")

# Cargar el Excel primero para saber qué equipos existen
try:
    df_elecciones = pd.read_excel("Quiniela.xlsx")
    
    # Extraemos todos los equipos únicos que la gente escribió en el Excel para que no tengas que escribirlos tú
    todos_los_equipos = set()
    for col in df_elecciones.columns[1:9]:
        for eq in df_elecciones[col].dropna():
            todos_los_equipos.add(str(eq).strip())
    lista_equipos_ordenada = sorted(list(todos_los_equipos))
except Exception as e:
    st.error("No se pudo cargar 'Quiniela.xlsx'. Asegúrate de que esté en la misma carpeta.")
    st.stop()

# Selectores múltiples en la barra lateral para el Administrador
dieciseisavos = st.sidebar.multiselect("⚽ Clasificados a Dieciseisavos de Final (1 pt)", lista_equipos_ordenada)
octavos = st.sidebar.multiselect("⭐ Clasificados a Octavos de Final (2 pts)", lista_equipos_ordenada)
cuartos = st.sidebar.multiselect("🔥 Clasificados a Cuarto de Final (3 pts)", lista_equipos_ordenada)
semis = st.sidebar.multiselect("👑 Clasificados a la Seminifla Final (4 pts)", lista_equipos_ordenada)
finalistas = st.sidebar.multiselect("👑 Clasificados a la Gran Final (5 pts)", lista_equipos_ordenada)


# --- PROCESAMIENTO DE PUNTOS MANUALES ---
puntos_por_equipo = {}

# Asignar puntos acumulados (Si llegó a la final tiene 4, si llegó a semis tiene 3, etc.)
for eq in dieciseisavos:
    puntos_por_equipo[normalizar_nombre(eq)] = 1
for eq in octavos:
    puntos_por_equipo[normalizar_nombre(eq)] = 2
for eq in cuartos:
    puntos_por_equipo[normalizar_nombre(eq)] = 3
for eq in semis:
    puntos_por_equipo[normalizar_nombre(eq)] = 4
for eq in finalistas:
    puntos_por_equipo[normalizar_nombre(eq)] = 5

# --- CÁLCULO DEL RANKING EN TIEMPO REAL ---
ranking = []

for index, row in df_elecciones.iterrows():
    nombre = row['Nombre']
    # Tomamos las 8 elecciones de la persona
    equipos_elegidos = [normalizar_nombre(row[col]) for col in df_elecciones.columns[1:9]]
    
    puntos_totales = 0
    for eq in equipos_elegidos:
        # Suma los puntos si el equipo tiene un valor asignado por el administrador
        puntos_totales += puntos_por_equipo.get(eq, 0)
        
    ranking.append({"Nombre": nombre, "Puntos": puntos_totales})

# Ordenar el ranking de mayor a menor
df_ranking = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False).reset_index(drop=True)
#%%
# Cambiar el índice para que empiece en 1 en lugar de 0
df_ranking.index = df_ranking.index + 1
#%%
# --- INTERFAZ VISUAL PRINCIPAL ---

# Formato destacado para los 3 primeros lugares
st.header("📊 Tabla de Posiciones (Ranking Live)")
col1, col2, col3 = st.columns(3)
if len(df_ranking) > 0 and df_ranking.iloc[0]['Puntos'] > 0:
    with col1:
        st.metric(label="🥇 1er Lugar", value=df_ranking.iloc[0]['Nombre'], delta=f"{df_ranking.iloc[0]['Puntos']} pts")
if len(df_ranking) > 1 and df_ranking.iloc[1]['Puntos'] > 0:
    with col2:
        st.metric(label="🥈 2do Lugar", value=df_ranking.iloc[1]['Nombre'], delta=f"{df_ranking.iloc[1]['Puntos']} pts")
if len(df_ranking) > 2 and df_ranking.iloc[2]['Puntos'] > 0:
    with col3:
        st.metric(label="🥉 3er Lugar", value=df_ranking.iloc[2]['Nombre'], delta=f"{df_ranking.iloc[2]['Puntos']} pts")

# Mostrar la tabla de posiciones completa
st.dataframe(df_ranking, use_container_width=True)

st.markdown("---")

# Mostrar el Excel original
st.header("📋 Elecciones de los Participantes")
st.dataframe(df_elecciones, use_container_width=True)




