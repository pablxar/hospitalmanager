from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def generar_pdf(nombre_analisis, ruta_imagenes, ruta_salida):
    """
    Genera un informe PDF a partir de imágenes extraídas de un análisis.

    :param nombre_analisis: Nombre del análisis (variable).
    :param ruta_imagenes: Ruta donde se encuentran las imágenes extraídas.
    :param ruta_salida: Ruta donde se guardará el PDF generado.
    """
    pdf_path = os.path.join(ruta_salida, f"report_{nombre_analisis}.pdf")
    nombre_analisis = nombre_analisis.split('_')[-1]  # Extraer solo el identificador del análisis
    c = canvas.Canvas(pdf_path, pagesize=letter)

    # Título del informe
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, f"Informe del Análisis: {nombre_analisis}")

    # Insertar imágenes
    y_position = 700
    for root, _, files in os.walk(ruta_imagenes):
        for file in sorted(files):  # Asegurarse de un orden consistente
            if file.endswith(".png"):
                image_path = os.path.join(root, file)
                if y_position < 100:  # Nueva página si no hay espacio
                    c.showPage()
                    y_position = 750
                c.drawImage(image_path, 50, y_position - 200, width=500, height=200, preserveAspectRatio=True, anchor='c')
                c.drawString(50, y_position - 220, file)  # Nombre de la imagen
                y_position -= 250

    c.save()
    return pdf_path
