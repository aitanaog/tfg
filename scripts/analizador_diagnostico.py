import pandas as pd
import numpy as np

def generar_sugerencia_diagnostico(id_usuario, ciudad):
    try:
        # 1. Cargar datos
        df_sintomas = pd.read_csv('datos_usuarios/registro_sintomas.csv', sep=';')
        df_polen = pd.read_csv('datos_procesados/polen_euskadi_final.csv', sep=';')
        
        # Limpiar fechas
        df_sintomas['fecha'] = pd.to_datetime(df_sintomas['fecha']).dt.date
        df_polen['Fecha'] = pd.to_datetime(df_polen['Fecha'], format='mixed').dt.date
        
        # 2. Filtrar por usuario y últimos 30 días
        user_data = df_sintomas[df_sintomas['id_usuario'] == id_usuario].copy()
        if len(user_data) < 7: # Mínimo una semana de datos para que sea serio
            return "Insuficiente", "Necesitamos al menos 7 días de registros para analizar tendencias."

        # 3. Cruzar con datos de polen de la ciudad
        polen_ciudad = df_polen[df_polen['Ciudad'] == ciudad]
        merged = pd.merge(user_data, polen_ciudad, left_on='fecha', right_on='Fecha')

        # 4. Cálculo de Correlación
        # Buscamos qué polen tiene mayor correlación con el nivel de 'malestar'
        columnas_polen = df_polen.columns.difference(['Fecha', 'Ciudad', 'Año', 'Mes', 'Dia', 'Unnamed: 0'])
        correlaciones = {}
        
        for p in columnas_polen:
            # Calculamos la correlación de Pearson entre el polen y el malestar
            correlacion = merged['malestar'].corr(merged[p])
            if not np.isnan(correlacion):
                correlaciones[p] = correlacion

        # 5. Obtener el culpable principal
        if not correlaciones:
            return "Indeterminado", "No se encontró una relación clara entre los pólenes actuales y tus síntomas."
            
        culpable = max(correlaciones, key=correlaciones.get)
        fuerza = correlaciones[culpable]

        if fuerza > 0.5:
            mensaje = f"Existe una correlación fuerte ({fuerza:.2f}) entre tus picos de malestar y los niveles de {culpable}."
            return culpable, mensaje
        else:
            return "Tendencia leve", f"Parece que el {culpable} coincide con tus síntomas, pero la relación es débil."

    except Exception as e:
        return "Error", str(e)