import flet as ft
from components.header import Header
from components.sidebar import Sidebar
from components.notifications import NotificationsManager
from views.home import HomeView
from views.reports import ReportsView
#from views.grafico import GraphicsView
from views.settings import SettingsView
from views.account import AccountView

class MainApp(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page
        self.title = "Manager Reports App"

        #colores de la app
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

        #componentes de la app
        self.notifications_manager = NotificationsManager(page, self.header_color, self.text_color)
        self.header = Header(page, self.header_color, self.text_color, self.notify_color, self.change_view, self.notifications_manager)
        self.sidebar = Sidebar(page, self.sidebar_color, self.text_color, self.bg_color, self.selected_color)

        #Vistas de la app
        self.views = {
            "home": HomeView(page, self.bg_color, self.text_color, self.white_color, self.notify_color, self.text_color2, self.notifications_manager), #Dentro de esta vista configuro todo el funcionamiento de nuevo análisis
            "reports": ReportsView(page, self.bg_color, self.text_color, self.white_color, self.notify_color, self.text_color2, self.notifications_manager),
            #"grafics": GraphicsView(page, self.bg_color, self.text_color, self.white_color, self.notify_color, self.text_color2),
            "settings": SettingsView(page, self.bg_color, self.text_color, self.white_color, self.notify_color, self.text_color2, self.notifications_manager),
            "account": AccountView(page, self.bg_color, self.text_color, self.white_color, self.notify_color, self.text_color2, self.notifications_manager)
        }

        # Agregar el contenedor de notificaciones al layout principal
        self.page.add(self.notifications_manager.popup.container)
        #Configuración eventos de la sidebar

        self.setup_sidebar_events()

        #Vista actual
        self.current_view = self.views["home"]

        #Cuerpo principal de la app
        self.body = ft.Container(
            expand=True,
            content = ft.Row(
                controls = [
                    self.sidebar,
                    self.current_view
                ]
            )
        )

        # Ejemplo de botón que genera una notificación automática
        self.test_button = ft.ElevatedButton(
            text="Generar Notificación",
            on_click=lambda e: self.add_notification("Se ejecutó el botón de prueba")
        )

        # Agregar el botón al diseño principal
        self.page.add(ft.Column(
            expand=True,
            controls = [
                self.header,
                self.body,
                self.test_button  # Botón de prueba agregado
            ]
        ))

    def setup_sidebar_events(self):
        self.sidebar.home_btn.on_click = lambda e: self.change_view("home")
        self.sidebar.reports_btn.on_click = lambda e: self.change_view("reports")
        #self.sidebar.grafics_btn.on_click = lambda e: self.change_view("grafics")
        self.sidebar.settings_btn.on_click = lambda e: self.change_view("settings")
        self.sidebar.account_btn.on_click = lambda e: self.change_view("account")

    def change_view(self, view_name):
        self.body.content.controls[1] = self.views[view_name]

        # Actualizar el estado de selección de los botones
        self.sidebar.update_content(
            home_selected=(view_name == "home"),
            reports_selected=(view_name == "reports"),
            grafics_selected=(view_name == "grafics"),
            settings_selected=(view_name == "settings"),
            account_selected=(view_name == "account")
        )

        self.page.update()

    def add_notification(self, message):
        """Agrega una notificación y muestra el popup."""
        self.notifications_manager.add_notification(message)
        

ft.app(target=MainApp, view=ft.WEB_BROWSER, assets_dir="assets")