import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AnalisisEconomico:
    def __init__(self, page, nombre_archivo=None):
        self.page = page
        self.nombre_archivo = nombre_archivo

    def generar_tablas(self, df: pd.DataFrame):
        tablas = {}

        # Conteo por "Especialidad (Descripción)"
        if 'Especialidad (Descripción )' in df.columns:
            conteo_esp = df['Especialidad (Descripción )'].value_counts().reset_index()
            conteo_esp.columns = ['Especialidad', 'Frecuencia']
            tablas['conteo_especialidad'] = conteo_esp

        # Distribución por "Nivel de severidad (Descripción)"
        if 'Nivel de severidad (Descripción)' in df.columns:
            distrib_severidad = df['Nivel de severidad (Descripción)'].value_counts().reset_index()
            distrib_severidad.columns = ['Nivel de severidad', 'Frecuencia']
            tablas['distribucion_nivel_severidad'] = distrib_severidad

        # Promedio de estancia por nivel de severidad
        if 'Nivel de severidad (Descripción)' in df.columns and 'Estancia del Episodio' in df.columns:
            promedio_estancia = df.groupby('Nivel de severidad (Descripción)')['Estancia del Episodio'].mean().reset_index()
            tablas['promedio_estancia_por_severidad'] = promedio_estancia

        return tablas

    def generar_graficos(self, df: pd.DataFrame):
        graficos = {}

        # Barras por Especialidad
        if 'Especialidad (Descripción )' in df.columns:
            fig, ax = plt.subplots()
            df['Especialidad (Descripción )'].value_counts().plot(kind='bar', ax=ax)
            ax.set_title('Frecuencia por Especialidad')
            ax.set_xlabel('Especialidad')
            ax.set_ylabel('Frecuencia')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['barras_especialidad.png'] = buf.getvalue()

        # Barras por Nivel de severidad
        if 'Nivel de severidad (Descripción)' in df.columns:
            fig, ax = plt.subplots()
            df['Nivel de severidad (Descripción)'].value_counts().plot(kind='bar', color='orange', ax=ax)
            ax.set_title('Distribución por Nivel de severidad')
            ax.set_xlabel('Nivel de severidad')
            ax.set_ylabel('Frecuencia')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['barras_nivel_severidad.png'] = buf.getvalue()

        # Barras promedio estancia por severidad
        if 'Nivel de severidad (Descripción)' in df.columns and 'Estancia del Episodio' in df.columns:
            promedio_estancia = df.groupby('Nivel de severidad (Descripción)')['Estancia del Episodio'].mean()
            fig, ax = plt.subplots()
            promedio_estancia.plot(kind='bar', color='skyblue', ax=ax)
            ax.set_title('Promedio de Estancia por Nivel de severidad')
            ax.set_xlabel('Nivel de severidad')
            ax.set_ylabel('Estancia Promedio')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['promedio_estancia_severidad.png'] = buf.getvalue()

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
