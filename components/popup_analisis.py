import flet as ft
import pandas as pd
import io
import asyncio
from zipfile import ZipFile
from datetime import datetime
from database import DatabaseManager
import matplotlib.pyplot as plt

from scripts.analisis_produccion import AnalisisProduccion
from scripts.analisis_economico import AnalisisEconomico
from scripts.analisis_clinico_gestion import AnalisisClinicoGestion
from scripts.analisis_cohortes import AnalisisCohortes

class PopupAnalisisManager:
    def __init__(self, page: ft.Page, user):
        self.page = page
        self.user = user
        self.resultados = {}
        self.current_step = 0
        self.total_steps = 0
        self.zip_buffer = None
        self.db_manager = DatabaseManager()


        self.progress_bar = ft.ProgressBar(width=400, value=0, visible=False)
        self.progress_text = ft.Text("0/0", size=16, visible=False)
        self.error_text = ft.Text("", color=ft.Colors.RED, visible=False)
        self.download_btn = ft.ElevatedButton("Descargar Resultados", visible=False)
        self.upload_btn = ft.ElevatedButton("Subir Base de Datos", on_click=lambda e: self.file_picker.pick_files())
        self.close_btn = ft.IconButton(icon=ft.Icons.CLOSE, on_click=self.cerrar_popup)

        self.file_picker = ft.FilePicker(on_result=self.ejecutar_analisis)
        self.page.overlay.append(self.file_picker)

        self.status_text = ft.Text("", size=16, color=ft.Colors.AMBER, visible=False)
        self.indeterminate_bar = ft.ProgressBar(width=400, visible=False, color=ft.Colors.AMBER, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.AMBER), bar_height=4, value=None)

        self.popup = ft.AlertDialog(
            modal=True,
            open=False,
            content=ft.Column([
                ft.Row([
                    ft.Text("Análisis de Base de Datos", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    self.close_btn
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.upload_btn,
                self.status_text,
                self.indeterminate_bar,
                self.progress_bar,
                self.progress_text,
                self.error_text,
                self.download_btn
            ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        self.download_btn.on_click = self.descargar_resultados

    def crear_zip_en_memoria(self):
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, "w") as zip_file:
            for nombre_analisis, resultados in self.resultados.items():
                tablas = resultados.get('tablas') or {}
                if 'estadisticas' in resultados and isinstance(resultados['estadisticas'], pd.DataFrame):
                    tablas = {'estadisticas': resultados['estadisticas']}
                for nombre_tabla, df in tablas.items():
                    df = df.map(lambda x: f"{x:.4f}" if isinstance(x, (int, float)) else x)
                    ncols = len(df.columns)
                    nrows = len(df)
                    fig_width = max(14, ncols * 1.2)
                    fig_height = max(1, min(0.7 * nrows, 40))
                    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
                    ax.axis('off')
                    col_colors = ['#4CAF50'] * ncols
                    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center', colColours=col_colors)
                    for (row, col), cell in table.get_celld().items():
                        cell.set_linewidth(0.5)
                        if row == 0:
                            cell.set_text_props(weight='bold', color='white', fontsize=14)
                            cell.set_facecolor('#4CAF50')
                        else:
                            cell.set_text_props(fontsize=12)
                            cell.set_facecolor('#F5F5F5')
                    table.auto_set_font_size(False)
                    table.scale(1.5, 1.5)
                    try:
                        plt.tight_layout()
                    except Exception:
                        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format='png', bbox_inches='tight')
                    plt.close(fig)
                    img_buffer.seek(0)
                    zip_file.writestr(f"{nombre_analisis}/tablas/{nombre_tabla}.png", img_buffer.getvalue())
                for nombre_img, img_bytes in resultados.get('graficos', {}).items():
                    zip_file.writestr(f"{nombre_analisis}/graficos/{nombre_img}", img_bytes)
        zip_buffer.seek(0)
        return zip_buffer

    def resetear_estado(self):
        self.resultados = {}
        self.current_step = 0
        self.total_steps = 0
        self.zip_buffer = None
        self.progress_bar.value = 0
        self.progress_bar.visible = False
        self.progress_text.value = ""
        self.progress_text.visible = False
        self.error_text.value = ""
        self.error_text.visible = False
        self.download_btn.visible = False
        self.download_btn.disabled = True  # <-- Deshabilitar por defecto
        self.upload_btn.visible = True

    def cargar_datos(self, path):
        if path.endswith('.xlsx'):
            return pd.read_excel(path, header=2)
        elif path.endswith('.csv'):
            return pd.read_csv(path, header=2)
        else:
            raise ValueError("El archivo debe ser .xlsx o .csv")

    def verificar_columnas(self, df):
        columnas_requeridas = [
            "Año egreso", "Hospital (Descripción)", "GRD", "Especialidad (Descripción )", "Fecha de egreso completa",
            "Sexo (Desc)", "Comuna de residencia ( Desc )", "Fecha ingreso completa", "(SI/NO) VMI", "Motivo Egreso (Descripción)",
            "Prevision (Desc)", "Hospital de procedencia (Des )", "Estancia del Episodio", "(Sí/No) Cancer-Neoplasias",
            "Tipo Ingreso (Descripción)", "Nivel de severidad (Descripción)", "(S/N) Egreso Quirúrgico", "(Si/No) Cesáreas", "Peso GRD",
            "CDM (Descripción)", "Mes egreso (Descripción)", "Edad en años", "Diag 01 Principal (cod+des)", "Estancias [Norma]", "Egresos"
        ]
        faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if faltantes:
            raise ValueError(f"Faltan columnas: {', '.join(faltantes)}")
        return df

    def update_progress(self, etapa=None):
        self.current_step += 1
        self.progress_bar.value = self.current_step / self.total_steps
        self.progress_text.value = f"{self.current_step}/{self.total_steps}"
        if etapa:
            self.status_text.value = f"Procesando etapa: {etapa.capitalize()}..."
        self.status_text.visible = True
        self.indeterminate_bar.visible = True if self.current_step < self.total_steps else False
        self.popup.update()

    def ejecutar_analisis(self, e):
        if self.file_picker.result.files:
            path = self.file_picker.result.files[0].path
            try:
                self.status_text.value = "Cargando y verificando datos..."
                self.status_text.visible = True
                self.indeterminate_bar.visible = True
                self.popup.update()
                df = self.verificar_columnas(self.cargar_datos(path))
                df = df.ffill()  # Llenar valores nulos hacia adelante

                # Convertir columna 'Egresos' a numérico
                df['Egresos'] = pd.to_numeric(df['Egresos'], errors='coerce')

                # Buscar la fila que contiene "Suma Total" en cualquier columna
                suma_total_row = df[df.apply(lambda row: row.astype(str).str.contains("Suma Total", case=False, na=False)).any(axis=1)]

                if not suma_total_row.empty:
                    suma_idx = suma_total_row.index[0]

                    # Acceder directamente al valor en la misma fila, columna 'Egresos'
                    valor_suma_total = df.at[suma_idx, 'Egresos']

                    # Cortar el DataFrame justo antes de esa fila
                    df = df.loc[:suma_idx - 1]

                    # Calcular total real
                    total_egresos = df['Egresos'].sum()

                    print(f"📊 Total de pacientes indicado en 'Suma Total': {int(valor_suma_total)}")
                    print(f"📥 Total de egresos analizados desde la base: {int(total_egresos)}")

                    if int(valor_suma_total) != int(total_egresos):
                        print("⚠️ ¡CUIDADO! La suma de egresos no coincide con el total declarado.")
                else:
                     print("⚠️ No se encontró la fila con 'Suma Total'.")


                # Asegurarse de que la fecha esté en datetime
                df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
                # Si no existe la columna 'Año', crearla vacía
                if 'Año' not in df.columns:
                    df['Año'] = pd.NA
                # Rellenar valores faltantes de 'Año' usando la fecha
                mascara_sin_anio = df['Año'].isna()
                df.loc[mascara_sin_anio, 'Año'] = df.loc[mascara_sin_anio, 'Fecha de egreso completa'].dt.year

            except Exception as ex:
                self.error_text.value = str(ex)
                self.error_text.visible = True
                self.status_text.visible = False
                self.indeterminate_bar.visible = False
                self.popup.update()
                return
            self.progress_bar.visible = True
            self.progress_text.visible = True
            self.upload_btn.visible = False
            self.error_text.visible = False
            self.download_btn.visible = False
            self.download_btn.disabled = True
            self.status_text.value = "Generando tablas de producción..."
            self.status_text.visible = True
            self.indeterminate_bar.visible = True
            self.popup.update()
            self.total_steps = (
                AnalisisProduccion.get_total_steps() +
                AnalisisEconomico.get_total_steps() +
                AnalisisClinicoGestion.get_total_steps() +
                AnalisisCohortes.get_total_steps()
            )
            self.resultados["produccion"] = AnalisisProduccion(self.page, path).ejecutar_analisis(df, lambda: self.update_progress("producción"))
            self.status_text.value = "Generando tablas y gráficos económicos..."
            self.popup.update()
            self.resultados["economico"] = AnalisisEconomico(self.page, path).ejecutar_analisis(df, lambda: self.update_progress("económico"))
            self.status_text.value = "Generando tablas y gráficos clínicos..."
            self.popup.update()
            self.resultados["clinico"] = AnalisisClinicoGestion(self.page, path).ejecutar_analisis(df, lambda: self.update_progress("clínico"))
            self.status_text.value = "Generando tablas y gráficos de cohortes..."
            self.popup.update()
            self.resultados["cohortes"] = AnalisisCohortes(self.page, path).ejecutar_analisis(df, lambda: self.update_progress("cohortes"))
            self.status_text.value = "Comprimiendo resultados..."
            self.popup.update()
            self.progress_bar.visible = False
            self.progress_text.visible = False
            self.zip_buffer = self.crear_zip_en_memoria()
            self.download_btn.visible = True
            self.download_btn.disabled = False
            self.status_text.value = "¡Análisis finalizado! Puedes descargar los resultados."
            self.indeterminate_bar.visible = False
            self.popup.update()
        else:
            self.error_text.value = "No se seleccionó ningún archivo."
            self.error_text.visible = True
            self.status_text.visible = False
            self.indeterminate_bar.visible = False
            self.popup.update()

    def descargar_resultados(self, e):
        if self.zip_buffer:
            self.file_picker.on_result = self.guardar_zip
            self.file_picker.save_file(file_name="resultados.zip")
        else:
            snackbar = ft.SnackBar(
                content=ft.Text("No hay resultados listos para descargar.", color=ft.Colors.WHITE),
                bgcolor="#FFC107",
                behavior=ft.SnackBarBehavior.FLOATING,
            )
            self.page.overlay.append(snackbar)
            snackbar.open = True
            self.page.update()


    def guardar_zip(self, e):
        if self.zip_buffer and e.path:
            try:
                with open(e.path, "wb") as f:
                    f.write(self.zip_buffer.getbuffer())
                now = datetime.now()
                analysis_name = f"Analisis_{now.strftime('%Y-%m-%d_%H-%M-%S')}"
                self.db_manager.insert_analysis(
                    usuario_id=self.user[0],
                    name=analysis_name,
                    date=now.strftime('%Y-%m-%d %H:%M:%S'),
                    file_content=self.zip_buffer.read()
                )
                snackbar = ft.SnackBar(content=ft.Text("Análisis guardado correctamente", color=ft.Colors.WHITE), bgcolor="#4CAF50", behavior=ft.SnackBarBehavior.FLOATING)
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()
            except Exception as ex:
                snackbar = ft.SnackBar(content=ft.Text(f"Error al guardar: {ex}", color=ft.Colors.WHITE), bgcolor="#F44336", behavior=ft.SnackBarBehavior.FLOATING)
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()
        else:
            snackbar = ft.SnackBar(content=ft.Text("No se seleccionó ninguna ruta para guardar.", color=ft.Colors.WHITE), bgcolor="#FFC107", behavior=ft.SnackBarBehavior.FLOATING)
            self.page.overlay.append(snackbar)
            snackbar.open = True
            self.page.update()

    def cerrar_popup(self, e):
        self.resetear_estado()
        self.popup.open = False
        self.popup.update()

    def get_popup(self):
        return self.popup