import flet as ft
import pandas as pd
from scripts.analisis_exploratorio import AnalisisExploratorio
from scripts.analisis_economico import AnalisisEconomico
from scripts.analisis_clinico_gestion import AnalisisClinicoGestion
from scripts.analisis_cohortes import AnalisisCohortes
import os
from zipfile import ZipFile

def crear_popup_analisis(page: ft.Page):
    progress_bar = ft.ProgressBar(width=400, value=0, visible=False)
    progress_text = ft.Text("0/0", size=16, visible=False)
    error_text = ft.Text("", color=ft.Colors.RED, visible=False)

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

    def ejecutacion(e):
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
            nombre_archivo = os.path.basename(archivo_datos).lower()
            nombre_carpeta = os.path.splitext(nombre_archivo)[0]
            carpeta_salida = f"outputs/{nombre_carpeta}"
            progress_bar.visible = True
            progress_text.visible = True
            upload_btn.visible = False
            error_text.visible = False
            popup.update()
            total_steps = 0
            total_steps += AnalisisExploratorio.get_total_steps()
            total_steps += AnalisisEconomico.get_total_steps()
            total_steps += AnalisisClinicoGestion.get_total_steps()
            total_steps += AnalisisCohortes.get_total_steps()
            current_step = 0
            def update_progress():
                nonlocal current_step
                current_step += 1
                progress_bar.value = current_step / total_steps
                progress_text.value = f"{current_step}/{total_steps}"
                popup.update()
            AnalisisExploratorio(page, carpeta_salida).ejecutar_analisis(df, update_progress)
            AnalisisEconomico(page, carpeta_salida).ejecutar_analisis(df, update_progress)
            AnalisisClinicoGestion(page, carpeta_salida).ejecutar_analisis(df, update_progress)
            AnalisisCohortes(page, carpeta_salida).ejecutar_analisis(df, update_progress)
            progress_bar.visible = False
            progress_text.visible = False
            download_btn.on_click = lambda e: descargar_resultados(e, carpeta_salida, nombre_carpeta)
            download_btn.visible = True
            popup.update()
            page.snack_bar = ft.SnackBar(ft.Text("Análisis finalizado correctamente."))
            page.snack_bar.open = True
            page.update()
            popup.open = False
        else:
            error_text.value = "No se seleccionó ningún archivo."
            error_text.visible = True
            popup.update()

    def crear_zip(carpeta_salida):
        zip_path = f"{carpeta_salida}.zip"
        with ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(carpeta_salida):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, carpeta_salida)
                    zipf.write(file_path, arcname)
        return zip_path

    def descargar_resultados(e, carpeta_salida, nombre_carpeta):
        zip_path = crear_zip(carpeta_salida)
        file_picker.save_file(file_name=f"{nombre_carpeta}.zip")
        file_picker.on_save = lambda e: guardar_zip(e, zip_path)

    def guardar_zip(e, zip_path):
        if e.path:
            os.rename(zip_path, e.path)

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    file_picker.on_result = ejecutacion
    file_picker.on_save = lambda e: guardar_zip(e, None)  # Inicialización segura para evitar errores

    upload_btn = ft.ElevatedButton("Subir Base de Datos", on_click=lambda e: file_picker.pick_files())

    close_btn = ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda e: [setattr(popup, 'open', False), popup.update()])

    download_btn = ft.ElevatedButton("Descargar Resultados", visible=False)

    popup = ft.AlertDialog(
        modal=True,
        open=False,  # No abrir automáticamente
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
    page.dialog = popup
    return popup, file_picker
