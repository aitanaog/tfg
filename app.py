import streamlit as st
import pandas as pd
import datetime
import os
from scripts.gestion_usuarios import obtener_perfil_usuario, validar_login, registrar_usuario
from scripts.actualizador_api import actualizar_desde_api
from scripts.analizador_niveles import obtener_color_alerta
from scripts.config import umbrales_polen

# 1. CONFIGURACIÓN INICIAL (DEBE SER LO PRIMERO)
st.set_page_config(page_title="TFG Polen Euskadi", page_icon="🌿", layout="wide")

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
        with st.spinner("Sincronizando con estaciones y ejecutando IA..."):
            try:
                actualizar_desde_api()
                from scripts.predictor import predecir_siguientes_dias
                predecir_siguientes_dias(perfil['ciudad'])
                st.session_state['actualizado_hoy'] = True
                st.rerun() 
            except Exception as e:
                st.error(f"Error en la actualización de datos: {e}")

    # --- SIDEBAR ---
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
        manana = fecha_actual + datetime.timedelta(days=1)
        dias_interes = [ayer2, ayer1, hoy, manana]

# --- MODO A: USUARIO DIAGNOSTICADO ---
        if perfil['diagnosticado'] == "Si":
            alergia = perfil['alergia_principal']
            st.subheader(f"📊 Seguimiento Crítico: {alergia}")
            
            # 1. MÉTRICAS PRINCIPALES
            etiquetas = ["Hace 2 días", "Ayer", "Hoy (Pred)", "Mañana (Pred)"]
            cols = st.columns(4)
            valor_manana = 0.0 # Para la alerta posterior

            for i, fecha in enumerate(dias_interes):
                dato = df_ciudad[df_ciudad['Fecha'] == fecha]
                valor_num = float(dato[alergia].values[0]) if not dato.empty else 0.0
                if fecha == manana: valor_manana = valor_num
                
                nivel, _ = obtener_color_alerta(alergia, valor_num)
                with cols[i]:
                    st.metric(label=etiquetas[i], value=f"{valor_num:.2f}", delta=nivel)

            # 2. PANEL DE PREVENCIÓN PERSONALIZADA
            st.divider()
            nivel_manana, _ = obtener_color_alerta(alergia, valor_manana)
            
            col_info, col_recom = st.columns([1, 1])

            with col_info:
                st.write(f"### 🛡️ Estado para mañana")
                if nivel_manana in ["Alto", "Muy Alto"]:
                    st.error(f"⚠️ **ALERTA CRÍTICA:** Se espera un nivel {nivel_manana.upper()} de {alergia}.")
                elif nivel_manana == "Moderado":
                    st.warning(f"🔔 **PRECAUCIÓN:** Niveles moderados detectados para mañana.")
                else:
                    st.success(f"✅ **DÍA TRANQUILO:** Los niveles de tu alergia serán bajos.")

            with col_recom:
                st.write("### 📋 Recomendaciones")
                if nivel_manana in ["Alto", "Muy Alto"]:
                    st.write("- Use mascarilla FFP2 en exteriores.")
                    st.write("- Evite hacer deporte al aire libre.")
                    st.write("- Al volver a casa, dúchese y cámbiese de ropa.")
                elif nivel_manana == "Moderado":
                    st.write("- Ventile la casa solo al amanecer o atardecer.")
                    st.write("- Use gafas de sol para proteger la conjuntiva.")
                else:
                    st.write("- Puede realizar actividades normales al aire libre.")
                # --- GRÁFICA DE EVOLUCIÓN NORMALIZADA ---
                st.write("### 📈 Análisis de Correlación Temporal")
                try:
                    df_s = pd.read_csv('datos_usuarios/registro_sintomas.csv', sep=';')
                    df_s['fecha'] = pd.to_datetime(df_s['fecha']).dt.date
                    df_u = df_s[df_s['id_usuario'] == st.session_state['id_usuario']]
                    
                    # Cruzamos con datos de polen
                    df_plot = pd.merge(df_u, df_ciudad[['Fecha', alergia]], left_on='fecha', right_on='Fecha')
                    
                    if len(df_plot) > 2:
                        # NORMALIZACIÓN MIN-MAX (Para que ambos queden entre 0 y 1)
                        def normalizar(serie):
                            if serie.max() == serie.min(): return serie * 0 # Evita división por cero
                            return (serie - serie.min()) / (serie.max() - serie.min())

                        df_norm = pd.DataFrame({
                            'Fecha': df_plot['fecha'],
                            'Tu Malestar (Normalizado)': normalizar(df_plot['malestar']),
                            f'Nivel de {alergia} (Normalizado)': normalizar(df_plot[alergia])
                        }).set_index('Fecha')

                        # Mostrar gráfica
                        st.line_chart(df_norm)
                        
                        # Calcular correlación real para mostrarla como dato técnico
                        r = df_plot['malestar'].corr(df_plot[alergia])
                        st.info(f"📊 **Índice de Coincidencia:** {r:.2f} (Un valor cercano a 1 indica que tu malestar depende directamente de este polen).")
                    else:
                        st.info("Aún no hay suficientes días emparejados para mostrar la tendencia.")
                except Exception as e:
                    st.error(f"Error al generar gráfica: {e}")
                except:
                    pass

        # --- MODO B: NO DIAGNOSTICADO ---
        else:
            st.subheader("🔎 Resumen General de Pólenes")
            columnas_excluir = ['Fecha', 'Ciudad', 'Año', 'Anio', 'Mes', 'Dia', 'Unnamed: 0']
            plantas = [c for c in df_ciudad.columns if c not in columnas_excluir]
            
            datos_tab = []
            
            # 1. Definimos la función de extracción
            def extraer_con_riesgo(fila, col):
                if not fila.empty:
                    try:
                        val = float(fila[col].values[0])
                        nivel, _ = obtener_color_alerta(col, val)
                        return f"{val:.2f} ({nivel})"
                    except: return "0.00 (-)"
                return "0.00 (-)"

            # 2. Llenamos la lista de datos (FUERA de cualquier elemento de Streamlit)
            for p in plantas:
                f_ayer = df_ciudad[df_ciudad['Fecha'] == ayer1]
                f_hoy = df_ciudad[df_ciudad['Fecha'] == hoy]
                f_man = df_ciudad[df_ciudad['Fecha'] == manana]
                
                datos_tab.append({
                    "Tipo de Polen": p, 
                    "Ayer (Real)": extraer_con_riesgo(f_ayer, p), 
                    "Hoy (Predicción)": extraer_con_riesgo(f_hoy, p), 
                    "Mañana (Predicción)": extraer_con_riesgo(f_man, p)
                })
            
            # 3. Mostramos la tabla UNA SOLA VEZ
            if datos_tab:
                st.table(pd.DataFrame(datos_tab))
            else:
                st.warning("No hay datos suficientes para mostrar la comparativa.")

            # 4. SECCIÓN DE PRE-DIAGNÓSTICO (Debajo de la tabla)
            st.divider()
            st.subheader("🧬 Asistente de Diagnóstico IA")
            st.write("Nuestra IA analiza la relación entre tus síntomas y los niveles de polen de los últimos 30 días.")
            
            if st.button("Analizar mis últimos 30 días"):
                from scripts.analizador_diagnostico import generar_sugerencia_diagnostico
                
                with st.spinner("Analizando correlaciones biológicas..."):
                    resultado, mensaje = generar_sugerencia_diagnostico(st.session_state['id_usuario'], perfil['ciudad'])
                    
                    if resultado == "Insuficiente":
                        st.warning(mensaje)
                    elif resultado == "Error":
                        st.error(f"No se pudo realizar el análisis: {mensaje}")
                    else:
                        st.success("¡Análisis completado!")
                        st.markdown(f"### 🎯 Resultado: Posible alergia a **{resultado}**")
                        st.info(mensaje)
                        st.caption("⚠️ Recuerda: Este informe es orientativo basado en estadística. Consulta siempre a un alergólogo.")

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
        
        # 2. Checkboxes de síntomas específicos (LISTA ACTUALIZADA)
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
            tomo_med = st.radio("¿Has tomado medicación?", ["No", "Sí"], horizontal=True)
        with col_m2:
            comentarios = st.text_input("Notas adicionales (ej: 'Mucho tiempo al aire libre')")
        
        if st.form_submit_button("Guardar Registro Diario"):
            ruta_sintomas = 'datos_usuarios/registro_sintomas.csv'
            if not os.path.exists('datos_usuarios'):
                os.makedirs('datos_usuarios')
                
            # Diccionario con todos los nuevos campos
            nuevo_registro = {
                'id_usuario': st.session_state['id_usuario'],
                'fecha': fecha_actual,
                'malestar': malestar,
                'estornudos': s_estornudos,
                'rinitis': s_rinitis,
                'conjuntivitis': s_conjuntivitis,
                'picor_garganta': s_picor_garganta,
                'tos': s_tos,
                'asma': s_asma,
                'dolor_cabeza': s_dolor_cabeza,
                'picor_nasal': s_picor_nasal,
                'opresion_toracica': s_opresion,
                'erupcion': s_erupcion,
                'mucosidad': s_mucosidad,
                'medicacion': tomo_med,
                'comentarios': comentarios
            }
            
            df_s = pd.DataFrame([nuevo_registro])
            header = not os.path.exists(ruta_sintomas)
            
            df_s.to_csv(ruta_sintomas, mode='a', index=False, header=header, sep=';', encoding='utf-8-sig')
            
            st.success("✅ Registro guardado correctamente.")
            st.divider()
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
    st.title("🌿 Control de Alergias Euskadi")
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
        new_u = st.text_input("Usuario")
        new_p = st.text_input("Contraseña", type='password')
        c = st.selectbox("Ciudad", ["Bilbao", "Donostia", "Vitoria"])
        e = st.number_input("Edad", 0, 100, 25)
        d = st.radio("¿Diagnosticado?", ["No", "Sí"])
        p_esp = st.selectbox("Alergia principal", options=list(umbrales_polen.keys())) if d == "Sí" else "No diagnosticado"
        if st.button("Registrarme"):
            exito, msg = registrar_usuario(new_u, new_p, c, e, (d=="Sí"), p_esp)
            if exito: st.success(msg)
            else: st.error(msg)