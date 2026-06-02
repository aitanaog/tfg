import pandas as pd
import os

RUTA_SINTOMAS = os.path.join(os.path.dirname(__file__), '..', 'datos_usuarios', 'registro_sintomas.csv')

SINTOMAS_LISTA = [
    'estornudos', 
    'rinitis', 
    'conjuntivitis', 
    'picor_garganta', 
    'tos', 
    'asma', 
    'dolor_cabeza', 
    'picor_nasal', 
    'opresion_toracica', 
    'erupcion', 
    'mucosidad'
]

def inicializar_diario():
    """Crea la carpeta y el CSV con las columnas oficiales si no existen."""
    if not os.path.exists(os.path.dirname(RUTA_SINTOMAS)):
        os.makedirs(os.path.dirname(RUTA_SINTOMAS))
    
    if not os.path.exists(RUTA_SINTOMAS):
        columnas = ['id_usuario', 'fecha', 'malestar'] + SINTOMAS_LISTA + ['medicacion', 'comentarios']
        df = pd.DataFrame(columns=columnas)
        df.to_csv(RUTA_SINTOMAS, index=False, sep=';', encoding='utf-8-sig')

def registrar_entrada_salud(id_usuario, fecha, nivel, sintomas_activos, medicacion="No", comentarios=""):
    """
    Registra el diario de síntomas en el CSV original. Si ya existe un registro 
    del mismo día para el mismo usuario, lo sobreescribe automáticamente.
    """
    try:
        inicializar_diario()
        
        nueva_fila = {
            'id_usuario': id_usuario,
            'fecha': fecha,
            'malestar': int(nivel),
            'medicacion': medicacion,
            'comentarios': comentarios
        }
        
        for s in SINTOMAS_LISTA:
            sintomas_activos_lower = [x.lower() for x in sintomas_activos]
            nueva_fila[s] = True if s.lower() in sintomas_activos_lower else False
        
        df_nuevo = pd.DataFrame([nueva_fila])
        
        df_hist = pd.read_csv(RUTA_SINTOMAS, sep=';')
        
        # Comprobar si ya se había enviado un reporte hoy para este usuario
        registro_previo = df_hist[(df_hist['id_usuario'] == id_usuario) & (df_hist['fecha'] == fecha)]
        ya_existia = not registro_previo.empty
        
        # Sobreescritura: Eliminamos del histórico el registro viejo de la fecha actual si existía
        df_hist = df_hist[~((df_hist['id_usuario'] == id_usuario) & (df_hist['fecha'] == fecha))]
        
        # Consolidación final y guardado en el fichero CSV original
        df_final = pd.concat([df_hist, df_nuevo], ignore_index=True)
        df_final.to_csv(RUTA_SINTOMAS, index=False, sep=';', encoding='utf-8-sig')
        
        if ya_existia:
            return True, "🔄 Tu registro de hoy ha sido actualizado."
        else:
            return True, "✅ Diario guardado con éxito por primera vez hoy."
            
    except Exception as e:
        return False, f"Error interno al guardar en el diario: {str(e)}"

# Ejemplo
if __name__ == "__main__":
    # El usuario marcó picor de ojos y estornudos
    mis_sintomas_de_hoy = ['Irritacion_ocular', 'Estornudos']
    registrar_entrada_salud('aitana_test', '2026-03-12', 'Bilbao', 7, mis_sintomas_de_hoy, "Hoy me duele un poco la cabeza")