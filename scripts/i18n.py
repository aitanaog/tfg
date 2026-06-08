# =========================================================================
# DICCIONARIO- Castellano / Euskara
# =========================================================================
DICCIONARIO = {
    "Castellano": {
        # General y Acceso
        "selector_idioma": "Idioma / Hizkuntza",
        "menu_acceso": "Acceso",
        "titulo_principal": "🌿 PolenGune: Control de Alergias Euskadi",
        "sub_login": "Iniciar Sesión",
        "lbl_usuario": "Usuario",
        "lbl_usuario_req": "Usuario *",
        "lbl_pass": "Contraseña",
        "lbl_pass_req": "Contraseña *",
        "btn_entrar": "Entrar",
        "err_login": "Credenciales incorrectas",
        "sub_registro": "Crear nueva cuenta",
        "cap_obligatorios": "Todos los campos de este formulario son obligatorios",
        "lbl_ciudad": "Ciudad *",
        "sel_ciudad": "Seleccione una ciudad...",
        "lbl_edad": "Edad *",
        "hlp_edad": "Introduzca una edad válida mayor que 0",
        "lbl_diag": "¿Está diagnosticado de alguna alergia? *",
        "sel_opcion": "Seleccione una opción...",
        "lbl_alergia": "Alergia principal *",
        "sel_alergia": "Seleccione su alergia principal...",
        "btn_registrar": "Registrarme",
        
        # Errores del formulario de registro
        "err_u_vacio": "El campo 'Usuario' no puede estar vacío.",
        "err_p_vacio": "El campo 'Contraseña' no puede estar vacío.",
        "err_c_vacio": "Debe seleccionar una 'Ciudad' de la lista.",
        "err_e_invalida": "Debe introducir una 'Edad' válida (mayor que 0).",
        "err_d_vacio": "Debe responder a la pregunta '¿Diagnosticado?'.",
        "err_a_vacio": "Ha marcado que sí está diagnosticado, debe seleccionar su 'Alergia principal'.",
        
        # Sidebar y Header (Logueado)
        "hdr_cuenta": "⚙️ Mi Cuenta",
        "txt_usuario": "👤 **Usuario:** ",
        "txt_ciudad": "📍 **Ciudad:** ",
        "btn_logout": "Cerrar Sesión",
        "st_sincro": "Sincronizando con estaciones y ejecutando predicción...",
        "err_sincro": "Error en la actualización de datos: ",
        "ttl_panel": "🌿 Panel de Control - ",
        "inf_consulta": "📅 **Día de consulta:** ",
        "btn_editar_perfil": "⚙️ Editar Perfil",
        "txt_alergia": "Alergia:",
        
        # Modo A: Diagnosticado
        "sub_critico": "📊 Seguimiento Crítico: ",
        "lbl_otros": "🌐 Otros niveles en tu zona (Hoy)",
        "sub_manana": "### 🛡️ Estado para mañana",
        "alt_critica": "⚠️ **ALERTA CRÍTICA:** Nivel ",
        "alt_mod": "🔔 **PRECAUCIÓN:** Niveles moderados para mañana.",
        "alt_baja": "✅ **DÍA TRANQUILO:** Niveles bajos de ",
        "sub_recom": "### 📋 Recomendaciones",
        "rec_alto": ["- Use mascarilla FFP2 en exteriores.", "- Evite hacer deporte al aire libre."],
        "rec_mod": ["- Ventile la casa solo al amanecer o atardecer.", "- Use gafas de sol."],
        "rec_bajo": ["- Puede realizar actividades normales."],
        
        # Modo B: No Diagnosticado
        "sub_hoy": "🔎 Estado de los Pólenes Hoy",
        "txt_hoy": "A continuación se muestran las especies con niveles significativos en tu ciudad.",
        "lbl_mod_alt": "### ⚠️ Niveles Moderados / Altos",
        "lbl_bajos": "### 🟢 Niveles Bajos",
        "txt_tranquilo": "No hay niveles de riesgo detectados para hoy. ¡Día tranquilo!",
        
        # Asistente de IA
        "ttl_asistente": "🧬 Asistente de Diagnóstico ",
        "txt_asistente_diag": "¿Sigues notando malestar incluso con niveles bajos de {alergia}? Analizaremos si estás desarrollando una nueva sensibilidad.",
        "txt_asistente_nodo": "¿Notas malestar pero no sabes a qué polen? Analizaremos tus últimos 30 días.",
        "btn_analizar": "🚀 Iniciar Análisis de Inteligencia Artificial",
        "st_analizando": "Analizando correlaciones...",
        "st_analizando_pats": "Analizando correlaciones y patrones clínicos...",
        "ia_confirmada": "### ✅ Relación Confirmada",
        "ia_msg_conf": "El motor analítico corrobora que tus síntomas actuales siguen fuertemente ligados a tu alergia principal a **{alergia}**. ",
        "ia_nueva_sens": "### ⚠️ Alerta de Nueva Sensibilidad: **{resultado}**",
        "ia_msg_nueva": "**¡Atención!** Aunque tu perfil indica que estás diagnosticado de *{alergia}*, nuestro motor inteligente ha detectado que tus síntomas de las últimas semanas guardan una relación mucho más estrecha con los niveles ambientales de **{resultado}**. Esto podría sugerir el desarrollo de una **alergia cruzada** o una nueva hipersensibilidad estacional.\n\n*Detalles del análisis:* ",
        "ia_posible_sens": "### 🎯 Posible sensibilidad: **{resultado}** ",
        
        # Diario de Síntomas
        "ttl_diario": "📝 Diario de Síntomas",
        "inf_diario": "Registra tu estado diario para ayudar a la IA a entender cómo te afectan los niveles de polen.",
        "lbl_malestar": "Nivel de malestar general",
        "hlp_malestar": "0: Sin síntomas, 10: Malestar extremo",
        "lbl_seleccion": "**Selecciona los síntomas que presentas hoy:**",
        "lbl_med": "¿Has tomado medicación?",
        "lbl_comentarios": "Notas adicionales (ej: 'Mucho tiempo al aire libre')",
        "btn_diario": "Guardar Registro Diario",
        "err_diario_vacio": "❌ No se puede guardar un registro vacío. Por favor, selecciona tu nivel de malestar o marca algún síntoma.",
        
        # Exportar PDF
        "ttl_exportar": "📂 Exportar Historial Médico",
        "txt_exportar": "Genera un documento PDF profesional con la evolución de tus síntomas y niveles de polen para facilitar el diagnóstico de tu alergólogo.",
        "btn_pdf": "📄 Generar Informe PDF",
        "st_pdf": "Compilando datos y generando PDF...",
        "btn_descarga": "📥 Descargar ahora",
        "inf_listo": "¡Informe listo!",
        "err_pdf": "No se pudo generar el informe: "
    },
    "Euskara": {
        # General y Acceso
        "selector_idioma": "Idioma / Hizkuntza",
        "menu_acceso": "Sarbidea",
        "titulo_principal": "🌿 PolenGune: Alergien Kontrola Euskadin",
        "sub_login": "Saioa Hasi",
        "lbl_usuario": "Erabiltzailea",
        "lbl_usuario_req": "Erabiltzailea *",
        "lbl_pass": "Pasahitza",
        "lbl_pass_req": "Pasahitza *",
        "btn_entrar": "Sartu",
        "err_login": "Kredentzial okerrak",
        "sub_registro": "Kontu berria sortu",
        "cap_obligatorios": "Formulario honetako eremu guztiak derrigorrezkoak dira",
        "lbl_ciudad": "Hiria *",
        "sel_ciudad": "Hautatu hiri bat...",
        "lbl_edad": "Adina *",
        "hlp_edad": "Sartu 0 baino handiagoa den baliozko adina",
        "lbl_diag": "Alergiarik diagnostikatu dizute? *",
        "sel_opcion": "Hautatu aukera bat...",
        "lbl_alergia": "Alergia nagusia *",
        "sel_alergia": "Hautatu zure alergia nagusia...",
        "btn_registrar": "Erregistratu",
        
        # Errores del formulario de registro
        "err_u_vacio": "'Erabiltzailea' eremua ezin da hutsik egon.",
        "err_p_vacio": "'Pasahitza' eremua ezin da hutsik egon.",
        "err_c_vacio": "Zerrendako 'Hiria' bat hautatu behar duzu.",
        "err_e_invalida": "Baliozko 'Adina' sartu behar duzu (0 baino handiagoa).",
        "err_d_vacio": "'Diagnostikatua?' galderari erantzun behar diozu.",
        "err_a_vacio": "Diagnostikatuta zaudela markatu duzu, zure 'Alergia nagusia' hautatu behar duzu.",
        
        # Sidebar y Header (Logueado)
        "hdr_cuenta": "⚙️ Nire Kontua",
        "txt_usuario": "👤 **Erabiltzailea:** ",
        "txt_ciudad": "📍 **Hiria:** ",
        "btn_logout": "Saioa Itxi",
        "st_sincro": "Estazioekin sinkronizatzen eta aurreikuspena exekutatzen...",
        "err_sincro": "Errorea datuak eguneratzean: ",
        "ttl_panel": "🌿 Kontrol Panela - ",
        "inf_consulta": "📅 **Kontsulta eguna:** ",
        "btn_editar_perfil": "⚙️ Profila Editatu",
        "txt_alergia": "Alergia:",
        
        # Modo A: Diagnosticado
        "sub_critico": "📊 Jarraipen Kritikoa: ",
        "lbl_otros": "🌐 Beste polen mailak zure eremuan (Gaur)",
        "sub_manana": "### 🛡️ Biharreko egoera",
        "alt_critica": "⚠️ **ALERTA KRITIKOA:** Maila ",
        "alt_mod": "🔔 **KONTUZ:** Maila moderatuak biharko.",
        "alt_baja": "✅ **EGUN LASAIA:** Polen maila baxuak: ",
        "sub_recom": "### 📋 Gomendioak",
        "rec_alto": ["- Erabili FFP2 maskara kanpoaldean.", "- Saihestu kirola egitea aire librean."],
        "rec_mod": ["- Aireztatu etxea egunsentian edo ilunabarrean soilik.", "- Erabili eguzkitako betaurrekoak."],
        "rec_bajo": ["- Jarduera normalak egin ditzakezu."],
        
        # Modo B: No Diagnosticado
        "sub_hoy": "🔎 Polen Mailaren Egoera Gaur",
        "txt_hoy": "Jarraian, zure hirian maila adierazgarriak dituzten espezieak ageri dira.",
        "lbl_mod_alt": "### ⚠️ Maila Moderatuak / Altuak",
        "lbl_bajos": "### 🟢 Maila Baxuak",
        "txt_tranquilo": "Ez da arrisku mailarik detektatu gaurko. Egun lasaia!",
        
        # Asistente de IA
        "ttl_asistente": "🧬 Diagnostiko Laguntzailea ",
        "txt_asistente_diag": "Ondoeza nabaritzen jarraitzen duzu {alergia} maila baxuekin ere? Sentikortasun berri bat garatzen ari zaren aztertuko dugu.",
        "txt_asistente_nodo": "Ondoeza nabaritzen duzu baina ez dakizu zein polenekiko? Zure azken 30 egunak aztertuko ditugu.",
        "btn_analizar": "🚀 Adimen Artifizialaren Azterketa Hasi",
        "st_analizando": "Korrelazioak aztertzen...",
        "st_analizando_pats": "Korrelazioak eta eredu klinikoak aztertzen...",
        "ia_confirmada": "### ✅ Harremana Baieztatuta",
        "ia_msg_conf": "Analisi-motorrak egiaztatu du zure egungo sintomek lotura estua izaten jarraitzen dutela zure alergia nagusiarekin: **{alergia}**. ",
        "ia_nueva_sens": "### ⚠️ Sentikortasun Berriaren Alerta: **{resultado}**",
        "ia_msg_nueva": "**Adi!** Zure profilak *{alergia}* alergia duzula adierazten duen arren, gure motor adimendunak detektatu du azken asteetako sintomek lotura estuagoa dutela **{resultado}** ingurune-mailekin. Horrek alergia gurutzatu bat edo urtaroko hipersentikortasun berri bat iradoki dezake.\n\n*Analisiaren xehetasunak:* ",
        "ia_posible_sens": "### 🎯 Sentikortasun posiblea: **{resultado}** ",
        
        # Diario de Síntomas
        "ttl_diario": "📝 Sintomen Egunkaria",
        "inf_diario": "Erregistratu zure eguneroko egoera adimen artifizialari laguntzeko polen mailak nola eragiten dizun ulertzen.",
        "lbl_malestar": "Egoera orokorraren ondoeza",
        "hlp_malestar": "0: Sintomarik gabe, 10: Muturreko ondoeza",
        "lbl_seleccion": "**Hautatu gaur dituzun sintomak:**",
        "lbl_med": "Medikaziorik hartu duzu?",
        "lbl_comentarios": "Ohar gehigarriak (adib: 'Denbora asko aire librean')",
        "btn_diario": "Gorde Eguneroko Erregistroa",
        "err_diario_vacio": "❌ Ezin da erregistro huts bat gorde. Mesedez, hautatu zure ondoeza maila edo markatu sintomaren bat.",
        
        # Exportar PDF
        "ttl_exportar": "📂 Historial Medikoa Esportatu",
        "txt_exportar": "Sortu PDF dokumentu profesional bat zure sintomen eta polen mailen bilakaerarekin, zure alergologoak diagnostikoa errazago egin dezan.",
        "btn_pdf": "📄 PDF Txostena Sortu",
        "st_pdf": "Datuak biltzen eta PDFa sortzen...",
        "btn_descarga": "📥 Deskargatu orain",
        "inf_listo": "Txostena prest!",
        "err_pdf": "Ezin izan da txostena sortu: "
    }
}