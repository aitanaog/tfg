import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
import sys
from config import sintomas_polen


ruta_datos = r'datos_procesados\polen_euskadi_final.csv'
carpeta_modelos = 'modelos_entrenados'

if not os.path.exists(carpeta_modelos):
    os.makedirs(carpeta_modelos)

def cargar_y_preparar_datos():
    df = pd.read_csv(ruta_datos, sep=';')
    # 'mixed' le dice a Pandas que si encuentra formatos distintos, intente adivinarlos uno a uno
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='mixed', dayfirst=False) 
    return df

def entrenar_modelos():
    df = cargar_y_preparar_datos()
    ciudades = ['Bilbao', 'Donostia', 'Vitoria']
    especies = list(sintomas_polen.keys())
    
    metricas_finales = []
    
    print(f"--- INICIANDO ENTRENAMIENTO PARA {len(ciudades)} CIUDADES Y {len(especies)} ESPECIES ---")

    for ciudad in ciudades:
        print(f"\n Procesando ciudad: {ciudad}")
        for esp in especies:
            
            df_especie = df[df['Ciudad'] == ciudad][['Fecha', esp]].copy()
            
            # Variables de entrenamiento
            df_especie['dia_año'] = df_especie['Fecha'].dt.dayofyear
            df_especie['lag_1'] = df_especie[esp].shift(1)
            df_especie['lag_2'] = df_especie[esp].shift(2)
            df_especie['media_7d'] = df_especie[esp].shift(1).rolling(window=7).mean()
            
            df_entrenamiento = df_especie.dropna()
            
            # Verificación de datos mínimos para entrenar
            if len(df_entrenamiento) < 60:
                continue
            
            # División Temporal (80% train, 20% test)
            split = int(len(df_entrenamiento) * 0.8)
            train, test = df_entrenamiento.iloc[:split], df_entrenamiento.iloc[split:]
            
            X_train = train[['dia_año', 'lag_1', 'lag_2', 'media_7d']]
            y_train = train[esp]
            X_test = test[['dia_año', 'lag_1', 'lag_2', 'media_7d']]
            y_test = test[esp]
            

            modelo = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
            modelo.fit(X_train, y_train)
            
            # calcular métricas de evaluación
            predicciones = modelo.predict(X_test)
            mae = mean_absolute_error(y_test, predicciones)   #cuántas unidades de polen se equivoca el modelo
            r2 = r2_score(y_test, predicciones)      #cuán bien captura los patrones
            

            metricas_finales.append({
                'Ciudad': ciudad,
                'Especie': esp,
                'MAE (Error Medio)': round(mae, 2),
                'R2 (Precisión %)': round(r2, 2)
            })
            
            # GUARDAR MODELO (.pkl)
            nombre_modelo = f"modelo_{ciudad}_{esp.replace('/', '_')}.pkl"
            ruta_guardado = os.path.join(carpeta_modelos, nombre_modelo)
            
            # compress=3 para que los pkl ocupen menos
            joblib.dump(modelo, ruta_guardado, compress=3)
            

    df_resultados = pd.DataFrame(metricas_finales)
    df_resultados.to_csv('metricas_modelos.csv', index=False, sep=';', encoding='utf-8-sig')

    print("PROCESO COMPLETADO")
    print(f"Modelos guardados en: {carpeta_modelos}")
    print("Archivo 'metricas_modelos.csv' generado para tu memoria.")

if __name__ == "__main__":
    entrenar_modelos()