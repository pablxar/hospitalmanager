import flet as ft
import pandas as pd
import io
from zipfile import ZipFile
from datetime import datetime
from database import DatabaseManager

from scripts.analisis_exploratorio import AnalisisExploratorio
from scripts.analisis_economico import AnalisisEconomico
from scripts.analisis_clinico_gestion import AnalisisClinicoGestion
from scripts.analisis_cohortes import AnalisisCohortes

def crear_zip_en_memoria(resultados_dict):
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        for nombre_analisis, resultados in resultados_dict.items():
            tablas = resultados.get('tablas') or {}
            if 'estadisticas' in resultados and isinstance(resultados['estadisticas'], pd.DataFrame):
                tablas = {'estadisticas': resultados['estadisticas']}
            for nombre_tabla, df in tablas.items():
                csv_bytes = df.to_csv(index=False).encode('utf-8')
                zip_file.writestr(f"{nombre_analisis}/tablas/{nombre_tabla}.csv", csv_bytes)
            graficos = resultados.get('graficos', {})
            for nombre_img, img_bytes in graficos.items():
                zip_file.writestr(f"{nombre_analisis}/graficos/{nombre_img}", img_bytes)
    zip_buffer.seek(0)
    return zip_buffer

def crear_popup_analisis(page: ft.Page):
    progress_bar = ft.ProgressBar(width=400, value=0, visible=False)
    progress_text = ft.Text("0/0", size=16, visible=False)
    error_text = ft.Text("", color=ft.Colors.RED, visible=False)
    download_btn = ft.ElevatedButton("Descargar Resultados", visible=False)

    resultados = {}
    current_step = 0
    total_steps = 0
    zip_buffer = None

    def resetear_estado():
        nonlocal resultados, current_step, total_steps, zip_buffer
        resultados = {}
        current_step = 0
        total_steps = 0
        zip_buffer = None
        progress_bar.value = 0
        progress_bar.visible = False
        progress_text.value = ""
        progress_text.visible = False
        error_text.value = ""
        error_text.visible = False
        download_btn.visible = False
        upload_btn.visible = True

    def cargar_datos(path):
        if path.endswith('.xlsx'):
            return pd.read_excel(path)
        elif path.endswith('.csv'):
            return pd.read_csv(path)
        else:
            raise ValueError("El archivo debe ser .xlsx o .csv")

    def verificar_columnas(df):
        columnas_requeridas = [
            "Episodio CMBD", "Motivo Egreso (descripción)", "Tipo Actividad", "Previsión", "Fecha Ingreso",
            "Fecha Egreso", "Hnp", "GRD codigo", "Peso GRD medio", "Estancia del episodio",
            "Egreso", "DG01 principal (codigo)", "DG01 principal (descripcion)",
            "Edad en Años", "Valor Precio Base", "Valor a Pagar"
        ]
        for col in columnas_requeridas:
            if col not in df.columns:
                raise ValueError(f"Falta la columna requerida: {col}")
        return df

    def update_progress():
        nonlocal current_step, total_steps
        current_step += 1
        progress_bar.value = current_step / total_steps
        progress_text.value = f"{current_step}/{total_steps}"
        popup.update()

    def ejecutar_analisis(e):
        nonlocal resultados, current_step, total_steps
        if file_picker.result.files:
            archivo_datos = file_picker.result.files[0].path
            try:
                df = cargar_datos(archivo_datos)
                df = verificar_columnas(df)
            except Exception as ex:
                error_text.value = str(ex)
                error_text.visible = True
                popup.update()
                return

            progress_bar.visible = True
            progress_text.visible = True
            upload_btn.visible = False
            error_text.visible = False
            download_btn.visible = False
            popup.update()

            total_steps = (
                AnalisisExploratorio.get_total_steps() +
                AnalisisEconomico.get_total_steps() +
                AnalisisClinicoGestion.get_total_steps() +
                AnalisisCohortes.get_total_steps()
            )
            current_step = 0
            resultados = {}

            resultados["exploratorio"] = AnalisisExploratorio(page, archivo_datos).ejecutar_analisis(df, update_progress)
            resultados["economico"] = AnalisisEconomico(page, archivo_datos).ejecutar_analisis(df, update_progress)
            resultados["clinico"] = AnalisisClinicoGestion(page, archivo_datos).ejecutar_analisis(df, update_progress)
            resultados["cohortes"] = AnalisisCohortes(page, archivo_datos).ejecutar_analisis(df, update_progress)

            progress_bar.visible = False
            progress_text.visible = False
            download_btn.visible = True
            popup.update()
        else:
            error_text.value = "No se seleccionó ningún archivo."
            error_text.visible = True
            popup.update()

    # Inicializar la base de datos
    db_manager = DatabaseManager()

    def guardar_zip(event):
        nonlocal zip_buffer
        if zip_buffer and event.path:
            try:
                with open(event.path, "wb") as f:
                    f.write(zip_buffer.getbuffer())

                # Generar nombre del análisis basado en la fecha y hora
                now = datetime.now()
                analysis_name = f"Analisis_{now.strftime('%Y-%m-%d_%H-%M-%S')}"

                # Leer el contenido del archivo .zip para guardarlo en la base de datos
                zip_buffer.seek(0)  # Asegurarse de que el puntero esté al inicio
                zip_content = zip_buffer.read()

                # Guardar en la base de datos
                db_manager.insert_analysis(
                    name=analysis_name,
                    date=now.strftime('%Y-%m-%d %H:%M:%S'),
                    file_content=zip_content  # Guardar el contenido del archivo .zip
                )

                snackbar = ft.SnackBar(
                    content=ft.Text("Análisis guardado correctamente", color=ft.Colors.WHITE),
                    bgcolor="#4CAF50",  # Color verde para éxito
                    behavior=ft.SnackBarBehavior.FLOATING,
                )
                page.overlay.append(snackbar)
                snackbar.open = True
                page.update()
            except Exception as ex:
                snackbar = ft.SnackBar(
                    content=ft.Text(f"Error al guardar el archivo: {ex}", color=ft.Colors.WHITE),
                    bgcolor="#F44336",  # Color rojo para error
                    behavior=ft.SnackBarBehavior.FLOATING,
                )
                page.overlay.append(snackbar)
                snackbar.open = True
                page.update()
        else:
            snackbar = ft.SnackBar(
                content=ft.Text("No se seleccionó ninguna ruta para guardar el archivo.", color=ft.Colors.WHITE),
                bgcolor="#FFC107",  # Color amarillo para advertencia
                behavior=ft.SnackBarBehavior.FLOATING,
            )
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()


    def descargar_resultados(e):
        nonlocal zip_buffer
        zip_buffer = crear_zip_en_memoria(resultados)
        file_picker.on_result = guardar_zip
        file_picker.save_file(file_name="resultados.zip")
        popup.update()

    def cerrar_popup(e):
        resetear_estado()
        popup.open = False
        popup.update()

    file_picker = ft.FilePicker(on_result=ejecutar_analisis)
    page.overlay.append(file_picker)

    upload_btn = ft.ElevatedButton("Subir Base de Datos", on_click=lambda e: file_picker.pick_files())
    download_btn.on_click = descargar_resultados
    close_btn = ft.IconButton(icon=ft.Icons.CLOSE, on_click=cerrar_popup)

    popup = ft.AlertDialog(
        modal=True,
        open=False,
        content=ft.Column([
            ft.Row([
                ft.Text("Análisis de Base de Datos", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                close_btn
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            upload_btn,
            progress_bar,
            progress_text,
            error_text,
            download_btn
        ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
        ),
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    return popup, file_picker
