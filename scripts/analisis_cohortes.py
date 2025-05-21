import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

class AnalisisCohortes:
    def __init__(self, page, nombre_archivo=None):
        self.page = page
        self.nombre_archivo = nombre_archivo

    def exportar_tabla_imagen_bytes(self, df: pd.DataFrame):
        import dataframe_image as dfi  # Mantener si lo usas, aunque en zip guardamos csv preferentemente
        buffer = io.BytesIO()
        dfi.export(df, buffer, max_rows=-1, table_conversion="chrome")
        buffer.seek(0)
        return buffer.getvalue()

    def generar_tablas(self, df: pd.DataFrame):
        resultados = {}

        if 'Edad en Años' in df.columns and 'DG01 principal (descripcion)' in df.columns:
            df['Grupo Etario'] = pd.cut(df['Edad en Años'], bins=[0, 18, 59, 120], labels=["0-18", "19-59", "60+"])
            tabla_diagnosticos = df.groupby(['Grupo Etario', 'DG01 principal (descripcion)'], observed=False).size().unstack(fill_value=0)
            resultados['diagnosticos_por_grupo_etario'] = tabla_diagnosticos

        if 'Fecha Ingreso' in df.columns and 'Valor a Pagar' in df.columns:
            df['Fecha Ingreso'] = pd.to_datetime(df['Fecha Ingreso'], errors='coerce')
            df = df.dropna(subset=['Fecha Ingreso'])
            df['Mes de Ingreso'] = df['Fecha Ingreso'].dt.to_period('M')
            tabla_ingresos = df.groupby('Mes de Ingreso', observed=False)['Valor a Pagar'].mean().reset_index()
            resultados['ingresos_por_mes'] = tabla_ingresos

        return resultados

    def generar_graficos(self, df: pd.DataFrame):
        resultados = {}

        if 'Edad en Años' in df.columns and 'DG01 principal (descripcion)' in df.columns:
            df['Grupo Etario'] = pd.cut(df['Edad en Años'], bins=[0, 18, 59, 120], labels=["0-18", "19-59", "60+"])
            heatmap_data = df.pivot_table(index='Grupo Etario', columns='DG01 principal (descripcion)', aggfunc='size', fill_value=0)
            plt.figure(figsize=(10, 8))
            sns.heatmap(heatmap_data, annot=False, cmap="YlGnBu")
            plt.title('Heatmap de Diagnósticos por Grupo Etario')
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            resultados['heatmap_diagnosticos_etario.png'] = buffer.getvalue()
            plt.close()

        if 'Fecha Ingreso' in df.columns and 'Valor a Pagar' in df.columns:
            df['Fecha Ingreso'] = pd.to_datetime(df['Fecha Ingreso'], errors='coerce')
            df = df.dropna(subset=['Fecha Ingreso'])
            df['Mes de Ingreso'] = df['Fecha Ingreso'].dt.to_period('M')

            ingresos_mensuales = df.groupby('Mes de Ingreso', observed=False)['Valor a Pagar'].sum()
            plt.figure()
            ingresos_mensuales.plot(kind='line')
            plt.title('Línea de Ingresos Mensuales')
            plt.xlabel('Mes de Ingreso')
            plt.ylabel('Ingresos Totales')
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            resultados['linea_ingresos_mensuales.png'] = buffer.getvalue()
            plt.close()

        return resultados

    def ejecutar_analisis(self, df: pd.DataFrame, update_progress=None):
        tablas = self.generar_tablas(df)
        if update_progress:
            update_progress()
        graficos = self.generar_graficos(df)
        if update_progress:
            update_progress()
        return {"tablas": tablas, "graficos": graficos}

    @staticmethod
    def get_total_steps():
        return 4
