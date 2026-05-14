import pandas as pd
from scripts.config import umbrales_polen

def obtener_color_alerta(especie, valor):
    if valor is None or pd.isna(valor):
        return "Bajo", "#28a745"

    # Buscamos la especie (en minúsculas para evitar errores)
    umbrales_min = {k.lower(): v for k, v in umbrales_polen.items()}
    reglas = umbrales_min.get(especie.lower(), {'bajo': 15, 'moderado': 80})

    # Lógica de dos umbrales:
    if valor >= reglas['moderado']:
        return "Alto", "#dc3545"      # Rojo
    elif valor >= reglas['bajo']:
        return "Moderado", "#ffc107"  # Amarillo
    else:
        return "Bajo", "#28a745"      # Verde

def calcular_indice_global(datos_ciudad):

    riesgos = []
    for especie, valor in datos_ciudad.items():
        if especie in umbrales_polen:
            nivel, _ = obtener_color_alerta(especie, valor)
            riesgos.append(nivel)
    
    if "Alto" in riesgos:
        return "Alerta Roja"
    elif "Moderado" in riesgos:
        return "Alerta Amarilla"
    return "Nivel Verde"