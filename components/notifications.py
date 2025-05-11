import flet as ft

class NotificationsPopup:
    def __init__(self, page: ft.Page, header_color: str, text_color: str):
        self.page = page  # Agregar el atributo 'page' aquí
        self.header_color = header_color
        self.text_color = text_color
        self.container = ft.Container(
            visible=False,  # Inicialmente oculto
            content=ft.Column(
                controls=[
                    ft.Text("Notificaciones", color=text_color, weight="bold"),
                    ft.Column(controls=[], scroll=ft.ScrollMode.AUTO),  # Contenedor de notificaciones
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        tooltip="Cerrar",
                        on_click=self.close_popup
                    )
                ],
                expand=True
            ),
            bgcolor=header_color,
            padding=10,
            border_radius=10,
            alignment=ft.alignment.top_right
        )

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
        self.container.update()  # Actualiza el contenedor
        self.page.update()  # Actualiza la página


class NotificationsManager:
    def __init__(self, page: ft.Page, header_color: str, text_color: str):
        self.page = page
        self.popup = NotificationsPopup(page, header_color, text_color)  # Pasar 'page' al popup
        self.notifications = []
        self.page.controls.append(self.popup.container)  # Agrega el contenedor al layout principal

    def add_notification(self, message: str):
        """Agrega una nueva notificación a la lista."""
        self.notifications.append(message)

    def show_notifications(self):
        """Actualiza y muestra el popup con las notificaciones actuales."""
        if not self.notifications:
            self.notifications.append("No tienes notificaciones nuevas.")
        else:
            self.notifications = [n for n in self.notifications if n != "No tienes notificaciones nuevas."]

        self.popup.update_notifications(self.notifications)
        self.page.update()  # Actualiza la página para reflejar los cambios

