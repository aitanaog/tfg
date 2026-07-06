import pandas as pd
import datetime
import joblib
import os
from scripts.config import sintomas_polen

carpeta_modelos = 'modelos_entrenados'

def predecir_siguientes_dias(ciudad):
    ruta_csv = 'datos_procesados/polen_euskadi_final.csv'
    df = pd.read_csv(ruta_csv, sep=';')
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    # Filtramos los datos de la ciudad y ordenamos
    df_ciudad = df[df['Ciudad'] == ciudad].sort_values('Fecha')
    especies = list(sintomas_polen.keys())
    
    hoy = datetime.date.today()
    mañana = hoy + datetime.timedelta(days=1)
    
    # Creamos un diccionario para la nueva fila de predicción
    nueva_fila_hoy = {'Fecha': hoy, 'Ciudad': ciudad}
    nueva_fila_mañana = {'Fecha': mañana, 'Ciudad': ciudad}

    for esp in especies:
        
        nombre_modelo = f"modelo_{ciudad}_{esp.replace('/', '_')}.pkl"
        ruta_modelo = os.path.join(carpeta_modelos, nombre_modelo)
        
        if os.path.exists(ruta_modelo):
            modelo = joblib.load(ruta_modelo)
            
            # Obtenemos: dia_año, lag_1, lag_2, media_7d
            ultimos_datos = df_ciudad[esp].tail(10).tolist()
            
            if len(ultimos_datos) >= 7:
                dia_año = hoy.timetuple().tm_yday
                lag_1 = ultimos_datos[-1] 
                lag_2 = ultimos_datos[-2]
                media_7 = sum(ultimos_datos[-7:]) / 7
                
                # Predicción para HOY
                X_hoy = pd.DataFrame([[dia_año, lag_1, lag_2, media_7]], 
                                    columns=['dia_año', 'lag_1', 'lag_2', 'media_7d'])
                pred_hoy = modelo.predict(X_hoy)[0]
                
                # Predicción para MAÑANA (usando la pred de hoy como lag_1)
                X_mañana = pd.DataFrame([[dia_año + 1, pred_hoy, lag_1, media_7]], 
                                        columns=['dia_año', 'lag_1', 'lag_2', 'media_7d'])
                pred_mañana = modelo.predict(X_mañana)[0]
                
                nueva_fila_hoy[esp] = round(pred_hoy, 2)
                nueva_fila_mañana[esp] = round(pred_mañana, 2)
        else:
            nueva_fila_hoy[esp] = 0.0
            nueva_fila_mañana[esp] = 0.0

    df_preds = pd.DataFrame([nueva_fila_hoy, nueva_fila_mañana])
    
    df_final = pd.concat([df, df_preds]).drop_duplicates(subset=['Fecha', 'Ciudad'], keep='last')
    df_final.to_csv(ruta_csv, index=False, sep=';')
    print(f" Predicciones integradas para {ciudad}")