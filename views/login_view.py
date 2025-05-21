import flet as ft
from auth import AuthManager  # Asegúrate de tener esta clase

class LoginView(ft.Container):
    def __init__(self, page: ft.Page, auth_manager: AuthManager, on_login_success):
        super().__init__(expand=True)
        self.page = page
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success

        # Fondo futurista con degradado
        self.page.bgcolor = "linear-gradient(to bottom, #1F1C2C, #928DAB)"

        # Logo encima del título
        logo = ft.Image(src="assets/logo.ico", width=100, height=100, fit=ft.ImageFit.CONTAIN)

        # Contenedor centrado con estilo futurista
        login_container = ft.Container(
            content=ft.Column(
                controls=[
                    logo,
                    ft.Text("Iniciar Sesión", size=24, weight=ft.FontWeight.BOLD),
                    self.create_login_form()
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,  # Espaciado entre elementos
            ),
            alignment=ft.alignment.center,
            width=400,
            height=600,
            bgcolor="#2E1A47",
            border_radius=20,
            shadow=ft.BoxShadow(
                spread_radius=10,
                blur_radius=20,
                color="#00000088",
                offset=ft.Offset(0, 10),
            ),
            padding=20,
        )

        self.content = ft.Container(
            content=login_container,
            alignment=ft.alignment.center,
            expand=True,
        )

    def create_login_form(self):
        # Crear formulario de login
        self.username = ft.TextField(label="Usuario", width=300, on_change=self.validate_inputs)
        self.password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300, on_change=self.validate_inputs)
        self.message = ft.Text("", color=ft.Colors.RED)

        # Asignar el botón de login como atributo de la clase
        self.login_button = ft.ElevatedButton("Entrar", on_click=self.login, disabled=True)
        self.register_button = ft.TextButton("Registrar nuevo usuario", on_click=self.go_register)

        return ft.Column(
            controls=[
                self.username,
                self.password,
                self.login_button,
                self.message,
                self.register_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def validate_inputs(self, e):
        self.login_button.disabled = not (self.username.value and self.password.value)
        self.update()

    def login(self, e):
        if not self.username.value or not self.password.value:
            self.message.value = "Por favor completa usuario y contraseña."
            self.update()
            return

        self.message.value = "Procesando..."
        self.update()

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
        self.page = page
        self.auth_manager = auth_manager

        # Logo encima del título
        logo = ft.Image(src="assets/logo.ico", width=100, height=100, fit=ft.ImageFit.CONTAIN)

        # Contenedor centrado con estilo futurista
        register_container = ft.Container(
            content=ft.Column(
                controls=[
                    logo,
                    ft.Text("Registrar nuevo usuario", size=24, weight=ft.FontWeight.BOLD),
                    self.create_register_form()
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,  # Espaciado entre elementos
            ),
            alignment=ft.alignment.center,
            width=400,
            height=600,
            bgcolor="#2E1A47",
            border_radius=20,
            shadow=ft.BoxShadow(
                spread_radius=10,
                blur_radius=20,
                color="#00000088",
                offset=ft.Offset(0, 10),
            ),
            padding=20,
        )

        super().__init__(
            content=register_container,
            alignment=ft.alignment.center,
            expand=True,
            visible=True
        )

    def create_register_form(self):
        # Crear formulario de registro
        self.username = ft.TextField(label="Usuario", width=300, on_change=self.validate_inputs)
        self.password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300, on_change=self.validate_inputs)
        self.email = ft.TextField(label="Email (opcional)", width=300)
        self.message = ft.Text("", color=ft.Colors.RED)

        self.register_button = ft.ElevatedButton("Registrar", on_click=self.register, disabled=True)
        cancel_button = ft.TextButton("Volver", on_click=self.close_popup)

        return ft.Column(
            controls=[
                self.username,
                self.password,
                self.email,
                self.message,
                ft.Row([
                    cancel_button,
                    self.register_button,
                ], alignment=ft.MainAxisAlignment.END),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def validate_inputs(self, e):
        self.register_button.disabled = not (self.username.value and self.password.value)
        self.update()

    def register(self, e):
        if not self.username.value or not self.password.value:
            self.message.value = "Usuario y contraseña son obligatorios."
            self.update()
            return

        self.message.value = "Procesando..."
        self.update()

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
