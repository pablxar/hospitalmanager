import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AnalisisClinicoGestion:
    def __init__(self, page, nombre_archivo=None):
        self.page = page
        self.nombre_archivo = nombre_archivo

    def generar_tablas(self, df: pd.DataFrame):
        tablas = {}

        # Siempre trabajar sobre una copia para evitar SettingWithCopyWarning
        df = df.copy()
        # Promedio de estancia por "Diag 01 Principal (cod+des)"
        if 'Estancia del Episodio' in df.columns and 'Diag 01 Principal (cod+des)' in df.columns:
            tablas['estancia_promedio_por_diagnostico'] = (
                df.groupby('Diag 01 Principal (cod+des)', observed=False)['Estancia del Episodio']
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )

        # Promedio de estancia por "Tipo Ingreso (Descripción)"
        if 'Tipo Ingreso (Descripción)' in df.columns and 'Estancia del Episodio' in df.columns:
            tablas['estancia_promedio_por_tipo_ingreso'] = (
                df.groupby('Tipo Ingreso (Descripción)', observed=False)['Estancia del Episodio']
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )

        # Frecuencia de diagnósticos por grupo etario
        if 'Edad en años' in df.columns and 'Diag 01 Principal (cod+des)' in df.columns:
            df.loc[:, 'Grupo Etario'] = pd.cut(df['Edad en años'], bins=[0, 18, 59, 120], labels=["0-18", "19-59", "60+"])
            tablas['frecuencia_diagnosticos_por_edad'] = (
                df.groupby(['Grupo Etario', 'Diag 01 Principal (cod+des)'], observed=False)
                .size()
                .unstack(fill_value=0)
            )

        return tablas

    def generar_graficos(self, df: pd.DataFrame):
        graficos = {}

        # Siempre trabajar sobre una copia para evitar SettingWithCopyWarning
        df = df.copy()
        # Boxplot de Estancia del Episodio por "Prevision (Desc)"
        if 'Estancia del Episodio' in df.columns and 'Prevision (Desc)' in df.columns:
            fig, ax = plt.subplots()
            df.boxplot(column='Estancia del Episodio', by='Prevision (Desc)', grid=False, ax=ax)
            ax.set_title('Distribución de Estancia por Previsión')
            ax.set_xlabel('Previsión')
            ax.set_ylabel('Estancia del Episodio')
            plt.suptitle('')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['boxplot_estancia_por_prevision.png'] = buf.getvalue()

        # Scatter Peso GRD vs Estancia del Episodio (en lugar de Valor a Pagar)
        if 'Peso GRD' in df.columns and 'Estancia del Episodio' in df.columns:
            fig, ax = plt.subplots()
            ax.scatter(df['Peso GRD'], df['Estancia del Episodio'])
            ax.set_title('Relación entre Peso GRD y Estancia del Episodio')
            ax.set_xlabel('Peso GRD')
            ax.set_ylabel('Estancia del Episodio')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['scatter_peso_vs_estancia.png'] = buf.getvalue()

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
