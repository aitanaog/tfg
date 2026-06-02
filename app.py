import streamlit as st
import pandas as pd
import datetime
import os
from scripts.gestion_usuarios import obtener_perfil_usuario, validar_login, registrar_usuario
from scripts.actualizador_api import actualizar_desde_api
from scripts.analizador_niveles import obtener_color_alerta
from scripts.config import umbrales_polen
import zipfile
import os

if not os.path.exists('modelos_entrenados'):
    with zipfile.ZipFile('modelos_entrenados.zip', 'r') as zip_ref:
        zip_ref.extractall('.')
        
# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="PolenGune", page_icon="🌿", layout="wide")

# 2. INICIALIZACIÓN DE VARIABLES DE SESIÓN
if 'logueado' not in st.session_state:
    st.session_state['logueado'] = False
if 'actualizado_hoy' not in st.session_state:
    st.session_state['actualizado_hoy'] = False

# --- FLUJO DE PANTALLAS ---

if st.session_state['logueado']:
    # ==========================================
    # PANTALLA: DASHBOARD (USUARIO LOGUEADO)
    # ==========================================
    
    perfil = obtener_perfil_usuario(st.session_state['id_usuario'])

    # --- MOTOR DE DATOS Y PREDICCIÓN ---
    if not st.session_state['actualizado_hoy']:
        with st.spinner("Sincronizando con estaciones y ejecutando predicción..."):
            try:
                actualizar_desde_api()
                from scripts.predictor import predecir_siguientes_dias
                predecir_siguientes_dias(perfil['ciudad'])
                st.session_state['actualizado_hoy'] = True
                st.rerun() 
            except Exception as e:
                st.error(f"Error en la actualización de datos: {e}")

    # --- SIDEBAR DE LA CUENTA ---
    with st.sidebar:
        st.header("⚙️ Mi Cuenta")
        st.write(f"👤 **Usuario:** {st.session_state['id_usuario']}")
        st.write(f"📍 **Ciudad:** {perfil['ciudad']}")
        if st.button("Cerrar Sesión"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.divider()

    # --- CABECERA ---
    fecha_actual = datetime.date.today()
    st.title(f"🌿 Panel de Control - {perfil['ciudad']}")
    st.info(f"📅 **Día de consulta:** {fecha_actual.strftime('%d/%m/%Y')}")

    # --- CARGA DE DATOS ---
    try:
        ruta_csv = 'datos_procesados/polen_euskadi_final.csv'
        df = pd.read_csv(ruta_csv, sep=';')
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='mixed').dt.date
        df_ciudad = df[df['Ciudad'] == perfil['ciudad']].sort_values(by='Fecha')

        ayer2 = fecha_actual - datetime.timedelta(days=2)
        ayer1 = fecha_actual - datetime.timedelta(days=1)
        hoy = fecha_actual
        mañana = fecha_actual + datetime.timedelta(days=1)
        dias_interes = [ayer2, ayer1, hoy, mañana]

        # --- MODO A: USUARIO DIAGNOSTICADO ---
        if perfil['diagnosticado'] == "Si":
            alergia_principal = perfil['alergia_principal']
            st.subheader(f"📊 Seguimiento Crítico: {alergia_principal}")
            
            # 1. MÉTRICAS EN GRANDE (ALERGIA PRINCIPAL)
            etiquetas = ["Hace 2 días", "Ayer", "Predicción de hoy", "Predicción de mañana"]
            cols_principal = st.columns(4)
            valor_mañana_principal = 0.0 

            for i, fecha in enumerate(dias_interes):
                dato = df_ciudad[df_ciudad['Fecha'] == fecha]
                valor_num = float(dato[alergia_principal].values[0]) if not dato.empty else 0.0
                if fecha == mañana: valor_mañana_principal = valor_num
                
                nivel, _ = obtener_color_alerta(alergia_principal, valor_num)
                with cols_principal[i]:
                    st.metric(label=etiquetas[i], value=f"{valor_num:.2f}", delta=nivel)

            # ---------------------------------------------------------
            # SECCIÓN:OTROS PÓLENES 
            # ---------------------------------------------------------
            st.write("---")
            st.subheader("🌐 Otros niveles en tu zona (Hoy)")
            
            # Identificamos todas las columnas de polen excepto Fecha, Ciudad y la Principal
            columnas_polen = [col for col in df_ciudad.columns if col not in ['Fecha', 'Ciudad', 'Año']]
            otros_polenes = [col for col in columnas_polen if col != alergia_principal]
            
            # Creamos un grid de 4 columnas para que no ocupe demasiado espacio vertical
            cols_otros = st.columns(4)
            dato_hoy = df_ciudad[df_ciudad['Fecha'] == hoy]

            for idx, col_polen in enumerate(otros_polenes):
                valor_hoy = float(dato_hoy[col_polen].values[0]) if not dato_hoy.empty else 0.0
                nivel_otros, _ = obtener_color_alerta(col_polen, valor_hoy)
                
                # Repartimos en las 4 columnas
                with cols_otros[idx % 4]:
                    # Usamos un formato algo más compacto para que no compita con la principal
                    st.write(f"**{col_polen}**")
                    st.caption(f"{valor_hoy:.1f} - {nivel_otros}")

            # ---------------------------------------------------------
            # 2. PANEL DE PREVENCIÓN PERSONALIZADA (ALERGIA PRINCIPAL)
            # ---------------------------------------------------------
            st.divider()
            nivel_manana, _ = obtener_color_alerta(alergia_principal, valor_mañana_principal)
            
            col_info, col_recom = st.columns([1, 1])

            with col_info:
                st.write(f"### 🛡️ Estado para mañana")
                if nivel_manana in ["Alto", "Muy Alto"]:
                    st.error(f"⚠️ **ALERTA CRÍTICA:** Nivel {nivel_manana.upper()} de {alergia_principal}.")
                elif nivel_manana == "Moderado":
                    st.warning(f"🔔 **PRECAUCIÓN:** Niveles moderados para mañana.")
                else:
                    st.success(f"✅ **DÍA TRANQUILO:** Niveles bajos de {alergia_principal}.")

            with col_recom:
                st.write("### 📋 Recomendaciones")
                if nivel_manana in ["Alto", "Muy Alto"]:
                    st.write("- Use mascarilla FFP2 en exteriores.")
                    st.write("- Evite hacer deporte al aire libre.")
                elif nivel_manana == "Moderado":
                    st.write("- Ventile la casa solo al amanecer o atardecer.")
                    st.write("- Use gafas de sol.")
                else:
                    st.write("- Puede realizar actividades normales.")
                    
            
            # ---------------------------------------------------------
            # 3. ASISTENTE DE DIAGNÓSTICO (ALERTAS CRUZADAS)
            # ---------------------------------------------------------
            st.divider()
            col_ia_text, col_ia_btn = st.columns([2, 1])
            with col_ia_text:
                st.subheader("🧬 Asistente de Diagnóstico ")
                st.write(f"¿Sigues notando malestar incluso con niveles bajos de {alergia_principal}? Analizaremos si estás desarrollando una nueva sensibilidad.")
            
            with col_ia_btn:
                btn_analizar_diagnosticado = st.button("🚀 Iniciar Análisis de IA", key="btn_ia_diag", use_container_width=True)

            if btn_analizar_diagnosticado:
                from scripts.analizador_diagnostico import generar_sugerencia_diagnostico
                with st.spinner("Analizando correlaciones y patrones clínicos..."):
                    resultado, mensaje, confianza= generar_sugerencia_diagnostico(st.session_state['id_usuario'], perfil['ciudad'])
                    
                    if resultado in ["Insuficiente", "Error"]:
                        st.warning(mensaje)
                    
                    # CASO 1: El polen sospechoso de la IA es el mismo que ya tiene diagnosticado
                    elif resultado.lower() == alergia_principal.lower():
                        st.success(f"### ✅ Relación Confirmada")
                        st.info(f"El motor analítico corrobora que tus síntomas actuales siguen fuertemente ligados a tu alergia principal a **{alergia_principal}**. {mensaje}")
                    
                    # CASO 2: La IA detecta un polen nuevo peligroso
                    else:
                        st.balloons()
                        st.warning(f"### ⚠️ Alerta de Nueva Sensibilidad: **{resultado}**")
                        st.markdown(f"""
                        **¡Atención!** Aunque tu perfil indica que estás diagnosticado de *{alergia_principal}*, 
                        nuestro motor inteligente ha detectado que tus síntomas de las últimas semanas guardan una relación mucho más estrecha 
                        con los niveles ambientales de **{resultado}**. 
                        
                        Esto podría sugerir el desarrollo de una **alergia cruzada** o una nueva hipersensibilidad estacional.
                        
                        *Detalles del análisis:* {mensaje}
                        """)



        # --- MODO B: NO DIAGNOSTICADO ---
        else:
            st.subheader("🔎 Estado de los Pólenes Hoy")
            st.write("A continuación se muestran las especies con niveles significativos en tu ciudad.")
            
            columnas_excluir = ['Fecha', 'Ciudad', 'Año', 'Mes', 'Dia', 'Unnamed: 0']
            plantas = [c for c in df_ciudad.columns if c not in columnas_excluir]
            
            # Obtenemos los datos de hoy y mañana
            fila_hoy = df_ciudad[df_ciudad['Fecha'] == hoy]
            fila_mañana = df_ciudad[df_ciudad['Fecha'] == mañana]

            # Creamos contenedores para organizar la vista
            col_alertas, col_bajos = st.columns([2, 1])

            with col_alertas:
                st.markdown("### ⚠️ Niveles Moderados / Altos")
                hay_alertas = False
                
                for p in plantas:
                    try:
                        val_hoy = float(fila_hoy[p].values[0]) if not fila_hoy.empty else 0.0
                        val_mañana = float(fila_mañana[p].values[0]) if not fila_mañana.empty else 0.0
                        nivel, _ = obtener_color_alerta(p, val_hoy)

                        # Solo mostramos en esta columna si el riesgo no es bajo
                        if nivel != "Bajo":
                            hay_alertas = True
                            # Calculamos tendencia
                            tendencia = "Subiendo 📈" if val_man > val_hoy else "Bajando 📉"
                            if abs(val_man - val_hoy) < 0.1: tendencia = "Estable ➡️"

                            with st.expander(f"**{p}**: {val_hoy:.1f} ({nivel})", expanded=True):
                                c1, c2 = st.columns(2)
                                c1.metric("Hoy", f"{val_hoy:.1f}")
                                c2.metric("Mañana (Pred)", f"{val_man:.1f}", delta=tendencia, delta_color="normal")
                    except:
                        continue
                
                if not hay_alertas:
                    st.success("No hay niveles de riesgo detectados para hoy. ¡Día tranquilo!")

            with col_bajos:
                st.markdown("### 🟢 Niveles Bajos")
                # Lista compacta para los pólenes que no preocupan
                for p in plantas:
                    try:
                        val_hoy = float(fila_hoy[p].values[0]) if not fila_hoy.empty else 0.0
                        nivel, _ = obtener_color_alerta(p, val_hoy)
                        if nivel == "Bajo":
                            st.caption(f"✅ {p}: {val_hoy:.1f}")
                    except:
                        continue




            # 3. SECCIÓN DE PRE-DIAGNÓSTICO (Más limpia)
            st.divider()
            col_ia_text, col_ia_btn = st.columns([2, 1])
            with col_ia_text:
                st.subheader("🧬 Asistente de Diagnóstico ")
                st.write("¿Notas malestar pero no sabes a qué polen? Analizaremos tus últimos 30 días.")
            
            with col_ia_btn:
                btn_analizar = st.button("🚀 Iniciar Análisis de Inteligencia Artificial", use_container_width=True)

            if btn_analizar:
                from scripts.analizador_diagnostico import generar_sugerencia_diagnostico
                with st.spinner("Analizando correlaciones..."):
                    resultado, mensaje, confianza = generar_sugerencia_diagnostico(st.session_state['id_usuario'], perfil['ciudad'])
                    if resultado in ["Insuficiente", "Error"]:
                        st.warning(mensaje)
                    else:
                        st.balloons()
                        st.success(f"### 🎯 Posible sensibilidad: **{resultado}** ")
                        st.info(mensaje)

    except Exception as e:
        st.error(f"Hubo un problema al cargar los datos: {e}")

    # --- SECCIÓN SÍNTOMAS ---
    st.divider()
    st.subheader("📝 Diario de Síntomas")
    st.info("Registra tu estado diario para ayudar a la IA a entender cómo te afectan los niveles de polen.")

    with st.form("form_sintomas"):
        # 1. Nivel de malestar
        malestar = st.select_slider(
            "Nivel de malestar general", 
            options=range(11), 
            value=0, 
            help="0: Sin síntomas, 10: Malestar extremo"
        )
        
        # 2. Checkboxes de síntomas específicos 
        st.write("**Selecciona los síntomas que presentas hoy:**")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            s_estornudos = st.checkbox("Estornudos")
            s_rinitis = st.checkbox("Rinitis")
            s_conjuntivitis = st.checkbox("Conjuntivitis")
            s_picor_garganta = st.checkbox("Picor de garganta")
            
        with col_s2:
            s_tos = st.checkbox("Tos")
            s_asma = st.checkbox("Asma")
            s_dolor_cabeza = st.checkbox("Dolor de Cabeza")
            s_picor_nasal = st.checkbox("Picor nasal")
            
        with col_s3:
            s_opresion = st.checkbox("Opresión torácica")
            s_erupcion = st.checkbox("Erupción")
            s_mucosidad = st.checkbox("Mucosidad")
            
        # 3. Medicación y notas
        st.divider()
        col_m1, col_m2 = st.columns([1, 2])
        with col_m1:
            tmo_med = st.radio("¿Has tomado medicación?", ["No", "Sí"], horizontal=True)
        with col_m2:
            comentarios = st.text_input("Notas adicionales (ej: 'Mucho tiempo al aire libre')")
        
        submit_button = st.form_submit_button("Guardar Registro Diario")

    # Procesamiento del formulario en app.py
    if submit_button:
        # Construcción de la lista de síntomas activos
        sintomas_marcados = []
        if s_conjuntivitis: sintomas_marcados.append('conjuntivitis')
        if s_estornudos: sintomas_marcados.append('estornudos')
        if s_rinitis: sintomas_marcados.append('rinitis')
        if s_asma: sintomas_marcados.append('asma')
        if s_picor_garganta: sintomas_marcados.append('picor_garganta')
        if s_tos: sintomas_marcados.append('tos')
        if s_dolor_cabeza: sintomas_marcados.append('dolor_cabeza')
        if s_opresion: sintomas_marcados.append('opresion_toracica')
        if s_picor_nasal: sintomas_marcados.append('picor_nasal')
        if s_erupcion: sintomas_marcados.append('erupcion')
        if s_mucosidad: sintomas_marcados.append('mucosidad')

        # VALIDACIÓN: Comprobar si todo está vacío
        if malestar == 0 and len(sintomas_marcados) == 0:
            st.error("❌ No se puede guardar un registro vacío. Por favor, selecciona tu nivel de malestar o marca algún síntoma.")
        else:
            # Llamamos al backend pasándole únicamente los datos del CSV de síntomas
            exito, msg = registrar_entrada_salud(
                id_usuario=st.session_state['id_usuario'],
                fecha=fecha_actual,
                nivel=malestar,
                sintomas_activos=sintomas_marcados,
                medicacion=tmo_med,      
                comentarios=comentarios         
            )
            
            if exito:
                st.success(msg)
            else:
                st.error(msg)
        st.subheader("📂 Exportar Historial Médico")
        col_pdf1, col_pdf2 = st.columns([2, 1])
        
    with col_pdf1:
        st.write("Genera un documento PDF profesional con la evolución de tus síntomas y niveles de polen para facilitar el diagnóstico de tu alergólogo.")
        
    with col_pdf2:
        if st.button("📄 Generar Informe PDF", use_container_width=True):
            from scripts.generador_pdf import exportar_pdf
                
            # Determinamos si enviamos una alergia específica o no
            alergia_usr = perfil['alergia_principal'] if perfil['diagnosticado'] == "Sí" else None
                
            with st.spinner("Compilando datos y generando PDF..."):
                exito, resultado = exportar_pdf(st.session_state['id_usuario'], perfil['ciudad'], alergia_usr)
                
            if exito:
                with open(resultado, "rb") as f:
                    st.download_button(
                        label="📥 Descargar ahora",
                        data=f,
                        file_name=os.path.basename(resultado),
                        mime="application/pdf",
                        use_container_width=True
                    )
                st.success("¡Informe listo!")
            else:
                st.error(f"No se pudo generar el informe: {resultado}")
