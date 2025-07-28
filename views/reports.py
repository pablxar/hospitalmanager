import flet as ft
from datetime import datetime
from database import DatabaseManager
import tempfile
import os
from markdown import markdown
import threading


class ReportsView(ft.Container):
    def __init__(self, page: ft.Page, bg_color: str, text_color: str, white_color: str, notify_color: str, text_color2: str, notifications_manager, user, db_manager):
        super().__init__(expand=True)
        self.page = page
        self.bg_color = bg_color
        self.text_color = text_color
        self.white_color = white_color
        self.notify_color = notify_color
        self.text_color2 = text_color2
        self.notifications_manager = notifications_manager
        self.user = user
        self.db_manager = db_manager
        
        # Initialize report editor content
        self.report_content = ""
        self.selected_images = []
        self.selected_documents = []
        
        # Create UI components
        self._create_ui()
        
        self.update_timer = None  # Timer for delayed content update
        
    def _create_ui(self):
        """Initialize all UI components"""
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Crear Informe",
                    icon=ft.Icons.INSERT_CHART,
                    content=ft.Container(
                        content=self._create_report_tab(),
                        padding=10
                    )
                ),
                ft.Tab(
                    text="Historial",
                    icon=ft.Icons.HISTORY,
                    content=ft.Container(
                        content=self._create_history_tab(),
                        padding=10
                    )
                )
            ],
            expand=True
        )
        
        self.content = ft.Container(
            expand=True,
            bgcolor=self.bg_color,
            padding=20,                       
            content=ft.Column(
                expand=True,
                spacing=20,
                controls=[
                    self._create_header(),
                    ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, self.text_color)),
                    ft.Container(
                        content=self.tabs,
                        width=1000,
                        alignment=ft.alignment.top_center,
                        expand=True
                    )
                ]
            )
        )
    
    def _create_header(self):
        """Create the header section"""
        return ft.Row(
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
            controls=[
                ft.Text("Gestión de Informes", 
                       color=self.text_color, 
                       size=24, 
                       weight=ft.FontWeight.BOLD),
                ft.Icon(ft.Icons.ANALYTICS, color=self.notify_color, size=32)
            ]
        )
    
    def _create_report_tab(self):
        """Create the report creation tab"""
        # Create components
        self.analysis_dropdown = self._create_analysis_dropdown()
        self.report_title_field = ft.TextField(
            label="Título del Informe",
            hint_text="Ingrese un título descriptivo",
            width=800,
            border_color=self.notify_color,
            focused_border_color=self.notify_color,
        )
        self.report_editor = ft.TextField(
            multiline=True,
            min_lines=10,
            max_lines=20,
            width=600,
            label="Contenido del Informe",
            hint_text="Escriba el contenido detallado del informe...",
            border_color=self.notify_color,
            focused_border_color=self.notify_color,
            on_change=lambda e: self._update_report_content(e)
        )
        
        self.image_list = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=150,
            child_aspect_ratio=1,
            spacing=10,
            run_spacing=10,
        )
        # Layout with professional sections
        return ft.Container(
            width=900,
            padding=10,
            alignment=ft.alignment.top_center,
            content=ft.Column(
                scroll=ft.ScrollMode.ADAPTIVE,
                spacing=25,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Generar Nuevo Informe Clínico", 
                        size=22, 
                        weight=ft.FontWeight.BOLD,
                        color=self.text_color),
                    
                    # Section 1: Analysis selection
                    ft.Container(
                        width=800,
                        padding=15,
                        border_radius=10,
                        bgcolor=ft.Colors.with_opacity(0.05, self.notify_color),
                        content=ft.Column(
                            spacing=15,
                            controls=[
                                ft.Text("1. Selección de Análisis", 
                                    size=18, 
                                    weight="bold",
                                    color=self.notify_color),
                                self.analysis_dropdown,
                            ]
                        )
                    ),
                    
                    # Section 2: Report configuration
                    ft.Container(
                        width=800,
                        padding=15,
                        border_radius=10,
                        bgcolor=ft.Colors.with_opacity(0.05, self.notify_color),
                        content=ft.Column(
                            spacing=15,
                            controls=[
                                ft.Text("2. Configuración del Informe", 
                                    size=18, 
                                    weight="bold",
                                    color=self.notify_color),
                                self.report_title_field,
                                self._create_report_editor(),
                            ]
                        )
                    ),
                    
                    # Section 3: Images and attachments
                    ft.Container(
                        width=800,
                        padding=15,
                        border_radius=10,
                        bgcolor=ft.Colors.with_opacity(0.05, self.notify_color),
                        content=ft.Column(
                            spacing=15,
                            controls=[
                                ft.Text("3. Material de Apoyo (Opcional)", 
                                    size=18, 
                                    weight="bold",
                                    color=self.notify_color),
                                self._create_attachment_controls(),
                                self._create_attachment_preview(),
                            ]
                        )
                    ),
                    
                    # Save button
                    ft.Container(
                        width=800,
                        padding=ft.padding.only(top=20),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.ElevatedButton(
                                    text="Generar Informe",
                                    icon=ft.Icons.SAVE_AS,
                                    style=ft.ButtonStyle(
                                        bgcolor=self.notify_color,
                                        color=ft.Colors.WHITE,
                                        padding=20,
                                        shape=ft.RoundedRectangleBorder(radius=10)
                                    ),
                                    on_click=self.save_report
                                )
                            ]
                        )
                    )
                ]
            )
        )
        
    def _create_report_editor(self):
        """Create the report editor with formatting options"""
        self.report_text_field = ft.TextField(
            multiline=True,
            min_lines=15,
            max_lines=25,
            width=770,
            label="Contenido del Informe",
            hint_text="Escriba aquí el contenido detallado del informe...\n\nPuede usar:\n- Puntos clave\n- Conclusiones\n- Recomendaciones",
            border_color=self.notify_color,
            focused_border_color=self.notify_color,
            on_change=self._on_text_change,  # Use the delayed update handler
            key="report_text_field"
        )
        self.markdown_preview = ft.Container(
            content=ft.Markdown("", extension_set="gitHubWeb"),
            padding=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=5,
            width=770
        )
        return ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.FORMAT_BOLD,
                            tooltip="Negrita",
                            on_click=lambda e: self._format_text("bold")
                        ),
                        ft.IconButton(
                            icon=ft.Icons.FORMAT_ITALIC,
                            tooltip="Cursiva",
                            on_click=lambda e: self._format_text("italic")
                        ),
                        ft.IconButton(
                            icon=ft.Icons.FORMAT_LIST_BULLETED,
                            tooltip="Lista con viñetas",
                            on_click=lambda e: self._format_text("bullet")
                        ),
                        ft.IconButton(
                            icon=ft.Icons.FORMAT_LIST_NUMBERED,
                            tooltip="Lista numerada",
                            on_click=lambda e: self._format_text("numbered")
                        ),
                        ft.IconButton(
                            icon=ft.Icons.INSERT_PHOTO,
                            tooltip="Insertar imagen desde URL",
                            on_click=lambda e: self._insert_image_url()
                        )
                    ]
                ),
                self.report_text_field,
                ft.Text("Vista previa:", size=14, weight="bold"),
                self.markdown_preview
            ]   
        )
    
    def _create_attachment_controls(self):
        """Create controls for attachments"""
        return ft.Row(
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.ElevatedButton(
                    text="Añadir Imágenes",
                    icon=ft.Icons.IMAGE,
                    style=ft.ButtonStyle(
                        bgcolor=self.notify_color,
                        color=ft.Colors.WHITE,
                        padding=20,
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    on_click=self._select_images
                ),
                ft.ElevatedButton(
                    text="Añadir Documentos",
                    icon=ft.Icons.INSERT_DRIVE_FILE,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE_GREY,
                        color=ft.Colors.WHITE,
                        padding=20,
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    on_click=self._select_documents
                ),
                ft.ElevatedButton(
                    text="Limpiar Todo",
                    icon=ft.Icons.CLEAR_ALL,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREY_600,
                        color=ft.Colors.WHITE,
                        padding=20,
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    on_click=self._clear_attachments
                )
            ]
        )
    
    def _create_attachment_preview(self):
        """Create preview area for attachments"""
        self.attachments_container = ft.Column(
            spacing=10,
            controls=[
                ft.Tabs(
                    selected_index=0,
                    tabs=[
                        ft.Tab(text="Imágenes", content=self._create_image_gallery()),
                        ft.Tab(text="Documentos", content=self._create_documents_list()),
                    ]
                )
            ]
        )
        return self.attachments_container
    
    def _create_image_gallery(self):
        """Create image gallery grid"""
        self.image_gallery = ft.GridView(
            width=770,
            height=200,
            runs_count=4,
            max_extent=180,
            child_aspect_ratio=1.2,
            spacing=10,
            run_spacing=10,
        )
        return self.image_gallery
    
    def _create_documents_list(self):
        """Create documents list view"""
        self.documents_list = ft.ListView(
            width=770,
            height=200,
            spacing=5
        )
        return self.documents_list
    
    def _create_history_tab(self):
        """Create the reports history tab"""
        self.history_list = self._create_reports_list()
        self.search_field = ft.TextField(
            label="Buscar informes...",
            hint_text="Filtrar por título o contenido",
            border_color=self.notify_color,
            focused_border_color=self.notify_color,
            width=800,
            on_change=self._filter_reports
        )
        
        return ft.Container(
            padding=20,
            alignment=ft.alignment.center,
            content=ft.Column(
                scroll=ft.ScrollMode.ADAPTIVE,
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Historial de Informes", 
                                   size=22, 
                                   weight=ft.FontWeight.BOLD,
                                   color=self.text_color),
                            ft.IconButton(
                                icon=ft.Icons.REFRESH,
                                icon_color=self.notify_color,
                                tooltip="Recargar historial",
                                on_click=self._reload_history
                            )
                        ]
                    ),
                    self.search_field,
                    self.history_list
                ]
            )
        )
    
    def _create_analysis_dropdown(self):
        """Create dropdown for analysis selection"""
        analyses = self.db_manager.fetch_analyses_by_user(self.user[0])
        return ft.Dropdown(
            options=[
                ft.dropdown.Option(
                    text=f"{analysis[1]} ({analysis[2].strftime('%d/%m/%Y') if isinstance(analysis[2], datetime) else analysis[2] or 'Sin fecha'})",
                    key=analysis[0]
                ) for analysis in analyses
            ],
            label="Seleccione un análisis",
            hint_text="Elija un análisis para generar el informe",
            width=800,
            border_color=self.notify_color,
            focused_border_color=self.notify_color,
            autofocus=True
        )
    
    def _create_reports_list(self):
        """Create list of reports with filtering capability"""
        reports = self.db_manager.fetch_reports_by_user(self.user[0])
        if not reports:
            return ft.Container(
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=48, color=self.notify_color),
                        ft.Text("No hay informes generados aún.", 
                               size=18, 
                               color=self.text_color),
                        ft.ElevatedButton(
                            text="Crear primer informe",
                            icon=ft.Icons.ADD,
                            on_click=lambda _: setattr(self.tabs, "selected_index", 0)
                        )
                    ]
                ),
                height=300,
                alignment=ft.alignment.center
            )

        return ft.Column(
            spacing=15,
            controls=[
                self._create_report_card(report) for report in reports
            ]
        )
    
    def _create_report_card(self, report):
        """Create an individual report card for the history list"""
        report_id, title, content, created_at = report
        return ft.Card(
            elevation=4,
            shape=ft.RoundedRectangleBorder(radius=10),
            content=ft.Container(
                padding=15,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(title, 
                                       size=16, 
                                       weight=ft.FontWeight.BOLD,
                                       color=self.text_color),
                                ft.Text(
                                    created_at.strftime("%d/%m/%Y %H:%M") if isinstance(created_at, datetime) else created_at or "Sin fecha",
                                    size=12,
                                    color=ft.Colors.GREY_500
                                )
                            ]
                        ),
                        ft.Text(
                            f"{content[:150]}..." if len(content) > 150 else content,
                            size=14,
                            color=self.text_color2
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            spacing=5,
                            controls=[
                                ft.OutlinedButton(
                                    text="Vista Previa",
                                    icon=ft.Icons.VISIBILITY,
                                    on_click=lambda e, rid=report_id: self._preview_report(rid)
                                ),
                                ft.OutlinedButton(
                                    text="Descargar PDF",
                                    icon=ft.Icons.DOWNLOAD,
                                    on_click=lambda e, rid=report_id: self.download_report(rid)
                                ),
                                ft.OutlinedButton(
                                    text="Eliminar",
                                    icon=ft.Icons.DELETE,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.RED
                                    ),
                                    on_click=lambda e, rid=report_id: self.delete_report(rid)
                                )
                            ]
                        )
                    ]
                )
            )
        )
        
    def _format_text(self, format_type):
        """Apply formatting to the text in the report editor"""
        current_value = self.report_text_field.value

        # Append formatting markers to the text
        if format_type == "bold":
            new_text = f"{current_value}**texto**"
        elif format_type == "italic":
            new_text = f"{current_value}*texto*"
        elif format_type == "bullet":
            new_text = f"{current_value}\n- Elemento de lista"
        elif format_type == "numbered":
            new_text = f"{current_value}\n1. Primer elemento"
        else:
            new_text = current_value

        # Update the text field
        self.report_text_field.value = new_text
        self.report_text_field.update()
        self._update_report_content(None)
    
    def _insert_image_url(self):
        """Show dialog to insert image from URL"""
        def insert_image(e):
            if url_input.value:
                markdown_image = f"\n\n![Descripción de la imagen]({url_input.value})\n\n"
                self.report_text_field.value += markdown_image
                self.report_text_field.update()
                self._update_report_content(None)
                self.page.dialog.open = False
                self.page.update()
        
        url_input = ft.TextField(label="URL de la imagen", width=400)
        insert_dialog = ft.AlertDialog(
            title=ft.Text("Insertar imagen desde URL"),
            content=url_input,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(self.page.dialog, "open", False)),
                ft.TextButton("Insertar", on_click=insert_image)
            ]
        )
        
        self.page.dialog = insert_dialog
        insert_dialog.open = True
        self.page.update()

    def _select_images(self, e):
        """Handle image selection using FilePicker"""
        file_picker = ft.FilePicker()
        self.page.overlay.append(file_picker)
        file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["jpg", "jpeg", "png", "gif"],
            on_result=lambda e: self._handle_image_selection(e)
        )

    def _handle_image_selection(self, e):
        """Process selected images and update the gallery"""
        if not e.files:
            return
            
        self.selected_images = [(file.path, file.name) for file in e.files]
        self._update_image_gallery()
        
    def _update_image_gallery(self):
        """Update the image gallery with selected images"""
        self.image_gallery.controls.clear()
        
        if not self.selected_images:
            self.image_gallery.controls.append(
                ft.Container(
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.IMAGE, size=48, color=ft.Colors.GREY_400),
                            ft.Text("No hay imágenes seleccionadas", 
                                   color=ft.Colors.GREY_500)
                        ]
                    ),
                    height=150,
                    alignment=ft.alignment.center
                )
            )
        else:
            for img_path, img_name in self.selected_images:
                self.image_gallery.controls.append(
                    ft.Column(
                        spacing=5,
                        controls=[
                            ft.Image(
                                src=img_path,
                                width=150,
                                height=100,
                                fit=ft.ImageFit.CONTAIN,
                                border_radius=ft.border_radius.all(5)
                            ),
                            ft.Text(
                                img_name,
                                size=12,
                                color=self.text_color2,
                                text_align=ft.TextAlign.CENTER,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS
                            )
                        ]
                    )
                )
        
        self.image_gallery.update()
    
    def _select_documents(self, e):
        """Handle document selection using FilePicker"""
        file_picker = ft.FilePicker()
        self.page.overlay.append(file_picker)
        file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["pdf", "docx", "txt", "xlsx"],
            on_result=lambda e: self._handle_document_selection(e)
        )
        
    def _handle_document_selection(self, e):
        """Process selected documents and update the list"""
        if not e.files:
            return
        self.selected_documents = [(file.path, file.name) for file in e.files]
        self._update_documents_list()
        
    def _update_documents_list(self):
        """Update the documents list with selected files"""
        self.documents_list.controls.clear()
        
        if not self.selected_documents:
            self.documents_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.INSERT_DRIVE_FILE, size=48, color=ft.Colors.GREY_400),
                            ft.Text("No hay documentos seleccionados", 
                                   color=ft.Colors.GREY_500)
                        ]
                    ),
                    height=150,
                    alignment=ft.alignment.center
                )
            )
        else:
            for doc_path, doc_name in self.selected_documents:
                icon = ft.Icons.PICTURE_AS_PDF if doc_name.lower().endswith(".pdf") else (
                    ft.Icons.DESCRIPTION if doc_name.lower().endswith((".doc", ".docx")) else (
                    ft.Icons.TABLE_CHART if doc_name.lower().endswith((".xls", ".xlsx")) else ft.Icons.INSERT_DRIVE_FILE
                ))
                
                self.documents_list.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(icon, color=self.notify_color),
                        title=ft.Text(doc_name, size=14, color=self.text_color),
                        trailing=ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, path=doc_path: self._remove_document(path)
                        )
                    )
                )
        
        self.documents_list.update()
    
    def _remove_document(self, doc_path):
        """Remove a document from the selection"""
        self.selected_documents = [doc for doc in self.selected_documents if doc[0] != doc_path]
        self._update_documents_list()
    
    def _clear_attachments(self, e):
        """Clear all attachments"""
        self.selected_images = []
        self.selected_documents = []
        self._update_image_gallery()
        self._update_documents_list()
    
    def _on_text_change(self, e):
        """Handle text change with a delay"""
        if self.update_timer:
            self.update_timer.cancel()  # Cancel the previous timer if still running

        # Start a new timer
        self.update_timer = threading.Timer(5.0, self._update_report_content)
        self.update_timer.start()

    def _update_report_content(self):
        """Update report content and preview"""
        self.report_content = self.report_text_field.value
        # Update markdown preview
        if hasattr(self, 'markdown_preview'):
            self.markdown_preview.content.value = markdown(self.report_content)
            self.markdown_preview.content.update()

    def _filter_reports(self, e):
        """Filter reports based on search input"""
        search_term = e.control.value.lower()
        reports = self.db_manager.fetch_reports_by_user(self.user[0])
        
        if not search_term:
            self.history_list.controls = [
                self._create_report_card(report) for report in reports
            ]
        else:
            filtered_reports = [
                report for report in reports 
                if search_term in report[1].lower() or search_term in report[2].lower()
            ]
            self.history_list.controls = [
                self._create_report_card(report) for report in filtered_reports
            ]
        
        self.history_list.update()
    
    def _preview_report(self, report_id):
        """Show a preview of the report in a dialog"""
        report = self.db_manager.fetch_reports_by_user(report_id)
        if not report:
            self._show_snackbar("Informe no encontrado", is_error=True)
            return
        
        _, title, content, _ = report
        
        preview_dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Container(
                width=600,
                height=400,
                content=ft.Column(
                    scroll=ft.ScrollMode.ADAPTIVE,
                    controls=[
                        ft.Markdown(content, extension_set="gitHubWeb")
                    ]
                )
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self._close_dialog(e))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.page.dialog = preview_dialog
        preview_dialog.open = True
        self.page.update()
    
    def _close_dialog(self, e):
        """Close the currently open dialog"""
        self.page.dialog.open = False
        self.page.update()
    
    def _reload_history(self, e=None):
        """Reload the reports history"""
        self.tabs.tabs[1].content = self._create_history_tab()
        self.page.update()
        self._show_snackbar("Historial actualizado")
    
    def _show_snackbar(self, message, is_error=False):
        """Show a snackbar notification"""
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_400 if is_error else ft.Colors.GREEN_400,
            behavior=ft.SnackBarBehavior.FLOATING,
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=10
        )
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()
    
    def save_report(self, e):
        """Save the report to database"""
        analysis_id = self.analysis_dropdown.value
        title = self.report_title_field.value
        content = self.report_content
        
        if not analysis_id:
            self._show_snackbar("Seleccione un análisis primero", is_error=True)
            return
        
        if not title or not content:
            self._show_snackbar("Complete el título y contenido del informe", is_error=True)
            return
        
        try:
            self.db_manager.insert_report(
                user_id=self.user[0],
                analysis_id=analysis_id,
                title=title,
                content=content
            )
            
            # Reset form
            self.report_title_field.value = ""
            self.report_text_field.value = ""
            self.selected_images = []
            self.selected_documents = []
            self._update_image_gallery()
            self._update_documents_list()
            self._update_report_content(None)
            self.report_text_field.focus()
            
            self._show_snackbar("Informe guardado exitosamente")
            self._reload_history()
        except Exception as ex:
            self._show_snackbar(f"Error al guardar: {str(ex)}", is_error=True)
    
    def download_report(self, report_id):
        """Download report as PDF (simulated)"""
        report = self.db_manager.fetch_reports_by_user(report_id)
        if not report:
            self._show_snackbar("Informe no encontrado", is_error=True)
            return
        
        _, title, content, _ = report
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                tmp.write(f"Informe: {title}\n\n".encode('utf-8'))
                tmp.write(content.encode('utf-8'))
                tmp_path = tmp.name
            
            self.page.launch_url(f"file://{tmp_path}")
            self._show_snackbar(f"Descarga iniciada: {title}")
            
            self.page.run_task(lambda: os.unlink(tmp_path), delay=10)
        except Exception as ex:
            self._show_snackbar(f"Error al descargar: {str(ex)}", is_error=True)
    
    def delete_report(self, report_id):
        """Delete a report after confirmation"""
        def confirm_delete(e):
            try:
                self.db_manager.delete_report_by_id(report_id)
                confirm_dialog.open = False
                self.page.update()
                self._show_snackbar("Informe eliminado")
                self._reload_history()
            except Exception as ex:
                self._show_snackbar(f"Error al eliminar: {str(ex)}", is_error=True)
        
        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Está seguro que desea eliminar este informe permanentemente?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._close_dialog(e)),
                ft.TextButton(
                    "Eliminar",
                    style=ft.ButtonStyle(color=ft.Colors.RED),
                    on_click=confirm_delete
                )
            ]
        )
        
        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()