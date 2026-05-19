from fpdf import FPDF
import pandas as pd
import datetime
import os
import numpy as np
from scripts.analizador_diagnostico import generar_sugerencia_diagnostico

class InformePolen(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Informe de Seguimiento Alergológico - IA Polen Euskadi', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()} - Documento generado por Sistema TFG IA', 0, 0, 'C')

def exportar_pdf(id_usuario, ciudad, alergia_asignada=None):
    try:
        # 1. CARGA DE DATOS
        df_s = pd.read_csv('datos_usuarios/registro_sintomas.csv', sep=';')
        df_p = pd.read_csv('datos_procesados/polen_euskadi_final.csv', sep=';')

        df_s['fecha'] = pd.to_datetime(df_s['fecha'], format='mixed').dt.date
        df_p['Fecha'] = pd.to_datetime(df_p['Fecha'], format='mixed').dt.date
        
        user_data = df_s[df_s['id_usuario'] == id_usuario].copy()
        if user_data.empty:
            return False, "No hay datos suficientes."

        # 2. CRUCE DE DATOS
        df_ciudad = df_p[df_p['Ciudad'] == ciudad]
        df_final = pd.merge(user_data, df_ciudad, left_on='fecha', right_on='Fecha', how='left')
        
        # 3. LÓGICA DE IA: DOBLE VALIDACIÓN (Lo nuevo que pedías)
        # Paso A: Consultamos a la IA qué polen es el más sospechoso este mes
        alergia_ia, mensaje_ia, valor_r_ia = generar_sugerencia_diagnostico(id_usuario, ciudad)
        valor_r_ia = df_final['malestar'].corr(df_final[alergia_ia]) if alergia_ia in df_final.columns else 0.0
        valor_r_ia = 0.0 if np.isnan(valor_r_ia) else valor_r_ia

        # Paso B: Comparamos con la alergia del perfil si existe
        if alergia_asignada:
            alergia_sospechosa = alergia_asignada # En la tabla mostraremos su alergia oficial
            valor_r = df_final['malestar'].corr(df_final[alergia_asignada])
            valor_r = 0.0 if np.isnan(valor_r) else valor_r
            
            # Si la IA encuentra otro polen con más fuerza, preparamos la alerta
            if alergia_ia != alergia_asignada and valor_r_ia > valor_r:
                texto_ia = (f"AVISO: Aunque su perfil indica alergia a {alergia_asignada}, "
                            f"la IA detecta una correlación mayor con {alergia_ia} ({valor_r_ia:.2f}). "
                            "Esto podría sugerir una nueva sensibilidad o alergia cruzada.")
            else:
                texto_ia = f"El análisis confirma la relación con su alergia habitual: {alergia_asignada}. {mensaje_ia}"
        else:
            # Si no tiene alergia previa, usamos 100% lo que diga la IA
            alergia_sospechosa = alergia_ia
            valor_r = valor_r_ia
            texto_ia = mensaje_ia

        # 4. CONFIGURACIÓN DEL PDF
        pdf = InformePolen()
        pdf.add_page()
        
        # Bloque de Información General
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, f"Usuario: {id_usuario} | Ciudad: {ciudad} | Informe al: {datetime.date.today()}", 1, 1, 'L', True)
        pdf.ln(5)

        # 5. TABLA DE REGISTROS DIARIOS
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, f"Historial Diario y Niveles de {alergia_sospechosa}", 0, 1)
        pdf.set_font("Arial", size=9)
        
        # Cabeceras (ajustamos anchos para la nueva columna)
        pdf.cell(22, 8, "Fecha", 1, 0, 'C', True)
        pdf.cell(18, 8, "Malestar", 1, 0, 'C', True)
        pdf.cell(25, 8, f"Nivel {alergia_sospechosa[:5]}", 1, 0, 'C', True) # Columna nueva
        pdf.cell(25, 8, "Medicación", 1, 0, 'C', True)
        pdf.cell(100, 8, "Comentarios", 1, 1, 'C', True)

        # Filas de datos (últimos 15 registros para que quepan bien)
        pdf.set_font("Arial", size=8)
        for index, row in df_final.sort_values('fecha', ascending=False).head(15).iterrows():
            # Tarea 1: Manejo de "Sin comentarios"
            comentario = str(row['comentarios']) if pd.notna(row['comentarios']) and str(row['comentarios']).strip() != "" else "Sin comentarios"
            
            # Tarea 3: Nivel de polen de ese día
            nivel_polen = f"{row[alergia_sospechosa]:.1f}" if (alergia_sospechosa in row and pd.notna(row[alergia_sospechosa])) else "N/A"
            pdf.cell(22, 8, str(row['fecha']), 1)
            pdf.cell(18, 8, f"{row['malestar']}/10", 1, 0, 'C')
            pdf.cell(25, 8, nivel_polen, 1, 0, 'C') 
            pdf.cell(25, 8, str(row['medicacion']), 1)
            pdf.cell(100, 8, comentario[:65], 1, 1)

        # 6. ANÁLISIS AUTOMÁTICO DE CORRELACIÓN (Tarea 2)
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 51, 102) # Azul oscuro profesional
        pdf.cell(0, 10, "ANÁLISIS AUTOMÁTICO DE CORRELACIÓN (IA)", 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=10)
        
        # Redacción del análisis según los datos
        if valor_r > 0.6:
            grado = "MUY ALTA"
            consejo = f"Existe una coincidencia clara entre el malestar y la presencia de {alergia_sospechosa}."
        elif valor_r > 0.3:
            grado = "MODERADA"
            consejo = f"Se observa cierta relación con {alergia_sospechosa}, aunque podrían influir otros factores."
        else:
            grado = "BAJA"
            consejo = "No se observa una relación clara con los pólenes analizados actualmente."

        texto_ia = (f"Tras analizar la serie temporal de síntomas y los niveles ambientales de polen en {ciudad}, "
                    f"el sistema ha detectado una correlación {grado} con el polen tipo: {alergia_sospechosa.upper()}.\n\n"
                    f"Índice de coincidencia estadística (Pearson): {valor_r:.2f}\n"
                    f"Nota para el facultativo: {consejo}")
        
        pdf.set_fill_color(245, 250, 255)
        pdf.multi_cell(0, 8, texto_ia, 1, 'L', True)

        # 7. GUARDAR ARCHIVO
        nombre_archivo = f"informe_{id_usuario}_{datetime.date.today()}.pdf"
        if not os.path.exists('datos_usuarios'): os.makedirs('datos_usuarios')
        ruta_pdf = f"datos_usuarios/{nombre_archivo}"
        pdf.output(ruta_pdf)
        
        return True, ruta_pdf

    except Exception as e:
        return False, f"Error al generar PDF: {str(e)}"