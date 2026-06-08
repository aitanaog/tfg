import pandas as pd
import os
import hashlib # Para no guardar las contraseñas en texto plano (Seguridad)

# Configuración de rutas
ruta_usuarios = os.path.join(os.path.dirname(__file__), '..', 'datos_usuarios', 'usuarios.csv')

def inicializar_usuarios():
    """Crea el archivo de usuarios si no existe."""
    if not os.path.exists(os.path.dirname(ruta_usuarios)):
        os.makedirs(os.path.dirname(ruta_usuarios))
    
    if not os.path.exists(ruta_usuarios):
        # Columnas: ID, Contraseña (hash), Ciudad, Edad, Alergia Principal
        columnas = ['id_usuario', 'password_hash', 'ciudad', 'edad', 'alergia_principal']
        df = pd.DataFrame(columns=columnas)
        df.to_csv(ruta_usuarios, index=False, sep=';')

def encriptar_password(password):
    """Convierte la contraseña en un código secreto (hash)."""
    return hashlib.sha256(password.encode()).hexdigest()

def registrar_usuario(id_usuario, password, ciudad, edad, tiene_diagnostico, polen_especifico):
    """
    tiene_diagnostico: bool (True si sabe qué alergia tiene, False si no)
    polen_especifico: str (Nombre del polen o 'No diagnosticado')
    """
    if not str(id_usuario).strip():
        return False, "Error: El usuario no puede estar vacío."
    if not str(password).strip():
        return False, "Error: La contraseña no puede estar vacía."
    if ciudad == "Seleccione una ciudad..." or not str(ciudad).strip():
        return False, "Error: Debe proporcionar una ciudad válida."
    if int(edad) <= 0:
        return False, "Error: La edad debe ser un número entero mayor que 0."
    if tiene_diagnostico and polen_especifico == "Seleccione su alergia principal...":
        return False, "Error: Debe especificar su alergia si está diagnosticado."
        
    inicializar_usuarios()
    df = pd.read_csv(ruta_usuarios, sep=';')
    
    if id_usuario in df['id_usuario'].values:
        return False, "El nombre de usuario ya existe."
    
    nuevo_usuario = {
        'id_usuario': id_usuario,
        'password_hash': encriptar_password(password),
        'ciudad': ciudad,
        'edad': int(edad),
        'diagnosticado': "Si" if tiene_diagnostico else "No",
        'alergia_principal': polen_especifico if tiene_diagnostico else "No diagnosticado"
    }
    
    df = pd.concat([df, pd.DataFrame([nuevo_usuario])], ignore_index=True)
    df.to_csv(ruta_usuarios, index=False, sep=';')
    return True, "Usuario registrado con éxito."

def validar_login(id_usuario, password):
    """Comprueba si el usuario y la contraseña son correctos."""
    if not os.path.exists(ruta_usuarios):
        return False
    
    df = pd.read_csv(ruta_usuarios, sep=';')
    pass_hash = encriptar_password(password)
    
    # Buscamos al usuario y comprobamos el hash de la contraseña
    usuario_valido = df[(df['id_usuario'] == id_usuario) & (df['password_hash'] == pass_hash)]
    
    return not usuario_valido.empty

def obtener_perfil_usuario(id_usuario):
    """
    Recupera toda la información de un usuario específico.
    """
    if not os.path.exists(ruta_usuarios):
        return None
    
    df = pd.read_csv(ruta_usuarios, sep=';')
    
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

def actualizar_perfil_usuario(id_usuario, nueva_ciudad, tiene_diagnostico, polen_especifico):
    """
    Actualiza los datos modificables del perfil de un usuario en el CSV.
    """
    if not os.path.exists(ruta_usuarios):
        return False, "Error: No se encontró el archivo de registros."
        
    df = pd.read_csv(ruta_usuarios, sep=';')
    
    # Comprobar si el usuario existe
    if id_usuario not in df['id_usuario'].values:
        return False, "Usuario no encontrado."
        
    # Actualizar los campos en la fila correspondiente
    df.loc[df['id_usuario'] == id_usuario, 'ciudad'] = nueva_ciudad
    df.loc[df['id_usuario'] == id_usuario, 'diagnosticado'] = "Si" if tiene_diagnostico else "No"
    df.loc[df['id_usuario'] == id_usuario, 'alergia_principal'] = polen_especifico if tiene_diagnostico else "No diagnosticado"
    
    # Guardar los cambios de vuelta en el CSV
    df.to_csv(ruta_usuarios, index=False, sep=';')
    return True, "Perfil actualizado con éxito."

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