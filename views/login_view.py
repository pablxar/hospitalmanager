import flet as ft
from auth import AuthManager  # Asegúrate de tener esta clase

class LoginView(ft.Container):
    def __init__(self, page: ft.Page, auth_manager: AuthManager, on_login_success):
        super().__init__()
        self.page = page
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success

        self.username = ft.TextField(label="Usuario", width=300)
        self.password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)
        self.message = ft.Text("", color=ft.Colors.RED)

        self.content = ft.Column(
            [
                ft.Text("Iniciar Sesión", size=24, weight=ft.FontWeight.BOLD),
                self.username,
                self.password,
                ft.ElevatedButton("Entrar", on_click=self.login),
                self.message,
                ft.TextButton("Registrar nuevo usuario", on_click=self.go_register),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def login(self, e):
        # Validación simple
        if not self.username.value or not self.password.value:
            self.message.value = "Por favor completa usuario y contraseña."
            self.update()
            return

        user_row = self.auth_manager.login(self.username.value.strip(), self.password.value)
        if user_row:
            self.message.value = ""
            self.update()
            self.on_login_success(user_row)
        else:
            self.message.value = "Usuario o contraseña incorrectos."
            self.update()

    def go_register(self, e):
        register_popup = RegisterPopup(self.page, self.auth_manager)
        self.page.overlay.append(register_popup)
        self.page.update()

class RegisterPopup(ft.Container):
    def __init__(self, page, auth_manager):
        self.username = ft.TextField(label="Usuario", width=300)
        self.password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)
        self.email = ft.TextField(label="Email (opcional)", width=300)
        self.message = ft.Text("", color=ft.Colors.RED)

        super().__init__(
            content=ft.Column([
                ft.Text("Registrar nuevo usuario", size=20, weight=ft.FontWeight.BOLD),
                self.username,
                self.password,
                self.email,
                self.message,
                ft.Row([
                    ft.TextButton("Cancelar", on_click=self.close_popup),
                    ft.ElevatedButton("Registrar", on_click=self.register),
                ], alignment=ft.MainAxisAlignment.END),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            alignment=ft.alignment.center,
            bgcolor="#FFFFFF",
            padding=20,
            border_radius=10,
            visible=True
        )
        self.page = page
        self.auth_manager = auth_manager

    def register(self, e):
        if not self.username.value or not self.password.value:
            self.message.value = "Usuario y contraseña son obligatorios."
            self.update()
            return

        try:
            success = self.auth_manager.register(self.username.value.strip(), self.password.value, self.email.value.strip())
            if success:
                self.message.value = "Usuario registrado con éxito. Ahora inicie sesión."
                self.update()
                import threading
                threading.Timer(2, self.close_popup).start()
            else:
                self.message.value = "Error: usuario ya existe o datos inválidos."
                self.update()
        except Exception as ex:
            self.message.value = f"Error inesperado: {str(ex)}"
            self.update()

    def close_popup(self, e=None):
        self.visible = False
        self.page.update()
