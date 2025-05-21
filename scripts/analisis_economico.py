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

        # Comparación entre Precio Base y Valor a Pagar (promedio)
        if 'Valor Precio Base' in df.columns and 'Valor a Pagar' in df.columns:
            tablas['comparacion_valores'] = df[['Valor Precio Base', 'Valor a Pagar']].describe().loc[['mean', 'std', 'min', 'max']]

        # Diagnósticos con mayor desviación entre base y valor real
        if 'DG01 principal (descripcion)' in df.columns:
            df['Desviacion'] = df['Valor a Pagar'] - df['Valor Precio Base']
            tablas['desviacion_promedio_por_diagnostico'] = df.groupby('DG01 principal (descripcion)')['Desviacion'].mean().sort_values(ascending=False).reset_index()

        # Promedio de costo por día de estancia
        if 'Valor a Pagar' in df.columns and 'Estancia del episodio' in df.columns:
            df['Costo por Día'] = df['Valor a Pagar'] / df['Estancia del episodio'].replace(0, 1)
            tablas['costo_promedio_por_dia'] = df.groupby('Tipo Actividad')['Costo por Día'].mean().sort_values(ascending=False).reset_index()

        return tablas

    def generar_graficos(self, df: pd.DataFrame):
        graficos = {}

        # Comparar Valor a Pagar vs Valor Precio Base
        if 'Valor a Pagar' in df.columns and 'Valor Precio Base' in df.columns:
            fig, ax = plt.subplots()
            ax.scatter(df['Valor Precio Base'], df['Valor a Pagar'])
            ax.set_title('Valor a Pagar vs Precio Base')
            ax.set_xlabel('Valor Precio Base')
            ax.set_ylabel('Valor a Pagar')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['scatter_valores.png'] = buf.getvalue()

        # Costo por día vs tipo de actividad
        if 'Costo por Día' in df.columns and 'Tipo Actividad' in df.columns:
            fig, ax = plt.subplots()
            df.boxplot(column='Costo por Día', by='Tipo Actividad', grid=False, ax=ax)
            ax.set_title('Costo por Día según Tipo de Actividad')
            ax.set_xlabel('Tipo de Actividad')
            ax.set_ylabel('Costo por Día')
            plt.suptitle('')  # Quita título automático
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['boxplot_costo_por_dia.png'] = buf.getvalue()

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
        return 5
