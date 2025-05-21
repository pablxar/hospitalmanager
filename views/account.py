import flet as ft
from components.notifications import NotificationsManager
from views.login_view import LoginView  # Importar LoginView

class AccountView(ft.Container):
    def __init__(self, page: ft.Page, bg_color: str, text_color: str, white_color: str, notify_color: str, text_color2: str, notifications_manager: NotificationsManager, user: dict, auth_manager, on_login_success):
        super().__init__(expand=True)
        self.page = page
        self.bg_color = bg_color
        self.text_color = text_color
        self.white_color = white_color
        self.notify_color = notify_color
        self.text_color2 = text_color2
        self.notifications_manager = notifications_manager
        self.user = user  # Información del usuario logueado
        self.auth_manager = auth_manager  # Referencia al auth_manager
        self.on_login_success = on_login_success  # Referencia a la función de login success

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
            elevation=5,
            content=ft.Container(
                bgcolor="#1E1E2F",
                border_radius=15,
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Text("Información del Perfil", color=self.text_color, size=22, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Icon(name=ft.Icons.PERSON, color=self.text_color),
                            ft.Text(f"Nombre: {self.user[1]}", color=self.text_color, size=18),
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Row([
                            ft.Icon(name=ft.Icons.EMAIL, color=self.text_color),
                            ft.Text(f"Correo: {self.user[3]}", color=self.text_color, size=18),
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Row([
                            ft.Icon(name=ft.Icons.PHONE, color=self.text_color),
                            ft.Text(f"Teléfono: {self.user[4] if len(self.user) > 4 else 'N/A'}", color=self.text_color, size=18),
                        ], alignment=ft.MainAxisAlignment.START),
                    ],
                    spacing=10,
                )
            )
        )

    def create_account_settings_card(self):
        return ft.Card(
            elevation=5,
            content=ft.Container(
                bgcolor="#1E1E2F",
                border_radius=15,
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Text("Configuración de la Cuenta", color=self.text_color, size=22, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            controls=[
                                ft.Icon(name=ft.Icons.LOCK, color=self.text_color),
                                ft.Text("Cambiar Contraseña", color=self.text_color, size=18),
                                ft.IconButton(ft.Icons.KEYBOARD_ARROW_RIGHT, icon_color=self.text_color)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(name=ft.Icons.LOGOUT, color=self.text_color),
                                ft.Text("Cerrar Sesión", color=self.text_color, size=18),
                                ft.IconButton(ft.Icons.KEYBOARD_ARROW_RIGHT, icon_color=self.text_color, on_click=self.logout)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
                    ],
                    spacing=10,
                )
            )
        )

    def logout(self, e):
        # Verificar si self.page está definido
        if self.page is None:
            print("Error: self.page is None. No se puede redirigir a la vista de login.")
            return

        # Cerrar sesión en el auth_manager
        if self.auth_manager:
            self.auth_manager.logout()  # Asegúrate de que este método exista en auth_manager

        # Limpiar información del usuario
        self.user = None

        # Actualizar el título de la ventana
        #self.page.title = "Iniciar Sesión"

        # Volver a la vista de login
        self.page.controls.clear()
        self.page.add(LoginView(self.page, self.auth_manager, self.on_login_success))
        self.page.update()

    def update(self):
        self.content.update()
