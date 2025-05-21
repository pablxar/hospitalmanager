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

        if 'Estancia del episodio' in df.columns and 'DG01 principal (descripcion)' in df.columns:
            tablas['estancia_promedio_por_diagnostico'] = df.groupby('DG01 principal (descripcion)', observed=False)['Estancia del episodio'].mean().sort_values(ascending=False).reset_index()

        if 'Valor a Pagar' in df.columns and 'DG01 principal (descripcion)' in df.columns:
            tablas['costos_promedio_por_diagnostico'] = df.groupby('DG01 principal (descripcion)', observed=False)['Valor a Pagar'].mean().sort_values(ascending=False).reset_index()

        if 'Tipo Actividad' in df.columns and 'Estancia del episodio' in df.columns:
            tablas['estancia_promedio_por_tipo_actividad'] = df.groupby('Tipo Actividad', observed=False)['Estancia del episodio'].mean().sort_values(ascending=False).reset_index()

        if 'Edad en Años' in df.columns and 'DG01 principal (descripcion)' in df.columns:
            df['Grupo Etario'] = pd.cut(df['Edad en Años'], bins=[0, 18, 59, 120], labels=["0-18", "19-59", "60+"])
            tablas['frecuencia_diagnosticos_por_edad'] = df.groupby(['Grupo Etario', 'DG01 principal (descripcion)'], observed=False).size().unstack(fill_value=0)

        return tablas

    def generar_graficos(self, df: pd.DataFrame):
        graficos = {}

        if 'Valor a Pagar' in df.columns and 'Previsión' in df.columns:
            fig, ax = plt.subplots()
            df.boxplot(column='Valor a Pagar', by='Previsión', grid=False, ax=ax)
            ax.set_title('Distribución del Valor a Pagar por Previsión')
            ax.set_xlabel('Previsión')
            ax.set_ylabel('Valor a Pagar')
            plt.suptitle('')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['boxplot_valor_por_prevision.png'] = buf.getvalue()

        if 'Peso GRD medio' in df.columns and 'Valor a Pagar' in df.columns:
            fig, ax = plt.subplots()
            ax.scatter(df['Peso GRD medio'], df['Valor a Pagar'])
            ax.set_title('Relación entre Peso GRD medio y Valor a Pagar')
            ax.set_xlabel('Peso GRD medio')
            ax.set_ylabel('Valor a Pagar')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            graficos['scatter_peso_vs_valor.png'] = buf.getvalue()

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
