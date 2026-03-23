import pandas as pd
import os
import hashlib # Para no guardar las contraseñas en texto plano (Seguridad)

# Configuración de rutas
RUTA_USUARIOS = os.path.join(os.path.dirname(__file__), '..', 'datos_usuarios', 'usuarios.csv')

def inicializar_usuarios():
    """Crea el archivo de usuarios si no existe."""
    if not os.path.exists(os.path.dirname(RUTA_USUARIOS)):
        os.makedirs(os.path.dirname(RUTA_USUARIOS))
    
    if not os.path.exists(RUTA_USUARIOS):
        # Columnas: ID, Contraseña (hash), Ciudad, Edad, Alergia Principal
        columnas = ['id_usuario', 'password_hash', 'ciudad', 'edad', 'alergia_principal']
        df = pd.DataFrame(columns=columnas)
        df.to_csv(RUTA_USUARIOS, index=False, sep=';')

def encriptar_password(password):
    """Convierte la contraseña en un código secreto (hash)."""
    return hashlib.sha256(password.encode()).hexdigest()

def registrar_usuario(id_usuario, password, ciudad, edad, tiene_diagnostico, polen_especifico):
    """
    tiene_diagnostico: bool (True si sabe qué alergia tiene, False si no)
    polen_especifico: str (Nombre del polen o 'No diagnosticado')
    """
    inicializar_usuarios()
    df = pd.read_csv(RUTA_USUARIOS, sep=';')
    
    if id_usuario in df['id_usuario'].values:
        return False, "El nombre de usuario ya existe."
    
    nuevo_usuario = {
        'id_usuario': id_usuario,
        'password_hash': encriptar_password(password),
        'ciudad': ciudad,
        'edad': edad,
        'diagnosticado': "Si" if tiene_diagnostico else "No",
        'alergia_principal': polen_especifico if tiene_diagnostico else "No diagnosticado"
    }
    
    df = pd.concat([df, pd.DataFrame([nuevo_usuario])], ignore_index=True)
    df.to_csv(RUTA_USUARIOS, index=False, sep=';')
    return True, "Usuario registrado con éxito."

def validar_login(id_usuario, password):
    """Comprueba si el usuario y la contraseña son correctos."""
    if not os.path.exists(RUTA_USUARIOS):
        return False
    
    df = pd.read_csv(RUTA_USUARIOS, sep=';')
    pass_hash = encriptar_password(password)
    
    # Buscamos al usuario y comprobamos el hash de la contraseña
    usuario_valido = df[(df['id_usuario'] == id_usuario) & (df['password_hash'] == pass_hash)]
    
    return not usuario_valido.empty

def obtener_perfil_usuario(id_usuario):
    """
    Recupera toda la información de un usuario específico.
    Útil para personalizar la interfaz tras el login.
    """
    if not os.path.exists(RUTA_USUARIOS):
        return None
    
    df = pd.read_csv(RUTA_USUARIOS, sep=';')
    
    # Buscamos la fila del usuario
    datos = df[df['id_usuario'] == id_usuario]
    
    if datos.empty:
        return None
    
    # Convertimos la fila en un diccionario para que sea fácil de usar
    perfil = datos.iloc[0].to_dict()
    
    # Limpiamos el hash de la contraseña por seguridad (no lo necesitamos en la interfaz)
    if 'password_hash' in perfil:
        del perfil['password_hash']
        
    return perfil

# --- PRUEBA DEL SISTEMA ---
if __name__ == "__main__":
    # 1. Intentamos registrar a alguien
    exito, msg = registrar_usuario('aitana99', '12345', 'Bilbao', 24, True, 'Gramíneas')
    print(msg)
    
    # 2. Intentamos loguearnos
    if validar_login('aitana99', '12345'):
        print("🔓 Acceso concedido")
    else:
        print("🔒 Contraseña incorrecta")