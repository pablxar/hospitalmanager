import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AnalisisExploratorio:
    def __init__(self, page, nombre_archivo=None):
        self.page = page
        self.nombre_archivo = nombre_archivo

    def analisis_estadistico(self, df: pd.DataFrame):
        resumen = df.describe(include='all')
        return resumen

    def generar_graficos(self, df: pd.DataFrame):
        graficos = {}

        # Histograma de edades en memoria
        if 'Edad en Años' in df.columns:
            fig, ax = plt.subplots()
            df['Edad en Años'].hist(bins=20, ax=ax)
            ax.set_title('Histograma de Edad')
            ax.set_xlabel('Edad')
            ax.set_ylabel('Frecuencia')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['histograma_edad.png'] = buf.getvalue()

        # Barras: Motivo de egreso en memoria
        if 'Motivo Egreso (descripción)' in df.columns:
            fig, ax = plt.subplots()
            df['Motivo Egreso (descripción)'].value_counts().plot(kind='bar', ax=ax)
            ax.set_title('Frecuencia por Motivo de Egreso')
            ax.set_xlabel('Motivo de Egreso')
            ax.set_ylabel('Frecuencia')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['barras_motivo_egreso.png'] = buf.getvalue()

        # Barras: Tipo de actividad en memoria
        if 'Tipo Actividad' in df.columns:
            fig, ax = plt.subplots()
            df['Tipo Actividad'].value_counts().plot(kind='bar', color='orange', ax=ax)
            ax.set_title('Distribución por Tipo de Actividad')
            ax.set_xlabel('Tipo de Actividad')
            ax.set_ylabel('Frecuencia')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['barras_tipo_actividad.png'] = buf.getvalue()

        return graficos

    def ejecutar_analisis(self, df: pd.DataFrame, update_progress=None):
        resultados = {}
        resultados['estadisticas'] = self.analisis_estadistico(df)
        if update_progress:
            update_progress()
        resultados['graficos'] = self.generar_graficos(df)
        if update_progress:
            update_progress()
        return resultados

    @staticmethod
    def get_total_steps():
        return 4
