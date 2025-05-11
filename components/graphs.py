import flet as ft

class GraphicsView(ft.Container):
    def __init__(self, page: ft.Page, bg_color: str, text_color: str):
        super().__init__(expand=True)
        self.page = page
        self.bg_color = bg_color
        self.text_color = text_color

        # Configuración del gráfico
        self.chart = ft.Column(
            expand=True,
            controls=[
                ft.Text("Gráfico de Ejemplo", color=self.text_color),
                ft.BarChart(
                    data=[
                        {"x": "A", "y": 10},
                        {"x": "B", "y": 20},
                        {"x": "C", "y": 30},
                    ],
                    color="#FF5733",
                ),
            ],
        )
        

        