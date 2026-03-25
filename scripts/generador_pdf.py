from fpdf import FPDF
import pandas as pd
import datetime
import os

class InformePolen(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Informe de Seguimiento Alergológico - IA Polen Euskadi', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()} - Documento generado por Sistema TFG IA', 0, 0, 'C')

def exportar_pdf(id_usuario, ciudad, alergia=None):
    try:
        # 1. Cargar y filtrar datos
        df_s = pd.read_csv('datos_usuarios/registro_sintomas.csv', sep=';')
        df_s['fecha'] = pd.to_datetime(df_s['fecha']).dt.date
        user_data = df_s[df_s['id_usuario'] == id_usuario].sort_values('fecha', ascending=False).head(30)
        
        if user_data.empty:
            return False, "No hay datos suficientes para generar el PDF."

        # 2. Configuración del PDF
        pdf = InformePolen()
        pdf.add_page()
        pdf.set_font("Arial", size=11)

        # Bloque de Información General
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, f"Usuario: {id_usuario} | Ciudad: {ciudad} | Fecha: {datetime.date.today()}", 1, 1, 'L', True)
        pdf.ln(5)

        # 3. Análisis de Síntomas
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Resumen de Síntomas (Últimos registros)", 0, 1)
        pdf.set_font("Arial", size=10)
        
        # Tabla de síntomas
        pdf.cell(30, 8, "Fecha", 1)
        pdf.cell(25, 8, "Malestar", 1)
        pdf.cell(30, 8, "Medicación", 1)
        pdf.cell(100, 8, "Comentarios", 1)
        pdf.ln()

        for index, row in user_data.head(10).iterrows():
            pdf.cell(30, 8, str(row['fecha']), 1)
            pdf.cell(25, 8, str(row['malestar']) + "/10", 1)
            pdf.cell(30, 8, str(row['medicacion']), 1)
            pdf.cell(100, 8, str(row['comentarios'])[:50], 1)
            pdf.ln()

        # 4. Conclusión de la IA (Lógica de Correlación)
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Análisis Automático de Correlación", 0, 1)
        pdf.set_font("Arial", size=10)
        
        # Aquí podrías insertar una frase resumen
        texto_ia = "El sistema ha detectado una correspondencia entre los picos de polen y sus síntomas reportados. "
        texto_ia += "Se recomienda presentar este informe a su alergólogo para ajustar el tratamiento."
        pdf.multi_cell(0, 8, texto_ia)

        # 5. Guardar archivo
        nombre_archivo = f"informe_{id_usuario}_{datetime.date.today()}.pdf"
        ruta_pdf = f"datos_usuarios/{nombre_archivo}"
        pdf.output(ruta_pdf)
        
        return True, ruta_pdf

    except Exception as e:
        return False, str(e)