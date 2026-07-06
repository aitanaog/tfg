import streamlit as st
import pandas as pd
import datetime
import os
from scripts.gestion_usuarios import obtener_perfil_usuario, validar_login, registrar_usuario, inicializar_usuarios, actualizar_perfil_usuario
from scripts.actualizador_api import actualizar_desde_api
from scripts.analizador_niveles import obtener_color_alerta
from scripts.gestion_sintomas import registrar_entrada_salud
from scripts.config import umbrales_polen, municipios
from scripts.i18n import DICCIONARIO
import zipfile

if not os.path.exists('modelos_entrenados'):
    with zipfile.ZipFile('modelos_entrenados.zip', 'r') as zip_ref:
        zip_ref.extractall('.')
        
st.set_page_config(page_title="PolenGune", page_icon="🌿", layout="wide")

# INICIALIZACIÓN DE VARIABLES DE SESIÓN
if 'logueado' not in st.session_state:
    st.session_state['logueado'] = False
if 'actualizado_hoy' not in st.session_state:
    st.session_state['actualizado_hoy'] = False

# SELECTOR GLOBAL DE IDIOMA EN LA SIDEBAR (BARRA LATERAL)
idioma = st.sidebar.selectbox(DICCIONARIO["Castellano"]["selector_idioma"], ["Castellano", "Euskara"])


# EDICIÓN PERFIL
@st.dialog("⚙️ Editar Perfil de Usuario" if idioma == "Castellano" else "⚙️ Erabiltzailearen Profila Editatu")
def mostrar_edicion():
    if 'perfil' not in st.session_state:
        st.write("Inicie sesión para modificar su perfil." if idioma == "Castellano" else "Hasi saioa profila aldatzeko.")
        return
        
    perfil_actual = st.session_state['perfil']
    st.write("Modifique los campos que necesite actualizar" if idioma == "Castellano" else "Aldatu eguneratu behar dituzun profilen eremuak:")
    
    ciudades = list(municipios.keys())
    indice_ciudad = ciudades.index(perfil_actual['ciudad']) if perfil_actual['ciudad'] in ciudades else 0
    nueva_ciudad = st.selectbox(DICCIONARIO[idioma]["lbl_ciudad"], options=ciudades, index=indice_ciudad)
    
    diag_previo = perfil_actual.get('diagnosticado', 'No') == 'Si'
    tiene_diag = st.checkbox(DICCIONARIO[idioma]["lbl_diag"], value=diag_previo)
    
    polenes = list(umbrales_polen.keys())
    alergia_actual = perfil_actual.get('alergia_principal', '')
    indice_polen = polenes.index(alergia_actual) if alergia_actual in polenes else 0
    
    polen_especifico = "No diagnosticado"
    if tiene_diag:
        polen_especifico = st.selectbox(DICCIONARIO[idioma]["lbl_alergia"], options=polenes, index=indice_polen)
    
    st.divider()
    texto_guardar = "💾 Guardar Cambios" if idioma == "Castellano" else "💾 Aldaketak Gorde"
    if st.button(texto_guardar, use_container_width=True):
        exito, msg = actualizar_perfil_usuario(st.session_state['id_usuario'], nueva_ciudad, tiene_diag, polen_especifico)
        if exito:
            st.session_state['perfil']['ciudad'] = nueva_ciudad
            st.session_state['perfil']['diagnosticado'] = "Si" if tiene_diag else "No"
            st.session_state['perfil']['alergia_principal'] = polen_especifico
            st.success("✅ Perfil actualizado correctamente." if idioma == "Castellano" else "✅ Profila ondo eguneratu da.")
            st.rerun()
        else:
            st.error(msg)

# =========================================================================
# FLUJO DE PANTALLAS (LOGUEADO)
# =========================================================================

