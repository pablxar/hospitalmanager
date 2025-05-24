import flet as ft
from components.notifications import NotificationsManager
from database import DatabaseManager
import os

class ReportsView(ft.Container):
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
        # Obtener análisis desde la base de datos para el usuario logueado
        analyses = self.db_manager.fetch_analyses_by_user(self.user[0])  # usuario_id en posición 0
        return ft.ListView(
            expand=True,
            spacing=10,
            controls=[
                self.create_report_item(analysis[1], analysis[2], analysis[0], analysis[0]) for analysis in analyses
            ]
        )

    def create_report_item(self, title: str, date: str, file_content: bytes, analysis_id=None):
        def show_delete_dialog(e):
            dialog = ft.AlertDialog(
                modal=True,
                open=True,
                title=ft.Text("Confirmar eliminación"),
                content=ft.Text(f"¿Estás seguro de que deseas eliminar el reporte '{title}'?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda ev: self.close_dialog()),
                    ft.TextButton("Eliminar", on_click=lambda ev: self.confirm_delete(analysis_id, title)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog = dialog
            if dialog not in self.page.overlay:
                self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

        return ft.Card(
            elevation=5,
            color=self.bg_color,
            content=ft.Container(
                padding=20,
                content=ft.Row([
                    ft.Container(
                        expand=True,
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
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        tooltip="Eliminar reporte",
                        icon_color=ft.Colors.RED,
                        on_click=show_delete_dialog
                    )
                ])
            )
        )

    def close_dialog(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
            self.page.dialog = None

    def confirm_delete(self, analysis_id, title):
        try:
            self.db_manager.delete_analysis_by_id(analysis_id)
            snackbar = ft.SnackBar(
                content=ft.Text(f"Reporte '{title}' eliminado correctamente.", color=ft.Colors.WHITE),
                bgcolor="#4CAF50",
                behavior=ft.SnackBarBehavior.FLOATING,
            )
            self.page.overlay.append(snackbar)
            snackbar.open = True
            self.reload_reports()
            self.page.update()
        except Exception as ex:
            self.notifications_manager.add_notification(f"Error al eliminar el reporte: {ex}")
        self.close_dialog()

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
