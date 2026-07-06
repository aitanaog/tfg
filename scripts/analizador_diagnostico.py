import pandas as pd
import numpy as np
from scripts.config import sintomas_polen # Importamos tu diccionario médico

def generar_sugerencia_diagnostico(id_usuario, ciudad):
    try:
        ### 1. CARGA DE DATOS ###
        df_sintomas = pd.read_csv('datos_usuarios/registro_sintomas.csv', sep=';')
        df_polen = pd.read_csv('datos_procesados/polen_euskadi_final.csv', sep=';')
        
        
        ### 2. FILTRADO POR USUARIO Y CIUDAD ###
        # Limpieza de fechas para que coincidan
        df_sintomas['fecha'] = pd.to_datetime(df_sintomas['fecha']).dt.date
        df_polen['Fecha'] = pd.to_datetime(df_polen['Fecha'], format='mixed').dt.date
        polen_ciudad = df_polen[df_polen['Ciudad'] == ciudad]
        
        user_data = df_sintomas[df_sintomas['id_usuario'] == id_usuario].copy()
        if len(user_data) < 30:
            return "Insuficiente", "Se requieren al menos 30 días de registros para un análisis fiable."

        ### 3 . CRUCE TEMPORAL ###

        merged = pd.merge(user_data, polen_ciudad, left_on='fecha', right_on='Fecha')

        # columnas de polen 
        columnas_polen = [c for c in df_polen.columns if c not in ['Fecha', 'Ciudad', 'Año', 'Anio', 'Mes', 'Dia', 'Unnamed: 0']]
        
        puntuaciones_finales = {}
        detalles_diagnostico = {}

        for p in columnas_polen:
            ### 4. CÁLCULO DE PEARSON (Peso: 60%) ###
            # Se mide si el nivel de 'malestar' (0-10) sigue la curva del polen
            corr_base = merged['malestar'].corr(merged[p])
            if np.isnan(corr_base) or corr_base < 0: corr_base = 0

            ### 5. VALIDACIÓN CLÍNICA (Peso: 40%) ###
            # Miramos si los síntomas marcados como True coinciden con el diccionario
            sintomas_tipicos = sintomas_polen.get(p, [])
            puntos_sintomas = 0
            sintomas_detectados = []

            for s in sintomas_tipicos:
                if s in merged.columns:
                    # Calculamos el porcentaje de días que tuvo ese síntoma
                    frecuencia = merged[s].mean() # Al ser booleano (True/False), la media es la frecuencia
                    if frecuencia > 0.3: # Si aparece en más del 30% de los días registrados
                        puntos_sintomas += 0.2 
                        sintomas_detectados.append(s)

            # Cálculo de la fuerza final (Normalizado)
            fuerza_total = (corr_base * 0.6) + (min(puntos_sintomas, 0.4))
            
            puntuaciones_finales[p] = fuerza_total
            detalles_diagnostico[p] = sintomas_detectados

        # RESULTADO FINAL
        if not puntuaciones_finales or max(puntuaciones_finales.values()) == 0:
            return "Indeterminado", "No hay una relación clara. Prueba a registrar más días de síntomas."

        # Elegimos el polen con mayor puntuación combinada
        culpable = max(puntuaciones_finales, key=puntuaciones_finales.get)
        confianza = puntuaciones_finales[culpable]
        lista_s = ", ".join(detalles_diagnostico[culpable])

        # 5. MENSAJE PERSONALIZADO
        if confianza > 0.6:
            msg = f"Probabilidad Alta. Tus picos de malestar y la presencia de {lista_s} coinciden estrechamente con los niveles de {culpable}."
        elif confianza > 0.3:
            msg = f"Probabilidad Media. Hay indicios de que {culpable} afecta a tu salud, coincidiendo con síntomas de {lista_s}."
        else:
            msg = "Tendencia leve. Se detecta una ligera coincidencia, pero los datos no son concluyentes todavía."

        return culpable, msg

    except Exception as e:
        return "Error", f"Error en el motor analítico: {str(e)}"