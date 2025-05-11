import flet as ft
from components.notifications import NotificationsManager

class AccountView(ft.Container):
    def __init__(self, page: ft.Page, bg_color: str, text_color: str, white_color: str, notify_color: str, text_color2: str, notifications_manager: NotificationsManager):
        super().__init__(expand=True)
        self.page = page
        self.bg_color = bg_color
        self.text_color = text_color
        self.white_color = white_color
        self.notify_color = notify_color
        self.text_color2 = text_color2
        self.notifications_manager = notifications_manager

        # Contenedor principal de la vista
        self.content = ft.Container(
            expand=True,
            bgcolor=self.bg_color,
            content=ft.Column(
                controls=[
                    self.create_header(),
                    self.create_profile_card(),
                    self.create_account_settings_card(),
                ]
            )
        )

    def create_header(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("Perfil de Usuario", color=self.text_color, size=24),
            ]
        )

    def create_profile_card(self):
        return ft.Card(
            
            content=ft.Column(
                controls=[
                    ft.Text("Información del Perfil", color=self.text_color, size=20),
                    ft.Text("Nombre: Juan Pérez", color=self.text_color),
                    ft.Text("Correo: juan@gmail.com", color=self.text_color),
                    ft.Text("Teléfono: 123456789", color=self.text_color),      
                ]
            )
        )
    def create_account_settings_card(self):
        return ft.Card(
            
            content=ft.Column(
                controls=[
                    ft.Text("Configuración de la Cuenta", color=self.text_color, size=20),
                    ft.Row(
                        controls=[
                            ft.Text("Cambiar Contraseña", color=self.text_color),
                            ft.IconButton(ft.Icons.KEYBOARD_ARROW_RIGHT, icon_color=self.text_color)
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Cerrar Sesión", color=self.text_color),
                            ft.IconButton(ft.Icons.KEYBOARD_ARROW_RIGHT, icon_color=self.text_color)
                        ]
                    )
                ]
            )
        )
    def update(self):
        self.content.update()  
