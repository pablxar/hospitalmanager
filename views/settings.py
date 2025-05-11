import flet as ft
from components.notifications import NotificationsManager

class SettingsView(ft.Container):
    def __init__(self, page: ft.Page, bg_color: str, text_color: str, white_color: str, notify_color: str, text_color2: str, notifications_manager: NotificationsManager):
        super().__init__(expand=True)
        self.page = page
        self.bg_color = bg_color
        self.text_color = text_color
        self.white_color = white_color
        self.notify_color = notify_color
        self.text_color2 = text_color2
        self.notifications_manager = notifications_manager  # Almacena el NotificationsManager para usarlo

        # Widget de configuración
        self.notifications_switch = ft.Switch(value=True, active_color= notify_color)
        self.theme_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("Light"),
                ft.dropdown.Option("Dark"),
                ft.dropdown.Option("System Default")
            ],
            value="Dark",
            width=200,
            border_color=notify_color,

        )
        self.font_size_slider = ft.Slider(
            min=12,
            max=24,
            value=16,
            divisions=6,
            label="{value}",
            active_color= notify_color,
            inactive_color= text_color2,
            thumb_color=white_color
        )

        self.content = ft.Column(
            scroll = ft.ScrollMode.AUTO,
            expand=True,
            spacing=20,
            controls=[
                self._create_header(),
                self._create_setting_card(
                    icon=ft.Icon(ft.Icons.NOTIFICATIONS, color=notify_color),
                    title="Notificaciones",
                    subtitle="Activar/Desactivar notificaciones por correo electrónico",
                    control=self.notifications_switch
                ),
                self._create_setting_card(
                    icon=ft.Icon(ft.Icons.COLOR_LENS, color=notify_color),
                    title="Tema",
                    subtitle="Selecciona el tema de la aplicación",
                    control=self.theme_dropdown
                ),
                self._create_setting_card(
                    icon=ft.Icon(ft.Icons.TEXT_FIELDS, color=notify_color),
                    title="Tamaño de fuente",
                    subtitle="Ajusta el tamaño de la fuente de la aplicación",
                    control=self.font_size_slider
                ),
                self._create_advanced_settings(),
                self._create_save_button()
            ]
        )
    def _create_header(self):
        return ft.Column(
            spacing=5,
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.SETTINGS, size=24, color=self.white_color),
                        ft.Text(
                            "Configuración",
                            size=24,
                            color=self.white_color,
                            weight="bold"
                        )
                    ],
                    spacing=10
                ),
                ft.Text("Ajusta la configuración de la aplicación según tus preferencias.", size=16,
                    color=ft.Colors.with_opacity(0.4, self.text_color)),
                ft.Divider(color= ft.Colors.with_opacity(0.2, self.text_color), height=10)
            ]
        )
    def _create_setting_card(self, icon: ft.Icon, title: str, subtitle: str, control: ft.Control):
        return ft.Card(
            elevation=5,
            color=ft.Colors.with_opacity(0.1, self.text_color),
            content=ft.Container(
                padding=15,
                content=ft.Row(
                    controls=[
                        icon,
                        ft.Column(
                            expand=True,
                            spacing=2,
                            controls=[
                                ft.Text(title, size=16, weight="bold", color=self.white_color),
                                ft.Text(subtitle, size=12, color= self.text_color), 
                            ]
                        ),
                        control
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )

        )
    def _create_advanced_settings(self):
        return ft.ExpansionTile(
            title=ft.Text("Configuración avanzada", color =self.white_color),
            subtitle=ft.Text("Opciones adicionales para usuarios avanzados", color = self.text_color),
            initially_expanded=False,
            controls=[
                self._create_setting_card(
                    icon=ft.Icon(ft.Icons.CLOUD, color=self.notify_color),
                    title="Sinconización en la nube",
                    subtitle="Configura la sincronización automática",
                    control=ft.Switch(value=False, active_color="24003E")
                ),
                self._create_setting_card(
                    icon=ft.Icon(ft.Icons.SECURITY, color=self.notify_color),
                    title="Autenticación de dos factores",
                    subtitle="Aumenta la seguridad de tu cuenta",
                    control=ft.Switch(value=False, active_color="24003E")
                ),
            ]
        )
    
    def _create_save_button(self):
        return ft.Container(
            padding=ft.padding.only(top=20),
            content= ft.FilledButton(
                content=ft.Text("Guardar cambios", color=self.white_color),
                width=200,
                height=45,
                style=ft.ButtonStyle(
                    bgcolor=self.notify_color,
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=20,
                    overlay_color=ft.Colors.with_opacity(0.1, self.white_color)
                ),
                on_click=lambda e: [
                    self._save_settings(),
                    self.notifications_manager.add_notification("Realizaste Cambios de configuración!")
                ]
            ),
            alignment=ft.alignment.center
        )
    
    def _save_settings(self):
        snackbar = ft.SnackBar(
            content=ft.Text("Cambios guardados correctamente", color=self.white_color),
            bgcolor=self.notify_color,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        self.page.overlay.append(snackbar)  # Agrega el SnackBar a la superposición de la página
        snackbar.open = True
        self.page.update()
