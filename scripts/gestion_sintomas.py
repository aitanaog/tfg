import pandas as pd
import os

# Configuración de rutas
RUTA_SINTOMAS = os.path.join(os.path.dirname(__file__), '..', 'datos_usuarios', 'registro_sintomas.csv')

# Diccionario oficial de síntomas para tu TFG
SINTOMAS_LISTA = [
    'Conjuntivitis', 
    'Estornudos', 
    'Rinitis', 
    'Asma',
    'Picor_Garganta', 
    'Tos', 
    'Dolor_de_cabeza',
    'Opresión_torácica',
    'Picor_nasal',
    'Erupción',
    'Irritacion_ocular',
    'Mucosidad'
]

def inicializar_diario():
    """Crea la carpeta y el CSV con las columnas necesarias si no existen."""
    if not os.path.exists(os.path.dirname(RUTA_SINTOMAS)):
        os.makedirs(os.path.dirname(RUTA_SINTOMAS))
    
    if not os.path.exists(RUTA_SINTOMAS):
        # Creamos la cabecera: Usuario, Fecha, Nivel y luego todos los síntomas como columnas
        columnas = ['ID_Usuario', 'Fecha', 'Ciudad', 'Nivel_Malestar'] + SINTOMAS_LISTA + ['Notas']
        df = pd.DataFrame(columns=columnas)
        df.to_csv(RUTA_SINTOMAS, index=False, sep=';')

def registrar_entrada_salud(id_usuario, fecha, ciudad, nivel, sintomas_activos, notas=""):

    inicializar_diario()
    
    # Creamos un diccionario para la nueva fila
    nueva_fila = {
        'ID_Usuario': id_usuario,
        'Fecha': fecha,
        'Ciudad': ciudad,
        'Nivel_Malestar': nivel,
        'Notas': notas
    }
    
    # Ponemos 1 si el síntoma se marcó, 0 si no
    for s in SINTOMAS_LISTA:
        nueva_fila[s] = True if s in sintomas_activos else False
    
    df_nuevo = pd.DataFrame([nueva_fila])
    
    # Leer histórico y gestionar duplicados (si el usuario actualiza su estado del mismo día)
    df_hist = pd.read_csv(RUTA_SINTOMAS, sep=';')
    
    # Borrar si ya existía una entrada para ESE usuario en ESA fecha
    df_hist = df_hist[~((df_hist['ID_Usuario'] == id_usuario) & (df_hist['Fecha'] == fecha))]
    
    # Unir y guardar
    df_final = pd.concat([df_hist, df_nuevo], ignore_index=True)
    df_final.to_csv(RUTA_SINTOMAS, index=False, sep=';')
    print(f"✅ Diario actualizado para el usuario {id_usuario}")

# Ejemplo
if __name__ == "__main__":
    # El usuario marcó picor de ojos y estornudos
    mis_sintomas_de_hoy = ['Irritacion_ocular', 'Estornudos']
    registrar_entrada_salud('aitana_test', '2026-03-12', 'Bilbao', 7, mis_sintomas_de_hoy, "Hoy me duele un poco la cabeza")