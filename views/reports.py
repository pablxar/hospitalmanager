import flet as ft
from components.notifications import NotificationsManager
from database import DatabaseManager
import os

class ReportsView(ft.Container):
    def __init__(self, page: ft.Page, bg_color: str, text_color: str, white_color: str, notify_color: str, text_color2: str, notifications_manager: NotificationsManager):
        super().__init__(expand=True)
        self.page = page
        self.bg_color = bg_color
        self.text_color = text_color
        self.white_color = white_color
        self.notify_color = notify_color
        self.text_color2 = text_color2
        self.page.bgcolor = bg_color
        self.notifications_manager = notifications_manager

        # Inicializar la base de datos
        self.db_manager = DatabaseManager()

        # Inicializar el FilePicker
        self.file_picker = ft.FilePicker()
        self.page.overlay.append(self.file_picker)

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=20,
            controls=[
                self.create_header(),
                self.create_report_list()
            ]
        )

    def create_header(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("Reportes", color=self.text_color, size=24, weight=ft.FontWeight.BOLD),
                ft.Icon(ft.Icons.REPORT_PROBLEM, color=self.notify_color, size=32),
                ft.ElevatedButton(
                    text="Recargar",
                    on_click=lambda e: self.reload_reports()
                )
            ]
        )

    def create_report_list(self):
        # Obtener análisis desde la base de datos (id, nombre, fecha, contenido blob)
        analyses = self.db_manager.fetch_analyses()
        return ft.ListView(
            expand=True,
            spacing=10,
            controls=[
                self.create_report_item(analysis[1], analysis[2], analysis[3]) for analysis in analyses
            ]
        )

    def create_report_item(self, title: str, date: str, file_content: bytes):
        return ft.Card(
            elevation=5,
            color=self.bg_color,
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=self.white_color),
                        ft.Text(f"Fecha: {date}", size=14, color=self.text_color),
                        ft.ElevatedButton(
                            text="Descargar",
                            on_click=lambda e, content=file_content, name=title: self.download_file(content, name)
                        )
                    ]
                )
            )
        )

    def download_file(self, file_content: bytes, file_name: str):
        def save_file(event):
            if event.path:
                try:
                    with open(event.path, "wb") as output_file:
                        output_file.write(file_content)

                    self.notifications_manager.add_notification(f"Archivo descargado correctamente en: {event.path}")
                except Exception as ex:
                    self.notifications_manager.add_notification(f"Error al guardar el archivo: {ex}")
            else:
                self.notifications_manager.add_notification("No se seleccionó ninguna ruta para guardar el archivo.")

            self.page.update()

        self.file_picker.on_result = save_file
        self.file_picker.save_file(file_name=f"{file_name}.zip")

    def reload_reports(self):
        # Actualizar la lista de reportes desde la base de datos
        self.content.controls[1] = self.create_report_list()
        self.page.update()
