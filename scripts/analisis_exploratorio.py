import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AnalisisExploratorio:
    def __init__(self, page, nombre_archivo=None):
        self.page = page
        self.nombre_archivo = nombre_archivo

    def generar_tablas(self, df: pd.DataFrame):
        tablas = {}

        # Conteo por Motivo Egreso (Descripción)
        if 'Motivo Egreso (Descripción)' in df.columns:
            conteo = df['Motivo Egreso (Descripción)'].value_counts().reset_index()
            conteo.columns = ['Motivo Egreso', 'Frecuencia']
            tablas['conteo_motivo_egreso'] = conteo

        # Distribución por Tipo Ingreso (Descripción)
        if 'Tipo Ingreso (Descripción)' in df.columns:
            distribucion = df['Tipo Ingreso (Descripción)'].value_counts().reset_index()
            distribucion.columns = ['Tipo Ingreso', 'Frecuencia']
            tablas['distribucion_tipo_ingreso'] = distribucion

        # Distribución por Sexo (Desc)
        if 'Sexo (Desc)' in df.columns:
            distribucion_sexo = df['Sexo (Desc)'].value_counts().reset_index()
            distribucion_sexo.columns = ['Sexo', 'Frecuencia']
            tablas['distribucion_sexo'] = distribucion_sexo

        # Puedes agregar más tablas según tu análisis

        return tablas

    def generar_graficos(self, df: pd.DataFrame):
        graficos = {}

        # Histograma de Edad en años
        if 'Edad en años' in df.columns:
            fig, ax = plt.subplots()
            df['Edad en años'].hist(bins=20, ax=ax)
            ax.set_title('Histograma de Edad')
            ax.set_xlabel('Edad')
            ax.set_ylabel('Frecuencia')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['histograma_edad.png'] = buf.getvalue()

        # Barras Motivo Egreso (Descripción)
        if 'Motivo Egreso (Descripción)' in df.columns:
            fig, ax = plt.subplots()
            df['Motivo Egreso (Descripción)'].value_counts().plot(kind='bar', ax=ax)
            ax.set_title('Frecuencia por Motivo de Egreso')
            ax.set_xlabel('Motivo de Egreso')
            ax.set_ylabel('Frecuencia')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['barras_motivo_egreso.png'] = buf.getvalue()

        # Barras Tipo Ingreso (Descripción)
        if 'Tipo Ingreso (Descripción)' in df.columns:
            fig, ax = plt.subplots()
            df['Tipo Ingreso (Descripción)'].value_counts().plot(kind='bar', color='orange', ax=ax)
            ax.set_title('Distribución por Tipo de Ingreso')
            ax.set_xlabel('Tipo de Ingreso')
            ax.set_ylabel('Frecuencia')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['barras_tipo_ingreso.png'] = buf.getvalue()

        return graficos

    def ejecutar_analisis(self, df: pd.DataFrame, update_progress=None):
        resultados = {}
        resultados['tablas'] = self.generar_tablas(df)
        if update_progress:
            update_progress()
        resultados['graficos'] = self.generar_graficos(df)
        if update_progress:
            update_progress()
        return resultados

    @staticmethod
    def get_total_steps():
        return 6
