import flet as ft
from components.graphs import GraphicsView

class DashboardView(ft.Container):
    def __init__(self, page: ft.Page, bg_color: str, text_color: str):
        super().__init__(expand=True)
        self.page = page
        self.bg_color = bg_color
        self.text_color = text_color

        # Configuración del gráfico
        self.chart = GraphicsView(page, bg_color, text_color)

        # Contenedor principal de la vista
        self.content = ft.Container(
            expand=True,
            bgcolor=self.bg_color,
            content=ft.Column(
                controls=[
                    self._create_header(),
                    self.chart,
                ]
            )
        )
        
    def _create_header(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("Dashboard", color=self.text_color, size=24, weight=ft.FontWeight.BOLD),
                ft.Icon(ft.icons.DASHBOARD, color=self.text_color, size=32)
            ]
        )
    