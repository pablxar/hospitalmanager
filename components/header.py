import flet as ft
# Importación del NotificationsPopup
from components.notifications import NotificationsManager

# Simplificación del Header para usar NotificationsManager
class Header(ft.Container):
    def __init__(self, page: ft.Page, header_color: str, text_color: str, notify_color: str, change_view_callback, notifications_manager):
        super().__init__(height=60, bgcolor=header_color)
        self.change_view = change_view_callback
        self.notifications_manager = notifications_manager
        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Container(
                    content=ft.Image(
                        src="assets/logo.ico",
                        width=40,
                        height=40,
                        tooltip="Inicio"
                    ),
                    on_click=lambda e: self.change_view("home")
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Hospital Analytics Manager App",
                            text_align=ft.TextAlign.CENTER,
                            size=20,
                            color=text_color,
                            weight="bold"
                        )
                    ]
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.NOTIFICATION_IMPORTANT,
                            icon_color=notify_color,
                            tooltip="Notificaciones",
                            icon_size=30,
                            #on_click=lambda e: self.notifications_manager.show_notifications()
                        ),
                        ft.IconButton(
                            icon=ft.Icons.PERSON,
                            icon_color=text_color,
                            tooltip="Perfil",
                            icon_size=30,
                            on_click=lambda e: self.change_view("account")
                        )
                    ]
                )
            ]
        )