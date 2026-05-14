import requests
import pandas as pd
import os
import sys
from datetime import datetime, timedelta

# 1. Configuración de rutas
# Añadimos la raíz al path para poder importar el archivo config.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.config import municipios, mapeo_especies

# Ruta al CSV histórico
ruta_csv = os.path.join(os.path.dirname(__file__), '..', 'datos_procesados', 'polen_euskadi_final.csv')

def actualizar_desde_api():
    print("Iniciando sincronización con Open Data Euskadi...")
    
    # 2. ventana de tiempo = últimos 15 días
    hoy = datetime.now()
    fecha_inicio_dt = hoy - timedelta(days=90)
    
    fecha_inicio = fecha_inicio_dt.strftime('%Y-%m-%d')
    fecha_fin = hoy.strftime('%Y-%m-%d')
    
    print(f" Ventana de actualización: del {fecha_inicio} al {fecha_fin}")

    # 3. Leer el CSV actual
    if not os.path.exists(ruta_csv):
        print(f"❌ Error: No se encuentra el archivo en {ruta_csv}")
        return

    df_actual = pd.read_csv(ruta_csv, sep=';')
    # Convertimos la columna Fecha a datetime para poder comparar
    df_actual['Fecha'] = pd.to_datetime(df_actual['Fecha'], errors='coerce')

    nuevos_registros = []

    # 4. Bucle de descarga por ciudad (Bilbao, Donostia, Vitoria)
    for ciudad, m_id in municipios.items():
        print(f" Solicitando datos de {ciudad}...")
        url = f"https://api.euskadi.eus/pollen-quality/measurements/municipalities/{m_id}/from/{fecha_inicio}/to/{fecha_fin}"
        
        try:
            response = requests.get(url, timeout=25)
            if response.status_code == 200:
                mediciones_json = response.json()
                
                temp_dict = {}
                for dia_obj in mediciones_json:
                    fecha_str = dia_obj.get('date')
                    lista_mediciones = dia_obj.get('measurements', [])
                    
                    if not fecha_str:
                        continue
                    
                    if fecha_str not in temp_dict:
                        temp_dict[fecha_str] = {'Fecha': fecha_str, 'Ciudad': ciudad}
                    
                    # Recorremos la sub-lista de plantas de cada día
                    for m in lista_mediciones:
                        esp_id = m.get('specieId')
                        valor = m.get('pollenCount', 0)
                        
                        # Buscamos el nombre de tu columna en el config.py
                        columna = mapeo_especies.get(str(esp_id).lower())
                        if columna:
                            temp_dict[fecha_str][columna] = valor
                
                # Añadimos los días procesados de esta ciudad a la lista general
                nuevos_registros.extend(list(temp_dict.values()))
                
            else:
                print(f"⚠️ Error API en {ciudad}: {response.status_code}")
        except Exception as e:
            print(f"❌ Fallo de conexión en {ciudad}: {e}")

    # 5. Integración y Limpieza
    if nuevos_registros:
        df_nuevos = pd.DataFrame(nuevos_registros)
        df_nuevos['Fecha'] = pd.to_datetime(df_nuevos['Fecha'])
        
        # Borramos las filas viejas del CSV que coincidan con las fechas que acabamos de descargar
        print(" Borrando datos antiguos/vacíos para reescribir con datos reales...")
        fechas_nuevas = df_nuevos['Fecha'].unique()
        df_actual = df_actual[~df_actual['Fecha'].isin(fechas_nuevas)]
        
        # Unimos lo viejo con lo nuevo
        df_final = pd.concat([df_actual, df_nuevos], sort=False)
        
        # Ordenamos por fecha y ciudad para que el CSV no sea un caos
        df_final = df_final.sort_values(['Fecha', 'Ciudad'])
        
        # Rellenar con 0.0 SOLO las columnas de polen (numéricas), no la Fecha ni la Ciudad
        columnas_polen = df_final.columns.difference(['Fecha', 'Ciudad'])
        df_final[columnas_polen] = df_final[columnas_polen].fillna(0.0)

        # Y por seguridad, borrar cualquier fila que se haya quedado sin fecha antes de guardar
        df_final = df_final.dropna(subset=['Fecha'])
        
        # Guardar cambios
        df_final.to_csv(ruta_csv, sep=';', index=False)
        
        print(f"¡Sincronización exitosa! Se han actualizado {len(df_nuevos)} registros.")
    else:
        print("No se han encontrado datos nuevos en la API.")

if __name__ == "__main__":
    actualizar_desde_api()