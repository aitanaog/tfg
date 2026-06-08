import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
import sys

# 1. IMPORTACIÓN DE CONFIGURACIÓN
from config import sintomas_polen

# 2. CONFIGURACIÓN DE RUTAS
ruta_datos = r'datos_procesados\polen_euskadi_final.csv'
carpeta_modelos = 'modelos_entrenados'

if not os.path.exists(carpeta_modelos):
    os.makedirs(carpeta_modelos)

def cargar_y_preparar_datos():
    df = pd.read_csv(ruta_datos, sep=';')
    # 'mixed' le dice a Pandas que si encuentra formatos distintos, intente adivinarlos uno a uno
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='mixed', dayfirst=False) 
    return df

def entrenar_sistema_global():
    df = cargar_y_preparar_datos()
    ciudades = ['Bilbao', 'Donostia', 'Vitoria']
    especies = list(sintomas_polen.keys())
    
    metricas_finales = []
    
    print(f"--- INICIANDO ENTRENAMIENTO PARA {len(ciudades)} CIUDADES Y {len(especies)} ESPECIES ---")

    for ciudad in ciudades:
        print(f"\n Procesando ciudad: {ciudad}")
        for esp in especies:
            # Filtrado y limpieza por ciudad/especie
            df_esp = df[df['Ciudad'] == ciudad][['Fecha', esp]].copy()
            
            # Feature Engineering (Lags y Medias Móviles)
            df_esp['dia_año'] = df_esp['Fecha'].dt.dayofyear
            df_esp['lag_1'] = df_esp[esp].shift(1)
            df_esp['lag_2'] = df_esp[esp].shift(2)
            df_esp['media_7d'] = df_esp[esp].shift(1).rolling(window=7).mean()
            
            df_ml = df_esp.dropna()
            
            # Verificación de datos mínimos para entrenar
            if len(df_ml) < 60:
                continue
            
            # División Temporal (80% train, 20% test)
            split = int(len(df_ml) * 0.8)
            train, test = df_ml.iloc[:split], df_ml.iloc[split:]
            
            X_train = train[['dia_año', 'lag_1', 'lag_2', 'media_7d']]
            y_train = train[esp]
            X_test = test[['dia_año', 'lag_1', 'lag_2', 'media_7d']]
            y_test = test[esp]
            
            # ENTRENAMIENTO
            modelo = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
            modelo.fit(X_train, y_train)
            
            # EVALUACIÓN
            predicciones = modelo.predict(X_test)
            mae = mean_absolute_error(y_test, predicciones)
            r2 = r2_score(y_test, predicciones)
            
            # GUARDAR MÉTRICAS
            metricas_finales.append({
                'Ciudad': ciudad,
                'Especie': esp,
                'MAE (Error Medio)': round(mae, 2),
                'R2 (Precisión %)': round(r2, 2)
            })
            
            # GUARDAR MODELO (.pkl)
            nombre_file = f"modelo_{ciudad}_{esp.replace('/', '_')}.pkl"
            ruta_guardado = os.path.join(carpeta_modelos, nombre_file)
            
            # compress=3 es el estándar, puedes subir hasta 9 si siguen siendo grandes
            joblib.dump(modelo, ruta_guardado, compress=3)
            
    # Exportar métricas a CSV para la memoria del TFG
    df_resultados = pd.DataFrame(metricas_finales)
    df_resultados.to_csv('metricas_modelos.csv', index=False, sep=';', encoding='utf-8-sig')
    print("\n" + "="*40)
    print("✅ PROCESO COMPLETADO")
    print(f"Modelos guardados en: {carpeta_modelos}")
    print("Archivo 'metricas_modelos.csv' generado para tu memoria.")
    print("="*40)

if __name__ == "__main__":
    entrenar_sistema_global()