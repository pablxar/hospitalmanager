import sys
import os

# Add the root directory to the Python module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import flet as ft
from components.notifications import NotificationsManager
from database import DatabaseManager

class AnalyticsView(ft.Container):
    def __init__(self, page: ft.Page, bg_color: str, text_color: str, white_color: str, notify_color: str, text_color2: str, notifications_manager: NotificationsManager, user):
        super().__init__(expand=True)
        self.page = page
        self.bg_color = bg_color
        self.text_color = text_color
        self.white_color = white_color
        self.notify_color = notify_color
        self.text_color2 = text_color2
        self.page.bgcolor = bg_color
        self.notifications_manager = notifications_manager
        self.user = user

        self.db_manager = DatabaseManager()
        self.file_picker = ft.FilePicker()
        self.page.overlay.append(self.file_picker)
        
        self.delete_dialog = None  # Atributo para rastrear el diálogo de eliminación
        self.download_dialog = None  # Atributo para rastrear el diálogo de descarga
        
        # Contenido principal con pestañas
        self.tabs = ft.Tabs(
            scrollable= ft.ScrollMode.AUTO,
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Nuevo Análisis", content=self.create_new_analysis_section()),
                ft.Tab(text="Historial", content=self.create_history_section())
            ],
            expand=True
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,  # Scroll controlado
            expand=True,
            controls=[
                self.create_header(),
                self.create_steps_section(),
                self.tabs
            ]
        )

    def create_header(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("Análisis de Datos", color=self.text_color, size=24, weight=ft.FontWeight.BOLD),
                ft.Icon(ft.Icons.ANALYTICS, color=self.notify_color, size=32)
            ]
        )

    def create_steps_section(self):
        return ft.Container(
            padding=20,
            alignment=ft.alignment.center,
            content=ft.ResponsiveRow(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                run_spacing=20,
                controls=[
                    ft.Container(
                        width=300,
                        height=120,
                        content=self.create_step_box(
                            "Paso 1: Subir Archivo", 
                            "Carga tu archivo de datos hospitalarios", 
                            ft.Icons.UPLOAD_FILE, 
                            "#007BFF"
                        )
                    ),
                    ft.Container(
                        width=300,
                        height=120,
                        content=self.create_step_box(
                            "Paso 2: Validación", 
                            "Verificamos la calidad de los datos", 
                            ft.Icons.VERIFIED, 
                            "#FF5722"
                        )
                    ),
                    ft.Container(
                        width=300,
                        height=120,
                        content=self.create_step_box(
                            "Paso 3: Procesamiento", 
                            "Analizamos automáticamente los datos", 
                            ft.Icons.ANALYTICS, 
                            "#4CAF50"
                        )
                    ),
                    ft.Container(
                        width=300,
                        height=120,
                        content=self.create_step_box(
                            "Paso 4: Visualización", 
                            "Generamos gráficos y reportes", 
                            ft.Icons.BAR_CHART, 
                            "#9C27B0"
                        )
                    )
                ]
            )
        )

    def create_step_box(self, title, description, icon, color):
        return ft.Card(
            elevation=3,
            content=ft.Container(
                bgcolor=self.white_color,
                padding=15,
                border_radius=10,
                content=ft.Column(
                    horizontal_alignment="center",
                    spacing=8,
                    controls=[
                        ft.Icon(name=icon, size=30, color=color),
                        ft.Text(title, size=16, weight="bold", color=self.text_color2),
                        ft.Text(description, size=12, color=self.text_color2, text_align="center")
                    ]
                )
            )
        )

    def create_new_analysis_section(self):
        return ft.Container(
            padding=20,
            content=ft.Column(
                scroll =ft.ScrollMode.AUTO,  # Enable controlled scrolling
                expand=True,
                spacing=25,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # Título
                    ft.Text(
                        "Subir Archivo de Datos", 
                        size=24, 
                        weight="bold", 
                        color=self.white_color
                    ),
                    
                    # Descripción
                    ft.Text(
                        "Sube un archivo Excel (xlsx, xls) o CSV para procesar los datos hospitalarios.",
                        size=16,
                        color=self.white_color,
                        text_align="center"
                    ),
                    
                    ft.Divider(height=1, color="#e0e0e0"),
                    
                    # Área de arrastrar y soltar
                    ft.ResponsiveRow(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                col={"sm": 12, "md": 8, "lg": 6},
                                content=ft.Card(
                                    elevation=5,
                                    content=ft.Container(
                                        padding=30,
                                        border=ft.border.all(2, "#e0e0e0"),
                                        border_radius=10,
                                        bgcolor=self.white_color,
                                        alignment=ft.alignment.center,
                                        content=ft.Column(
                                            horizontal_alignment="center",
                                            spacing=15,
                                            controls=[
                                                ft.Icon(
                                                    name=ft.Icons.CLOUD_UPLOAD,
                                                    size=50,
                                                    color=self.notify_color
                                                ),
                                                ft.Text(
                                                    "Arrastra tu archivo aquí o haz clic para seleccionar",
                                                    size=16,
                                                    color=self.text_color2,
                                                    text_align="center",
                                                    weight="bold"
                                                ),
                                                ft.Text(
                                                    "Archivos esperados: Excel (xlsx, xls) o CSV (máximo 10MB)",
                                                    size=14,
                                                    color=self.text_color2,
                                                    text_align="center"
                                                ),
                                                ft.Container(height=10),
                                                ft.ElevatedButton(
                                                    text="Seleccionar Archivo",
                                                    icon=ft.Icons.FILE_UPLOAD,
                                                    bgcolor=self.notify_color,
                                                    color=self.white_color,
                                                    on_click=self.on_file_select
                                                )
                                            ]
                                        )
                                    )
                                )
                            )
                        ]
                    ),
                    
                    ft.Divider(height=1, color="#e0e0e0"),
                    
                    # Información importante
                    ft.ResponsiveRow(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                col={"sm": 12, "md": 8, "lg": 6},
                                content=ft.Column(
                                    spacing=10,
                                    controls=[
                                        ft.Text(
                                            "Información importante:",
                                            size=18,
                                            weight="bold",
                                            color=self.white_color
                                        ),
                                        ft.Column(
                                            spacing=8,
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon(
                                                            name=ft.Icons.INFO_OUTLINE,
                                                            size=18,
                                                            color=self.notify_color
                                                        ),
                                                        ft.Text(
                                                            "Los archivos deben contener datos de egresos hospitalarios.",
                                                            size=14,
                                                            color=self.white_color
                                                        )
                                                    ]
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon(
                                                            name=ft.Icons.INFO_OUTLINE,
                                                            size=18,
                                                            color=self.notify_color
                                                        ),
                                                        ft.Text(
                                                            "Asegúrate de que las columnas estén correctamente etiquetadas.",
                                                            size=14,
                                                            color=self.white_color
                                                        )
                                                    ]
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon(
                                                            name=ft.Icons.INFO_OUTLINE,
                                                            size=18,
                                                            color=self.notify_color
                                                        ),
                                                        ft.Text(
                                                            "El análisis se iniciará automáticamente después de la subida.",
                                                            size=14,
                                                            color=self.white_color
                                                        )
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            )
                        ]
                    )
                ]
            )
        )
        
    def on_file_select(self, e):
        self.file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["xlsx", "xls", "csv"],
            dialog_title="Seleccionar archivo de datos"
        )

    def create_history_section(self):
        return ft.Container(
            padding=20,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,  # Enable controlled scrolling
                expand=True,
                controls=[
                    ft.Text("Historial", size=20, weight="bold", color=self.white_color),
                    ft.Divider(height=1, color="#e0e0e0"),
                    self.create_report_list()
                ]
            )
        )

    def create_report_list(self):
        analyses = self.db_manager.fetch_analyses_by_user(self.user[0])
        if not analyses:
            return ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(name=ft.Icons.HISTORY, size=50, color=self.white_color),
                    ft.Text("No hay análisis realizados aún", size=16, color=self.white_color)
                ]
            )

        return ft.ListView(
            expand=True,
            spacing=10,
            controls=[
                self.create_report_item(analysis[1], analysis[2], analysis[3], analysis[0])
                for analysis in analyses
            ]
        )
    def create_report_item(self, title: str, date: str, file_content: bytes, analysis_id=None):
            # Asegurarse de que file_content sean los bytes del ZIP, no el ID
        if not isinstance(file_content, bytes):
            raise ValueError("file_content debe ser de tipo bytes")
        return ft.Card(
            elevation=3,
            content=ft.Container(
                padding=15,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            expand=True,
                            controls=[
                                ft.Text(title, size=16, weight="bold", color=self.white_color),
                                ft.Text(f"Fecha: {date}", size=12, color=self.white_color)
                            ]
                        ),
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.DOWNLOAD,
                                    icon_color="#4CAF50",
                                    tooltip="Descargar reporte",
                                    on_click=lambda e: self.show_download_dialog(title, file_content)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color="#F44336",
                                    tooltip="Eliminar reporte",
                                    on_click=lambda e: self.show_delete_dialog(title, analysis_id)
                                )
                            ]
                        )
                    ]
                )
            )
        )
        
    def show_delete_dialog(self, title, analysis_id):
        self.delete_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Estás seguro de que deseas eliminar el análisis '{title}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_dialogs),
                ft.TextButton(
                    "Eliminar", 
                    on_click=lambda e: self.confirm_delete(analysis_id, title),
                    style=ft.ButtonStyle(color=ft.Colors.RED)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(self.delete_dialog)
        self.delete_dialog.open = True
        self.page.update()

    def show_download_dialog(self, title, file_content):
        self.download_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Descargar análisis"),
            content=ft.Text(f"¿Deseas descargar el análisis '{title}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=self.close_dialogs),
                ft.TextButton(
                    "Descargar", 
                    on_click=lambda e: self.download_file(file_content, title),
                    style=ft.ButtonStyle(color=ft.Colors.GREEN)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
       
        self.page.overlay.append(self.download_dialog)
        self.download_dialog.open = True
        self.page.update()

    def close_dialogs(self, e=None):
        if self.delete_dialog and self.delete_dialog.open:
            self.delete_dialog.open = False
        if self.download_dialog and self.download_dialog.open:
            self.download_dialog.open = False
        self.page.update()

    def confirm_delete(self, analysis_id, title):
        try:
            self.db_manager.delete_analysis_by_id(analysis_id)
            self._show_notification(f"Análisis '{title}' eliminado correctamente")
            
            # Actualizar la vista de historial
            self.tabs.tabs[1].content = self.create_history_section()
            self.close_dialog()
            self.page.update()
        except Exception as ex:
            self._show_notification(f"Error al eliminar el análisis: {ex}", is_error=True)
            self.close_dialogs()

    def download_file(self, file_content: bytes, file_name: str):
        def save_file_result(e: ft.FilePickerResultEvent):
            self.close_dialogs()

            if e.path:
                try:
                    # Verificar que el contenido no esté vacío
                    if not file_content or len(file_content) == 0:
                        raise ValueError("El archivo está vacío")
                    
                    # Asegurarnos que la extensión sea .zip
                    zip_path = e.path if e.path.endswith('.zip') else f"{e.path}.zip"

                    with open(zip_path, "wb") as f:
                        f.write(file_content)
                    snackbar = ft.SnackBar(content=ft.Text("Archivo descargado correctamente", color=ft.Colors.WHITE), bgcolor="#4CAF50", behavior=ft.SnackBarBehavior.FLOATING)
                    self.page.overlay.append(snackbar)
                    snackbar.open = True
                    self.page.update()
                except Exception as ex:
                    snackbar = ft.SnackBar(content=ft.Text(f"Error al guardar el archivo: {ex}", color=ft.Colors.WHITE), bgcolor="#F44336", behavior=ft.SnackBarBehavior.FLOATING)
                    self.page.overlay.append(snackbar)
                    snackbar.open = True
                    self.page.update()
            else:
                snackbar = ft.SnackBar(content=ft.Text("No se seleccionó ninguna ruta para guardar.", color=ft.Colors.WHITE), bgcolor="#FFC107", behavior=ft.SnackBarBehavior.FLOATING)
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()

        self.file_picker.on_result = save_file_result
        if not file_name.endswith('.zip'):
            file_name = f'{file_name}.zip'

        # Mostrar el diálogo de guardado
        self.file_picker.save_file(
            file_name=file_name,
            allowed_extensions=["zip"]
        )
        self.close_dialogs()
