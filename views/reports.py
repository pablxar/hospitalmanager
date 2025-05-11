import flet as ft
from components.notifications import NotificationsManager

class ReportsView(ft.Container):
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


        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=20,
            controls=[
                self.create_header(),
                self.create_report_list()
            ]
        )

    def create_header(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("Reportes", color=self.text_color, size=24, weight=ft.FontWeight.BOLD),
                ft.Icon(ft.Icons.REPORT_PROBLEM, color=self.notify_color, size=32)
            ]
        )

    def create_report_list(self):
        return ft.ListView(
            expand=True,
            spacing=10,
            controls=[
                self.create_report_item("Reporte 1", "Descripción del reporte 1"),
                self.create_report_item("Reporte 2", "Descripción del reporte 2"),
                self.create_report_item("Reporte 3", "Descripción del reporte 3")
            ]
        )

    def create_report_item(self, title: str, description: str):
        return ft.Card(
            elevation=5,
            color=self.bg_color,
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=self.white_color),
                        ft.Text(description, size=14, color=self.text_color)
                    ]
                )
            )
        )