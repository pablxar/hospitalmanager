import flet as ft
import sqlite3
import shutil
import zipfile
import os
from datetime import datetime
from components.notifications import NotificationsManager
from components.popup_analisis import PopupAnalisisManager
from components.report_generator import PopupReportGenerator

class HomeView(ft.Container):
    def __init__(self, page: ft.Page, bg_color: str, text_color: str, white_color: str, notify_color: str, text_color2: str, notifications_manager: NotificationsManager, user):
        super().__init__(expand=True)
        self.page = page
        self.bg_color = bg_color
        self.text_color = text_color
        self.white_color = white_color
        self.notify_color = notify_color
        self.text_color2 = text_color2
        self.page.bgcolor = bg_color
        self.notifications_manager = notifications_manager
        self.user = user

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
                self.create_feature_card("Generación de Informes", "Genera informes en base a análisis recientes", ft.Icons.ANALYTICS, self.on_generate_report_click),
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
        # Usar el nuevo manager de clase para el popup
        popup_manager = PopupAnalisisManager(self.page, self.user)
        self.popup, self.file_picker = popup_manager.popup, popup_manager.file_picker
        self.popup.alignment = ft.alignment.center

        if self.popup not in self.page.overlay:
            self.page.overlay.append(self.popup)

        self.popup.open = True
        self.page.dialog = self.popup
        self.page.update()

    def on_generate_report_click(self, e):
        # Usar el nuevo manager de clase para el popup
        report_manager = PopupReportGenerator(self.page, self.user, 'app_data.db')
        self.popup = report_manager.popup
        self.popup.alignment = ft.alignment.center

        if self.popup not in self.page.overlay:
            self.page.overlay.append(self.popup)

        self.popup.open = True
        self.page.dialog = self.popup
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




