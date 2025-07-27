import flet as ft
from auth import AuthManager
from database import DatabaseManager
from views.login_view import LoginView
from components.header import Header
from components.sidebar import Sidebar
from components.notifications import NotificationsManager
from views.home import HomeView
from views.analytics import AnalyticsView
from views.settings import SettingsView
from views.account import AccountView


class MainApp(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page
        self.page.icon = "assets/logo.ico"  # Cambiar el icono de la ventana al iniciar el programa
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthManager(self.db_manager)

        self.user = None  # Para guardar la fila de usuario logueado

        # Colores y componentes como tienes
        self.bg_color = "#2E1A47"
        self.header_color = "#3F2A56"
        self.sidebar_color = "#3F2A56"
        self.text_color = "#FFFFFF"
        self.containers_color = "#161717"
        self.boton_color = "#4B3F61"
        self.notify_color = "#F19EDC"
        self.text_color2 = "#24003E"
        self.white_color = "#FFFFFF"
        self.selected_color = "#2E1A47"

        self.notifications_manager = NotificationsManager(page, self.header_color, self.text_color, self.notify_color)

        # Componentes de navegación, que estarán disponibles sólo tras login
        self.header = None
        self.sidebar = None

        # Vistas, se cargarán luego del login
        self.views = {}

        # Layout principal
        self.body = None

        # Comenzar con login
        self.show_login()

    def show_login(self):
        self.page.title = "Login - Manager Reports App"
        self.page.icon = "assets/logo.ico"  # Cambiar el icono de la ventana
        self.page.controls.clear()

        # Instanciar la vista de login
        self.login_view = LoginView(self.page, self.auth_manager, self.on_login_success)

        # Agregar la vista de login a la página
        self.page.add(self.login_view)
        self.page.update()

    def on_login_success(self, user_row):
        self.user = user_row  # fila usuario (id, username, ...)
        self.setup_ui_post_login()

    def setup_ui_post_login(self):
        self.page.title = f"Bienvenido {self.user[1]}"  # username en posición 1

        self.header = Header(self.page, self.header_color, self.text_color, self.notify_color, self.change_view, self.notifications_manager)
        self.sidebar = Sidebar(self.page, self.sidebar_color, self.text_color, self.bg_color, self.selected_color)

        self.views = {
            "home": HomeView(self.page, self.bg_color, self.text_color, self.white_color, self.notify_color, self.text_color2, self.notifications_manager, self.user, self.change_view),
            "analytics": AnalyticsView(self.page, self.bg_color, self.text_color, self.white_color, self.notify_color, self.text_color2, self.notifications_manager, self.user),
            "settings": SettingsView(self.page, self.bg_color, self.text_color, self.white_color, self.notify_color, self.text_color2, self.notifications_manager, self.user),
            "account": AccountView(self.page, self.bg_color, self.text_color, self.white_color, self.notify_color, self.text_color2, self.notifications_manager, self.user, self.auth_manager, self.on_login_success),
        }

        self.page.overlay.append(self.notifications_manager.container)

        self.setup_sidebar_events()

        self.current_view = self.views["home"]

        self.body = ft.Container(
            expand=True,
            content=ft.Row(
                controls=[
                    self.sidebar,
                    self.current_view
                ]
            )
        )

        self.page.controls.clear()
        self.page.add(
            ft.Column(
                expand=True,
                controls=[
                    self.header,
                    self.body,
                ]
            )
        )
        self.page.update()

    def setup_sidebar_events(self):
        self.sidebar.home_btn.on_click = lambda e: self.change_view("home")
        self.sidebar.analytics_btn.on_click = lambda e: self.change_view("analytics")
        self.sidebar.settings_btn.on_click = lambda e: self.change_view("settings")
        self.sidebar.account_btn.on_click = lambda e: self.change_view("account")

    def change_view(self, view_name):
        self.body.content.controls[1] = self.views[view_name]
        self.sidebar.update_content(
            home_selected=(view_name == "home"),
            analytics_selected=(view_name == "analytics"),
            settings_selected=(view_name == "settings"),
            account_selected=(view_name == "account"),
        )
        self.page.update()

def main(page: ft.Page):
    app = MainApp(page)

if __name__ == "__main__":
    ft.app(target=main)
