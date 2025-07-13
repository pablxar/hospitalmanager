import flet as ft
import sqlite3
import shutil
import os
import tempfile
from zipfile import ZipFile
from components.reportlab_generator import generar_pdf
import asyncio

class PopupReportGenerator:
    def __init__(self, page: ft.Page, user, db_path: str):
        self.page = page
        self.user = user
        self.db_path = db_path

        # UI components
        self.progress_bar = ft.ProgressBar(width=400, value=0, visible=False)
        self.progress_text = ft.Text("0/0", size=16, visible=False)
        self.error_text = ft.Text("", color=ft.Colors.RED, visible=False)
        self.download_btn = ft.ElevatedButton("Descargar Informe", visible=False, on_click=self.download_report)
        self.upload_btn = ft.ElevatedButton("Seleccionar Análisis", on_click=self.populate_analysis_dropdown) # This button will open the file picker
        self.close_btn = ft.IconButton(icon=ft.Icons.CLOSE, on_click=self.close_popup)

        # Dropdown para seleccionar el análisis
        self.dropdown = ft.Dropdown(label="Selecciona un análisis", on_change=self.on_analysis_selected)

        # Populate dropdown with analyses from database
        self.populate_analysis_dropdown()

        # Progress text and bars
        self.status_text = ft.Text("", size=16, color=ft.Colors.AMBER, visible=False)
        self.indeterminate_bar = ft.ProgressBar(width=400, visible=False, color=ft.Colors.AMBER, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.AMBER), bar_height=4, value=None)

        # Popup dialog definition
        self.popup = ft.AlertDialog(
            modal=True,
            open=False,
            content=ft.Column([ 
                ft.Row([ft.Text("Generación de Informe", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER), self.close_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.dropdown,
                self.upload_btn,
                self.status_text,
                self.indeterminate_bar,
                self.progress_bar,
                self.progress_text,
                self.error_text,
                self.download_btn
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        # Agregar FilePicker al inicio
        self.file_picker = ft.FilePicker(on_result=self.save_report_to_path)
        self.page.overlay.append(self.file_picker)

    def populate_analysis_dropdown(self, *args):
        """Populate the dropdown with available analysis options from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM analyses WHERE usuario_id = ?", (self.user[0],))
        analyses = cursor.fetchall()
        conn.close()
        self.dropdown.options = [ft.DropdownOption(str(analysis[0]), analysis[1]) for analysis in analyses]
    
    def on_analysis_selected(self, e):
        """Handle analysis selection from the dropdown."""
        selected_analysis_id = self.dropdown.value
        if selected_analysis_id:
            # Limpiar el popup
            self.upload_btn.visible = False
            self.download_btn.visible = False
            self.progress_bar.value = 0
            self.progress_bar.visible = True
            self.progress_text.value = "Generando el informe..."
            self.progress_text.visible = True
            self.status_text.value = "Generando el informe..."
            self.status_text.visible = True
            self.page.update()

            # Retrieve and extract the selected analysis zip
            self.retrieve_analysis_zip(selected_analysis_id)

            # Cuando el informe esté listo
            self.progress_bar.visible = False
            self.progress_text.visible = False
            self.status_text.visible = False
            self.download_btn.visible = True
            self.page.update()

    def retrieve_analysis_zip(self, selected_analysis_id):
        """Retrieve the .zip file from the database and process it."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT file_content FROM analyses WHERE id = ?", (selected_analysis_id,))
        analysis_data = cursor.fetchone()
        conn.close()

        if not analysis_data:
            self.error_text.value = "No se encontró el análisis seleccionado."
            self.error_text.visible = True
            self.page.update()
            return

        # Create temp directory and save the zip file
        temp_base_dir = os.path.join('storage', 'data', 'temp')
        os.makedirs(temp_base_dir, exist_ok=True)

        zip_path = os.path.join(temp_base_dir, f"analysis_{selected_analysis_id}.zip")
        with open(zip_path, 'wb') as zip_file:
            zip_file.write(analysis_data[0])

        # Extract zip contents
        extract_path = f"storage/temp/analysis_{selected_analysis_id}/"
        self.extract_zip(zip_path, extract_path)

    def extract_zip(self, zip_path, extract_path):
        """Extract the contents of the .zip file."""
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        # Process extracted files (graphics and tables)
        self.process_files(extract_path)
    
    def show_snackbar(self, text, bgcolor=ft.Colors.AMBER):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(text),
            bgcolor=bgcolor,
            behavior=ft.SnackBarBehavior.FLOATING
        )
        self.page.snack_bar.open = True
        self.page.update()


    def process_files(self, extract_path):
        """Process the extracted files (graphics and tables)."""
        graphics = []
        tables = []

        # Define the analysis types
        analysis_types = ["clinico", "cohortes", "economico", "produccion"]

        # Search for graphics and tables in the extracted directories
        for analysis_type in analysis_types:
            graphics_path = f"{extract_path}/{analysis_type}/graficos"
            tables_path = f"{extract_path}/{analysis_type}/tablas"

            if os.path.exists(graphics_path):
                graphics.extend([os.path.join(graphics_path, f) for f in os.listdir(graphics_path) if f.endswith('.png')])

            if os.path.exists(tables_path):
                tables.extend([os.path.join(tables_path, f) for f in os.listdir(tables_path) if f.endswith('.png')])

        if not graphics:
            self.show_snackbar("No se encontraron gráficos en el análisis seleccionado.", ft.Colors.RED)
            return

        if not tables:
            self.show_snackbar("No se encontraron tablas en el análisis seleccionado.", ft.Colors.RED)
            return

        # Asegurar consistencia en el flujo visual y de interacción
        self.status_text.value = "Generando el informe..."
        self.status_text.visible = True
        self.indeterminate_bar.visible = True
        self.progress_bar.visible = False
        self.progress_text.visible = False
        self.download_btn.visible = False
        self.page.update()

        # Generar el informe
        pdf_path = self.generate_report_pdf(graphics, tables)
        self.pdf_path = pdf_path  # Guardar la ruta del PDF generado

        # Actualizar estado tras la generación
        self.indeterminate_bar.visible = False
        self.status_text.visible = False
        self.download_btn.visible = True
        self.page.update()

        # Mostrar snackbar tras guardar
        self.show_snackbar("Informe generado exitosamente.", ft.Colors.GREEN)

        # Save the report in the database
        self.save_report_to_db(f"Informe_{self.user[0]}", pdf_path)

    def generate_report_pdf(self, graphics, tables):
        """Genera el informe en formato PDF utilizando ReportLab."""
        # Crear un directorio temporal para almacenar las imágenes
        temp_dir = tempfile.mkdtemp()

        # Copiar gráficos y tablas al directorio temporal
        for file in graphics + tables:
            if os.path.exists(file):
                shutil.copy(file, temp_dir)
            else:
                raise FileNotFoundError(f"El archivo {file} no existe.")

        if not self.dropdown.value:
            raise ValueError("No se seleccionó un análisis válido en el dropdown.")

        pdf_path = os.path.join('storage', 'temp', f'report_{self.dropdown.value}.pdf')
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        try:
            generar_pdf(self.dropdown.value, temp_dir, os.path.dirname(pdf_path))
        except Exception as e:
            raise RuntimeError(f"Error al generar el PDF: {str(e)}")

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"El archivo PDF no se generó correctamente en {pdf_path}. Verifique la ruta y el módulo de generación.")

        return pdf_path

    def save_report_to_db(self, report_name, pdf_path):
        """Save the generated report PDF to the database."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        with open(pdf_path, 'rb') as f:
            blob = f.read()
        cur.execute(
            "INSERT INTO reports (name, date, report) VALUES (?, DATE('now'), ?)",
            (report_name, blob)
        )
        conn.commit()
        conn.close()

    def show_popup(self):
        self.popup.alignment = ft.alignment.center

        if self.popup not in self.page.overlay:
            self.page.overlay.append(self.popup)

        self.popup.open = True
        self.page.dialog = self.popup
        self.page.update()

    def close_popup(self, e):
        self.reset_status()
        self.popup.open = False
        self.page.update()

    def download_report(self, e):
        """Download the generated report."""
        if not self.download_btn.visible:
            self.show_snackbar("No hay ningún informe disponible para descargar.", ft.Colors.RED)
            return

        # Mostrar diálogo para elegir la ruta de descarga
        self.show_snackbar("Seleccione la ruta para guardar el informe.", ft.Colors.AMBER)

        # Esperar a que el usuario seleccione la ruta
        self.file_picker.save_file(file_name=f"report_{self.dropdown.value}.pdf")

    def save_report_to_path(self, e):
        """Guardar el informe en la ruta seleccionada y mostrar snackbar."""
        if e.path:
            try:
                temp_dir = os.path.dirname(self.pdf_path)

                # Validar existencia del archivo PDF antes de copiar
                if not os.path.exists(self.pdf_path):
                    self.show_snackbar("El archivo PDF no existe.", ft.Colors.RED)
                    return

                # Copiar el archivo PDF a la ruta seleccionada
                shutil.copy(self.pdf_path, e.path)

                # Validar existencia de la carpeta temporal antes de eliminar
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

                self.show_snackbar("Informe guardado correctamente.", ft.Colors.GREEN)
            except Exception as ex:
                self.show_snackbar("Error al guardar el informe.", ft.Colors.RED)
        else:
            self.show_snackbar("No se seleccionó ninguna ruta para guardar el informe.", ft.Colors.RED)

    def reset_status(self):
        """Reset the status and UI elements."""
        self.current_step = 0
        self.total_steps = 0
        self.progress_bar.value = 0
        self.progress_bar.visible = False
        self.progress_text.value = ""
        self.progress_text.visible = False
        self.error_text.value = ""
        self.error_text.visible = False
        self.download_btn.visible = False
        self.download_btn.disabled = True
        self.upload_btn.visible = True
        self.status_text.value = ""
        self.status_text.visible = False
        self.indeterminate_bar.visible = False
        self.page.update()

    def update_progress(self, etapa=None):
        """Actualizar la barra de progreso."""
        self.current_step += 1
        self.progress_bar.value = self.current_step / self.total_steps
        self.progress_text.value = f"{self.current_step}/{self.total_steps}"
        if etapa:
            self.status_text.value = f"Procesando etapa: {etapa.capitalize()}..."
        self.status_text.visible = True
        self.indeterminate_bar.visible = True if self.current_step < self.total_steps else False
        self.page.update()

    def ejecutar_generacion(self, e):
        """Ejecutar la generación del informe."""
        self.reset_status()
        self.upload_btn.visible = False
        self.status_text.value = "Generando el informe..."
        self.status_text.visible = True
        self.indeterminate_bar.visible = True
        self.page.update()

        try:
            # Simular pasos de generación
            self.total_steps = 3
            for etapa in ["Preparación", "Generación", "Finalización"]:
                self.update_progress(etapa)

            self.status_text.value = "Informe listo para descargar."
            self.indeterminate_bar.visible = False
            self.download_btn.visible = True
            self.page.update()
        except Exception as ex:
            self.error_text.value = str(ex)
            self.error_text.visible = True
            self.status_text.visible = False
            self.indeterminate_bar.visible = False
            self.page.update()