else:
    # ==========================================
    # PANTALLA: LOGIN / REGISTRO (SI NO ESTÁ LOGUEADO)
    # ==========================================
    st.title("🌿 PolenGune : Control de Alergias Euskadi")
    choice = st.sidebar.selectbox("Acceso", ["Login", "Registro"])

    if choice == "Login":
        st.subheader("Iniciar Sesión")
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type='password')
        if st.button("Entrar"):
            if validar_login(u, p):
                st.session_state['logueado'] = True
                st.session_state['id_usuario'] = u
                st.rerun()
            else: st.error("Credenciales incorrectas")

    elif choice == "Registro":
        st.subheader("Crear nueva cuenta")
        st.caption("Todos los campos de este formulario son obligatorios")
        
        new_u = st.text_input("Usuario *").strip()
        new_p = st.text_input("Contraseña *", type='password').strip()
        
        opciones_ciudades = ["Seleccione una ciudad...", "Bilbao", "Donostia", "Vitoria"]
        c = st.selectbox("Ciudad *", opciones_ciudades)
        
        e = st.number_input("Edad *", min_value=0, max_value=100, value=0, help="Introduzca una edad válida mayor que 0")
        
        d = st.radio("¿Está diagnosticado de alguna alergia? *", ["Seleccione una opción...", "No", "Sí"])
        
        p_esp = "No diagnosticado"
        mostrar_alergia_selectbox = False
        
        if d == "Sí":
            opciones_alergias = ["Seleccione su alergia principal..."] + list(umbrales_polen.keys())
            p_esp = st.selectbox("Alergia principal *", opciones_alergias)
            mostrar_alergia_selectbox = True
            
        if st.button("Registrarme"):
            errores = []
            
            if not new_u:
                errores.append("El campo 'Usuario' no puede estar vacío.")
            if not new_p:
                errores.append("El campo 'Contraseña' no puede estar vacío.")
            if c == "Seleccione una ciudad...":
                errores.append("Debe seleccionar una 'Ciudad' de la lista.")
            if e <= 0:
                errores.append("Debe introducir una 'Edad' válida (mayor que 0).")
            if d == "Seleccione una opción...":
                errores.append("Debe responder a la pregunta '¿¿Diagnosticado??'.")
            if d == "Sí" and p_esp == "Seleccione su alergia principal...":
                errores.append("Ha marcado que sí está diagnosticado, debe seleccionar su 'Alergia principal'.")
                
            if errores:
                for error in errores:
                    st.error(error)
            else:
                tiene_diag_bool = (d == "Sí")
                exito, msg = registrar_usuario(new_u, new_p, c, e, tiene_diag_bool, p_esp)
                if exito: 
                    st.success(msg)
                else: 
                    st.error(msg)