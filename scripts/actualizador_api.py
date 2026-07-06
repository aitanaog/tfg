import requests
import pandas as pd
import os
import sys
from datetime import datetime, timedelta


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.config import municipios, mapeo_especies


ruta_csv = os.path.join(os.path.dirname(__file__), '..', 'datos_procesados', 'polen_euskadi_final.csv')

def actualizar_desde_api():
    """
    Descarga los últimos 15 días de datos de polen desde la API de 
    Open Data Euskadi para cada municipio configurado, y actualiza
    el CSV histórico sustituyendo las fechas que se solapen con
    los datos nuevos descargados.
    """
    
    print("Iniciando sincronización con Open Data Euskadi...")
    
    ### 1. CONSULTA DE LOS ÚLTIMOS 15 DÍAS  ###
    
    hoy = datetime.now()
    fecha_inicio_dt = hoy - timedelta(days=15)
    
    fecha_inicio = fecha_inicio_dt.strftime('%Y-%m-%d')
    fecha_fin = hoy.strftime('%Y-%m-%d')
    
    print(f" Ventana de actualización: del {fecha_inicio} al {fecha_fin}")

    # Leer el CSV actual
    if not os.path.exists(ruta_csv):
        print(f" Error: No se encuentra el archivo en {ruta_csv}")
        return

    df_actual = pd.read_csv(ruta_csv, sep=';')
    df_actual['Fecha'] = pd.to_datetime(df_actual['Fecha'], errors='coerce')        # Se convierte la columna 'Fecha' del CSV a formato fecha para poder operar con ella.

    nuevos_registros = []
    errores_ciudades = []
    
    # Bucle de descarga por ciudad (Bilbao, Donostia, Vitoria)
    for ciudad, m_id in municipios.items():
        print(f" Solicitando datos de {ciudad}...")
        url = f"https://api.euskadi.eus/pollen-quality/measurements/municipalities/{m_id}/from/{fecha_inicio}/to/{fecha_fin}"
        
        ### 2. PROCESAMIENTO DE LA RESPUESTA ###
        try:
            response = requests.get(url, timeout=25)
            if response.status_code == 200:
                mediciones_json = response.json()
                
                temp_dict = {}
                
                # Recorre los días que ha devuelto la API.
                for dia_obj in mediciones_json:
                    fecha_str = dia_obj.get('date')
                    lista_mediciones = dia_obj.get('measurements', [])      # Extrae la lista de mediciones de polen.
                    
                    if not fecha_str:
                        continue
                    
                    if fecha_str not in temp_dict:
                        temp_dict[fecha_str] = {'Fecha': fecha_str, 'Ciudad': ciudad}
                    
                    # Recorremos la sub-lista de plantas de cada día
                    for m in lista_mediciones:
                        esp_id = m.get('specieId')
                        valor = m.get('pollenCount', 0)
                        
                        # Buscamos el nombre de la columna en el config.py
                        columna = mapeo_especies.get(str(esp_id).lower())
                        if columna:
                            temp_dict[fecha_str][columna] = valor
                
                # Pasa los datos del diccionario a la lista general de nuevos registros.
                nuevos_registros.extend(list(temp_dict.values()))
                
            else:
                print(f" Error API en {ciudad}: {response.status_code}")
                errores_ciudades.append(ciudad)
        except Exception as e:
            print(f" Fallo de conexión en {ciudad}: {e}")
            errores_ciudades.append(ciudad)



    if nuevos_registros:
        df_nuevos = pd.DataFrame(nuevos_registros)
        df_nuevos['Fecha'] = pd.to_datetime(df_nuevos['Fecha'])
        
        ### 3. ACTUALIZACIÓN DEL HISTÓRICO ###
        print(" Borrando datos antiguos/vacíos para reescribir con datos actualizados...")
        
        fechas_nuevas = df_nuevos['Fecha'].unique()
        df_actual = df_actual[~df_actual['Fecha'].isin(fechas_nuevas)]              # Filtra el CSV antiguo para BORRAR las filas cuyas fechas coincidan con las nuevas.
        
        #Se une lo viejo con lo nuevo
        df_final = pd.concat([df_actual, df_nuevos], sort=False)
        
        ### 4. INTEGRACIÓN Y LIMPIEZA ###
        
        df_final = df_final.sort_values(['Fecha', 'Ciudad'])
        
        # Rellenar con 0.0 las columnas que tengan valores NaN
        columnas_polen = df_final.columns.difference(['Fecha', 'Ciudad'])
        df_final[columnas_polen] = df_final[columnas_polen].fillna(0.0)

        # Borrar cualquier fila que se haya quedado sin fecha antes de guardar
        df_final = df_final.dropna(subset=['Fecha'])
        
        # Guardar cambios
        df_final.to_csv(ruta_csv, sep=';', index=False)
        
        print(f"¡Sincronización exitosa! Se han actualizado {len(df_nuevos)} registros.")
    else:
        print("No se han encontrado datos nuevos en la API.")
        
    
    return errores_ciudades  # lista vacía = todo ok


if __name__ == "__main__":
    actualizar_desde_api()