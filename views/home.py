import flet as ft
from components.notifications import NotificationsManager
from components.popup_analisis import crear_popup_analisis

class HomeView(ft.Container):
    def __init__(self, page: ft.Page, bg_color: str, text_color: str, white_color: str, notify_color: str, text_color2: str, notifications_manager: NotificationsManager):
        super().__init__(expand=True)
        self.page = page
        self.bg_color = bg_color
        self.text_color = text_color
        self.white_color = white_color
        self.notify_color = notify_color
        self.text_color2 = text_color2
        self.page.bgcolor = bg_color
        self.notifications_manager = notifications_manager

        self.popup, self.file_picker = crear_popup_analisis(self.page)
        self.page.dialog = self.popup

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=20,
            controls=[
                self.create_header(),
                self.create_welcome_message(),
                self.create_feature_cards(),
                self.create_graph_section()
            ]
        )

    def create_header(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("Bienvenido a la Aplicación", color=self.text_color, size=24, weight=ft.FontWeight.BOLD),
                ft.Icon(ft.Icons.HOME, color=self.notify_color, size=32)
            ]
        )

    def create_welcome_message(self):
        return ft.Text(
            "Esta es la página de inicio de la aplicación. Aquí puedes encontrar información y acceso a todas las funciones.",
            color=self.text_color,
            size=16,
            text_align=ft.TextAlign.CENTER
        )

    def create_feature_cards(self):
        return ft.Row(
            wrap=True,  # Permite que las tarjetas se ajusten automáticamente en filas
            spacing=20,
            run_spacing=20,
            controls=[
                self.create_feature_card("Nuevo Análisis", "Accede a la creación de nuevos análisis", ft.Icons.ADD, self.on_new_analysis_click),
                self.create_feature_card("Registro de Documentos", "Pronto disponible...", ft.Icons.DESCRIPTION),
                self.create_feature_card("Generación de Informes", "Pronto disponible...", ft.Icons.ANALYTICS),
                self.create_feature_card("Pronto disponible...", "", ft.Icons.HOURGLASS_EMPTY),
                self.create_feature_card("Pronto disponible...", "", ft.Icons.HOURGLASS_EMPTY)
            ]
        )

    def create_feature_card(self, title: str, description: str, icon: str, on_click=None):
        return ft.Card(
            elevation=5,
            color=self.bg_color,
            content=ft.Container(
                width=250,  # Ajuste de ancho según la imagen
                height=180,  # Ajuste de alto según la imagen
                padding=20,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(icon, size=40, color=self.white_color),
                        ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=self.white_color, text_align=ft.TextAlign.CENTER),
                        ft.Text(description, size=16, color=self.text_color, text_align=ft.TextAlign.CENTER)
                    ]
                ),
                on_click=on_click
            )
        )
    def on_new_analysis_click(self, e):
        # Asegúrate de que el popup esté configurado correctamente
        if not self.popup:
            self.popup, self.file_picker = crear_popup_analisis(self.page)
            self.popup.alignment = ft.alignment.center  # Centrar el popup

        # Agregar el popup al overlay si no está presente
        if self.popup not in self.page.overlay:
            self.page.overlay.append(self.popup)

        # Mostrar el popup sobre la vista actual
        self.popup.open = True
        self.page.update()

    def create_graph_section(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Evolución Mensual de Egresos por Hospital de la Red", size=18, weight=ft.FontWeight.BOLD, color=self.text_color),
                    ft.Text("Últimos 6 Meses", size=14, color=self.text_color2),
                    ft.Container(
                        height=300,
                        content=ft.Text("[Gráfico Placeholder]", color=self.text_color2, text_align=ft.TextAlign.CENTER)
                    )
                ]
            )
        )




