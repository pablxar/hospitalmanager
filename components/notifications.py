import flet as ft
from flet.core import *

class NotificationsManager:
    def __init__(self, page: ft.Page, header_color: str, text_color: str, notify_color: str):
        self.page = page
        self.header_color = header_color
        self.text_color = text_color
        self.notify_color = notify_color
        self.notifications = []
        self.popup = self 

        # Crear el contenedor de notificaciones
        self.container = ft.Container(
            visible=False,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Notificaciones", color=text_color, weight="bold", size=18),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                tooltip="Cerrar",
                                on_click=self.close_popup
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(color=text_color),
                    ft.ListView(
                        expand=True,
                        spacing=10,
                        controls=[]  # Contenedor de notificaciones dinámico
                    )
                ],
                expand=True
            ),
            bgcolor=notify_color,
            padding=20,
            width=300,  # Ancho del panel lateral
            alignment=ft.alignment.center_right,  # Asegura que se alinee al borde derecho de toda la pantalla
            border_radius=ft.border_radius.only(top_left=20, bottom_left=20),
            margin=ft.margin.only(top=0, right=0)  # Elimina márgenes para que quede al borde
        )

        self.page.controls.append(self.container)  # Agrega el contenedor al layout principal

    def show_notifications(self):
        """Actualiza y muestra el popup con las notificaciones actuales."""
        if not self.notifications:
            self.notifications.append("No tienes notificaciones nuevas.")
        else:
            self.notifications = [n for n in self.notifications if n != "No tienes notificaciones nuevas."]

        self.container.content.controls[2].controls = [
            ft.Text(notification, color=self.text_color) for notification in self.notifications
        ]
        self.container.visible = True
        self.container.update()
        self.page.update()
    
    def add_notification(self, message: str):
        """Agrega una nueva notificación a la lista."""
        self.notifications.append(message)
    
    def update_notifications(self, notifications: list):
        """Actualiza el contenido del popup con una lista de notificaciones."""
        self.container.content.controls[1].controls = [
            ft.Text(notification, color=self.text_color) for notification in notifications
        ]
        self.container.visible = True  # Muestra el popup
        self.container.update()  # Actualiza el contenedor
        self.page.update()  # Actualiza la página

    def close_popup(self, e=None):
        """Cierra el popup."""
        self.container.visible = False
        self.container.update()
        self.page.update()