if st.session_state['logueado']:
    perfil = st.session_state.get('perfil', obtener_perfil_usuario(st.session_state['id_usuario']))

    # --- MOTOR DE DATOS Y PREDICCIÓN ---
    # Solo se ejecuta una vez por sesión/día (controlado por 'actualizado_hoy').

    if not st.session_state['actualizado_hoy']:
        with st.spinner(DICCIONARIO[idioma]["st_sincro"]):
            try:
                errores = actualizar_desde_api()
                if errores:
                    st.warning(f"No se pudieron actualizar datos para: {', '.join(errores)}")
                    
                from scripts.predictor import predecir_siguientes_dias #solo se carga el modelo de predicción cuando realmente hace falta (mejora el tiempo de arranque).
                predecir_siguientes_dias(perfil['ciudad'])
                st.session_state['actualizado_hoy'] = True
                st.rerun() 
            except Exception as e:
                st.error(f"{DICCIONARIO[idioma]['err_sincro']}{e}")

    # --- SIDEBAR DE LA CUENTA ---
    with st.sidebar:
        st.header(DICCIONARIO[idioma]["hdr_cuenta"])
        st.write(f"{DICCIONARIO[idioma]['txt_usuario']}{st.session_state['id_usuario']}")
        st.write(f"{DICCIONARIO[idioma]['txt_ciudad']}{perfil['ciudad']}")
        st.write(f"🩺 **{DICCIONARIO[idioma]['txt_alergia']}** {perfil.get('alergia_principal', 'No diagnosticado')}")
        
        if st.button(DICCIONARIO[idioma]["btn_editar_perfil"], use_container_width=True):
            mostrar_edicion()
            
        if st.button(DICCIONARIO[idioma]["btn_logout"], use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.divider()

    # --- 1. CABECERA ---
    fecha_actual = datetime.date.today()
    st.title(f"{DICCIONARIO[idioma]['ttl_panel']}{perfil['ciudad']}")
    st.info(f"{DICCIONARIO[idioma]['inf_consulta']}{fecha_actual.strftime('%d/%m/%Y')}")


    # SECCIÓN 2: ESTADO DE LOS PÓLENES 

    valor_mañana_principal = 0.0  # Variable de control
    
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
            st.subheader(f"{DICCIONARIO[idioma]['sub_critico']}{alergia_principal}")
            etiquetas = DICCIONARIO[idioma]["etiquetas_dias"]
            cols_principal = st.columns(4)

            for i, fecha in enumerate(dias_interes):
                dato = df_ciudad[df_ciudad['Fecha'] == fecha]
                valor_num = float(dato[alergia_principal].values[0]) if not dato.empty else 0.0
                if fecha == mañana: valor_mañana_principal = valor_num
                
                nivel, _ = obtener_color_alerta(alergia_principal, valor_num)
                with cols_principal[i]:
                    # Usamos 'delta' para mostrar el nivel de alerta (Bajo/Moderado/Alto...)
                    st.metric(label=etiquetas[i], value=f"{valor_num:.2f}", delta=nivel)

            st.write("---")
            st.subheader(DICCIONARIO[idioma]["lbl_otros"])
            columnas_polen = []
            for col in df_ciudad.columns:
                if col not in ['Fecha', 'Ciudad', 'Año']:
                    columnas_polen.append(col)
            otros_polenes = [col for col in columnas_polen if col != alergia_principal]
            
            cols_otros = st.columns(4)
            dato_hoy = df_ciudad[df_ciudad['Fecha'] == hoy]

            for idx, col_polen in enumerate(otros_polenes):
                valor_hoy = float(dato_hoy[col_polen].values[0]) if not dato_hoy.empty else 0.0
                nivel_otros, _ = obtener_color_alerta(col_polen, valor_hoy)
                with cols_otros[idx % 4]:
                    st.write(f"**{col_polen}**")
                    st.caption(f"{valor_hoy:.1f} - {nivel_otros}")

            st.divider()
            nivel_mañana, _ = obtener_color_alerta(alergia_principal, valor_mañana_principal)
            col_info, col_recom = st.columns([1, 1])

            with col_info:
                st.write(DICCIONARIO[idioma]["sub_mañana"])
                if nivel_mañana in ["Alto", "Muy Alto"]:
                    st.error(f"{DICCIONARIO[idioma]['alt_critica']}{nivel_mañana.upper()} de {alergia_principal}.")
                elif nivel_mañana == "Moderado":
                    st.warning(DICCIONARIO[idioma]["alt_mod"])
                else:
                    st.success(f"{DICCIONARIO[idioma]['alt_baja']}{alergia_principal}.")

            with col_recom:
                st.write(DICCIONARIO[idioma]["sub_recom"])
                if nivel_mañana in ["Alto", "Muy Alto"]:
                    for rec in DICCIONARIO[idioma]["rec_alto"]: st.write(rec)
                elif nivel_mañana == "Moderado":
                    for rec in DICCIONARIO[idioma]["rec_mod"]: st.write(rec)
                else:
                    for rec in DICCIONARIO[idioma]["rec_bajo"]: st.write(rec)

        # --- MODO B: NO DIAGNOSTICADO ---
        else:
            st.subheader(DICCIONARIO[idioma]["sub_hoy"])
            st.write(DICCIONARIO[idioma]["txt_hoy"])
            
            columnas_excluir = ['Fecha', 'Ciudad', 'Año']
            plantas = [c for c in df_ciudad.columns if c not in columnas_excluir]
            
            fila_hoy = df_ciudad[df_ciudad['Fecha'] == hoy]
            fila_mañana = df_ciudad[df_ciudad['Fecha'] == mañana]

            col_alertas, col_bajos = st.columns([2, 1])

            # Recorremos 'plantas' UNA sola vez, clasificando cada una como
            # "en alerta" (nivel Moderado o superior) o "baja"
            
            plantas_alerta = []
            plantas_bajas = []

            for p in plantas:
                try:
                    val_hoy = float(fila_hoy[p].values[0]) if not fila_hoy.empty else 0.0
                    val_man = float(fila_mañana[p].values[0]) if not fila_mañana.empty else 0.0
                    nivel, _ = obtener_color_alerta(p, val_hoy)

                    if nivel == "Bajo":
                        plantas_bajas.append((p, val_hoy))
                    else:
                        if val_man > val_hoy:
                            tendencia = DICCIONARIO[idioma]["tend_subiendo"]
                        else:
                            tendencia = DICCIONARIO[idioma]["tend_bajando"]
                        if abs(val_man - val_hoy) < 0.1:
                            tendencia = DICCIONARIO[idioma]["tend_estable"]
                        plantas_alerta.append((p, val_hoy, val_man, nivel, tendencia))
                except (IndexError, KeyError):
                    continue

            with col_alertas:
                st.markdown(DICCIONARIO[idioma]["lbl_mod_alt"])
                if not plantas_alerta:
                    st.success(DICCIONARIO[idioma]["txt_tranquilo"])
                for p, val_hoy, val_man, nivel, tendencia in plantas_alerta:
                    with st.expander(f"**{p}**: {val_hoy:.1f} ({nivel})", expanded=True):
                        c1, c2 = st.columns(2)
                        c1.metric(DICCIONARIO[idioma]["lbl_hoy_metric"], f"{val_hoy:.1f}")
                        c2.metric(DICCIONARIO[idioma]["lbl_manana_metric"], f"{val_man:.1f}", delta=tendencia, delta_color="normal")

            with col_bajos:
                st.markdown(DICCIONARIO[idioma]["lbl_bajos"])
                for p, val_hoy in plantas_bajas:
                    st.caption(f"✅ {p}: {val_hoy:.1f}")
                    
    except Exception as e:
        st.error(f"Hubo un problema al cargar los datos de polen: {e}")

    
    # SECCIÓN 3: DIARIO DE SÍNTOMAS

    st.divider()
    st.subheader(DICCIONARIO[idioma]["ttl_diario"])
    st.info(DICCIONARIO[idioma]["inf_diario"])

    with st.form("form_sintomas"):
        malestar = st.select_slider(DICCIONARIO[idioma]["lbl_malestar"], options=range(11), value=0, help=DICCIONARIO[idioma]["hlp_malestar"])
        st.write(DICCIONARIO[idioma]["lbl_seleccion"])
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            s_estornudos = st.checkbox(DICCIONARIO[idioma]["sint_estornudos"])
            s_rinitis = st.checkbox(DICCIONARIO[idioma]["sint_rinitis"])
            s_conjuntivitis = st.checkbox(DICCIONARIO[idioma]["sint_conjuntivitis"])
            s_picor_garganta = st.checkbox(DICCIONARIO[idioma]["sint_picor_garganta"])
        with col_s2:
            s_tos = st.checkbox(DICCIONARIO[idioma]["sint_tos"])
            s_asma = st.checkbox(DICCIONARIO[idioma]["sint_asma"])
            s_dolor_cabeza = st.checkbox(DICCIONARIO[idioma]["sint_dolor_cabeza"])
            s_picor_nasal = st.checkbox(DICCIONARIO[idioma]["sint_picor_nasal"])
        with col_s3:
            s_opresion = st.checkbox(DICCIONARIO[idioma]["sint_opresion"])
            s_erupcion = st.checkbox(DICCIONARIO[idioma]["sint_erupcion"])
            s_mucosidad = st.checkbox(DICCIONARIO[idioma]["sint_mucosidad"])
            
        st.divider()
        col_m1, col_m2 = st.columns([1, 2])
        with col_m1:
            tmo_med = st.radio(DICCIONARIO[idioma]["lbl_med"], [DICCIONARIO[idioma]["opc_no"], DICCIONARIO[idioma]["opc_si"]], horizontal=True)
        with col_m2:
            comentarios = st.text_input(DICCIONARIO[idioma]["lbl_comentarios"])
        
        submit_button = st.form_submit_button(DICCIONARIO[idioma]["btn_diario"])

    if submit_button:
        sintomas_marcados = []
        if s_estornudos: sintomas_marcados.append('estornudos')
        if s_rinitis: sintomas_marcados.append('rinitis')
        if s_conjuntivitis: sintomas_marcados.append('conjuntivitis')
        if s_picor_garganta: sintomas_marcados.append('picor_garganta')
        if s_tos: sintomas_marcados.append('tos')
        if s_asma: sintomas_marcados.append('asma')
        if s_dolor_cabeza: sintomas_marcados.append('dolor_cabeza')
        if s_picor_nasal: sintomas_marcados.append('picor_nasal')
        if s_opresion: sintomas_marcados.append('opresion_toracica')
        if s_erupcion: sintomas_marcados.append('erupcion')
        if s_mucosidad: sintomas_marcados.append('mucosidad')

        if malestar == 0 and len(sintomas_marcados) == 0:
            st.error(DICCIONARIO[idioma]["err_diario_vacio"])
        else:
            med_backend = "Sí" if tmo_med in ("Sí", "Bai") else "No"
            exito, msg = registrar_entrada_salud(
                id_usuario=st.session_state['id_usuario'], fecha=fecha_actual, nivel=malestar,
                sintomas_activos=sintomas_marcados, medicacion=med_backend, comentarios=comentarios         
            )
            if exito: st.success(msg)
            else: st.error(msg)


    # SECCIÓN 4: ASISTENTE DE DIAGNÓSTICO
    st.divider()
    col_ia_text, col_ia_btn = st.columns([2, 1])
    
    with col_ia_text:
        st.subheader(DICCIONARIO[idioma]["ttl_asistente"])
        if perfil['diagnosticado'] == "Si":
            st.write(DICCIONARIO[idioma]["txt_asistente_diag"].format(alergia=perfil['alergia_principal']))
        else:
            st.write(DICCIONARIO[idioma]["txt_asistente_nodo"])
    
    with col_ia_btn:
        btn_analizar = st.button(DICCIONARIO[idioma]["btn_analizar"], key="btn_ia_global", use_container_width=True)

    if btn_analizar:
        from scripts.analizador_diagnostico import generar_sugerencia_diagnostico
        with st.spinner(DICCIONARIO[idioma]["st_analizando_pats"] if perfil['diagnosticado'] == "Si" else DICCIONARIO[idioma]["st_analizando"]):
            
            if perfil['diagnosticado'] == "Si":
                resultado, mensaje = generar_sugerencia_diagnostico(st.session_state['id_usuario'], perfil['ciudad'])
                if resultado in ["Insuficiente", "Error"]:
                    st.warning(mensaje)
                elif resultado.lower() == perfil['alergia_principal'].lower():
                    st.success(DICCIONARIO[idioma]["ia_confirmada"])
                    st.info(f"{DICCIONARIO[idioma]['ia_msg_conf'].format(alergia=perfil['alergia_principal'])}{mensaje}")
                else:
                    st.balloons()
                    st.warning(DICCIONARIO[idioma]["ia_nueva_sens"].format(resultado=resultado))
                    st.markdown(f"{DICCIONARIO[idioma]['ia_msg_nueva'].format(alergia=perfil['alergia_principal'], resultado=resultado)}{mensaje}")
            else:
                resultado, mensaje = generar_sugerencia_diagnostico(st.session_state['id_usuario'], perfil['ciudad'])
                if resultado in ["Insuficiente", "Error"]:
                    st.warning(mensaje)
                else:
                    st.balloons()
                    st.success(f"{DICCIONARIO[idioma]['ia_posible_sens'].format(resultado=resultado)}")
                    st.info(mensaje)

    
    # SECCIÓN 5: EXPORTAR HISTORIAL A PDF
    
    st.divider()
    st.subheader(DICCIONARIO[idioma]["ttl_exportar"])
    col_pdf1, col_pdf2 = st.columns([2, 1])
        
    with col_pdf1:
        st.write(DICCIONARIO[idioma]["txt_exportar"])
        
    with col_pdf2:
        if st.button(DICCIONARIO[idioma]["btn_pdf"], use_container_width=True):
            from scripts.generador_pdf import exportar_pdf
            alergia_usr = perfil['alergia_principal'] if perfil['diagnosticado'] == "Si" else None
                
            with st.spinner(DICCIONARIO[idioma]["st_pdf"]):
                exito, resultado = exportar_pdf(st.session_state['id_usuario'], perfil['ciudad'], alergia_usr)
                
            if exito:
                with open(resultado, "rb") as f:
                    st.download_button(
                        label=DICCIONARIO[idioma]["btn_descarga"],
                        data=f,
                        file_name=os.path.basename(resultado),
                        mime="application/pdf",
                        use_container_width=True
                    )
                st.success(DICCIONARIO[idioma]["inf_listo"])
            else:
                st.error(f"{DICCIONARIO[idioma]['err_pdf']}{resultado}")
else:

    # PANTALLA: LOGIN / REGISTRO (SI NO ESTÁ LOGUEADO)
    
    st.title(DICCIONARIO[idioma]["titulo_principal"])
    choice = st.sidebar.selectbox(DICCIONARIO[idioma]["menu_acceso"], ["Login", "Registro"])
    
    if choice == "Login":
        st.subheader(DICCIONARIO[idioma]["sub_login"])
        u = st.text_input(DICCIONARIO[idioma]["lbl_usuario"])
        p = st.text_input(DICCIONARIO[idioma]["lbl_pass"], type='password')
        if st.button(DICCIONARIO[idioma]["btn_entrar"]):
            if validar_login(u, p):
                st.session_state['logueado'] = True
                st.session_state['id_usuario'] = u
                st.session_state['perfil'] = obtener_perfil_usuario(u)
                st.rerun()
            else: 
                st.error(DICCIONARIO[idioma]["err_login"])

    elif choice == "Registro":
        st.subheader(DICCIONARIO[idioma]["sub_registro"])
        st.caption(DICCIONARIO[idioma]["cap_obligatorios"])
        
        new_u = st.text_input(DICCIONARIO[idioma]["lbl_usuario_req"]).strip()
        new_p = st.text_input(DICCIONARIO[idioma]["lbl_pass_req"], type='password').strip()
        
        opciones_ciudades = [DICCIONARIO[idioma]["sel_ciudad"]] + list(municipios.keys())
        c = st.selectbox(DICCIONARIO[idioma]["lbl_ciudad"], opciones_ciudades)
        
        e = st.number_input(DICCIONARIO[idioma]["lbl_edad"], min_value=0, max_value=100, value=0, help=DICCIONARIO[idioma]["hlp_edad"])
        
        opciones_diag = [DICCIONARIO[idioma]["sel_opcion"], DICCIONARIO[idioma]["opc_no"], DICCIONARIO[idioma]["opc_si"]]
        d = st.radio(DICCIONARIO[idioma]["lbl_diag"], opciones_diag)
        
        p_esp = "No diagnosticado"
        
        if d == "Sí" or d == "Bai":
            opciones_alergias = [DICCIONARIO[idioma]["sel_alergia"]] + list(umbrales_polen.keys())
            p_esp = st.selectbox(DICCIONARIO[idioma]["lbl_alergia"], opciones_alergias)
            
        if st.button(DICCIONARIO[idioma]["btn_registrar"]):
            errores = []
            if not new_u: errores.append(DICCIONARIO[idioma]["err_u_vacio"])
            if not new_p: errores.append(DICCIONARIO[idioma]["err_p_vacio"])
            if c == DICCIONARIO[idioma]["sel_ciudad"]: errores.append(DICCIONARIO[idioma]["err_c_vacio"])
            if e <= 0: errores.append(DICCIONARIO[idioma]["err_e_invalida"])
            if d == DICCIONARIO[idioma]["sel_opcion"]: errores.append(DICCIONARIO[idioma]["err_d_vacio"])
            if (d == "Sí" or d == "Bai") and p_esp == DICCIONARIO[idioma]["sel_alergia"]:
                errores.append(DICCIONARIO[idioma]["err_a_vacio"])
                
            if errores:
                for error in errores: st.error(error)
            else:
                tiene_diag_bool = (d == "Sí" or d == "Bai")
                exito, msg = registrar_usuario(new_u, new_p, c, e, tiene_diag_bool, p_esp)
                if exito: st.success(msg)
                else: st.error(msg)