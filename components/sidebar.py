import flet as ft

class Sidebar(ft.Container):
    def __init__(self, page: ft.Page, sidebar_color: str, text_color: str, bg_color: str, selected_color: str):
        super().__init__(width=60, border_radius=10, padding=5)
        self.sidebar_color = sidebar_color
        self.page = page
        self.text_color = text_color
        self.bg_color = bg_color
        self.selected_color = selected_color
        self.expanded = False  # Estado para controlar si la sidebar está expandida

        # Guardar los iconos como atributos para acceder luego
        self.home_btn = ft.IconButton(icon=ft.Icons.HOME, icon_color=text_color)
        self.analytics_btn = ft.IconButton(icon=ft.Icons.ANALYTICS, icon_color=text_color)
        self.grafics_btn = ft.IconButton(icon=ft.Icons.SHOW_CHART, icon_color=text_color)
        self.settings_btn = ft.IconButton(icon=ft.Icons.SETTINGS, icon_color=text_color)
        self.account_btn = ft.IconButton(icon=ft.Icons.PERSON, icon_color=text_color)

        # Botón para expandir/colapsar la sidebar
        self.toggle_btn = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD, icon_color=text_color, on_click=self.toggle_sidebar
        )

        self.update_content()

    def toggle_sidebar(self, e):
        self.expanded = not self.expanded
        self.width = 200 if self.expanded else 60
        self.toggle_btn.icon = ft.Icons.ARROW_BACK if self.expanded else ft.Icons.ARROW_FORWARD
        self.update_content()
        self.update()

    def update_content(self, home_selected=False, analytics_selected=False, grafics_selected=False, settings_selected=False, account_selected=False):
        # Actualizar el contenido de la sidebar según el estado expandido
        self.bgcolor = self.sidebar_color  # Aplicar el color de fondo de la sidebar
        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column([
                    self.create_button(self.home_btn, "Inicio", is_selected=home_selected),
                    self.create_button(self.analytics_btn, "Análisis", is_selected=analytics_selected),
                    self.create_button(self.grafics_btn, "Gráficos", is_selected=grafics_selected),
                    self.toggle_btn  # Botón para expandir/colapsar
                ]),
                ft.Column([
                    self.create_button(self.settings_btn, "Configuración", is_selected=settings_selected),
                    self.create_button(self.account_btn, "Cuenta", is_selected=account_selected)
                ])
            ]
        )

    def create_button(self, button, label, is_selected=False):
        # Crear un botón con texto opcional según el estado expandido
        if self.expanded:
            return ft.Container(
                content=ft.Row([
                    button,
                    ft.Text(label, color=self.text_color)
                ], alignment=ft.MainAxisAlignment.START),
                on_click=button.on_click,  # Asignar la función del botón al contenedor completo
                padding=5,
                bgcolor=self.selected_color if is_selected else None,  # Cambiar el fondo si está seleccionado
                border_radius=5
            )
        return ft.Container(
            content=button,
            bgcolor=self.selected_color if is_selected else None,  # Cambiar el fondo si está seleccionado
            border_radius=5
        )

