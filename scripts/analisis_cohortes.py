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

    def generar_tablas(self, df: pd.DataFrame):
        resultados = {}

        # Definir grupo etario según "Edad en años"
        if 'Edad en años' in df.columns and 'Diag 01 Principal (cod+des)' in df.columns:
            df['Grupo Etario'] = pd.cut(df['Edad en años'], bins=[0, 18, 59, 120], labels=["0-18", "19-59", "60+"])
            tabla_diagnosticos = df.groupby(['Grupo Etario', 'Diag 01 Principal (cod+des)'], observed=False).size().unstack(fill_value=0)
            resultados['diagnosticos_por_grupo_etario'] = tabla_diagnosticos

        # Promedio de estancia por grupo etario
        if 'Estancia del Episodio' in df.columns:
            promedio_estancia = df.groupby('Grupo Etario')['Estancia del Episodio'].mean().reset_index()
            resultados['promedio_estancia_por_grupo_etario'] = promedio_estancia

        # Conteo de egresos por mes (usando "Fecha egreso completa")
        if 'Fecha de egreso completa' in df.columns:
            df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
            df = df.dropna(subset=['Fecha de egreso completa'])
            df['Mes de Egreso'] = df['Fecha de egreso completa'].dt.to_period('M')
            conteo_egresos = df.groupby('Mes de Egreso', observed=False).size().reset_index(name='Egresos')
            resultados['egresos_por_mes'] = conteo_egresos

        return resultados

    def generar_graficos(self, df: pd.DataFrame):
        resultados = {}

        # Heatmap diagnósticos por grupo etario
        if 'Edad en años' in df.columns and 'Diag 01 Principal (cod+des)' in df.columns:
            df['Grupo Etario'] = pd.cut(df['Edad en años'], bins=[0, 18, 59, 120], labels=["0-18", "19-59", "60+"])
            heatmap_data = df.pivot_table(index='Grupo Etario', columns='Diag 01 Principal (cod+des)', aggfunc='size', fill_value=0)
            plt.figure(figsize=(14, 10))
            sns.heatmap(heatmap_data, annot=False, cmap="YlGnBu")
            plt.title('Heatmap de Diagnósticos por Grupo Etario')
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            resultados['heatmap_diagnosticos_etario.png'] = buffer.getvalue()
            plt.close()

        # Línea de egresos mensuales
        if 'Fecha de egreso completa' in df.columns:
            df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
            df = df.dropna(subset=['Fecha de egreso completa'])
            df['Mes de Egreso'] = df['Fecha de egreso completa'].dt.to_period('M')
            egresos_mensuales = df.groupby('Mes de Egreso', observed=False).size()
            plt.figure(figsize=(12, 6))
            egresos_mensuales.plot(kind='line')
            plt.title('Línea de Egresos Mensuales')
            plt.xlabel('Mes de Egreso')
            plt.ylabel('Cantidad de Egresos')
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            resultados['linea_egresos_mensuales.png'] = buffer.getvalue()
            plt.close()

        # Barras promedio estancia por grupo etario
        if 'Edad en años' in df.columns and 'Estancia del Episodio' in df.columns:
            df['Grupo Etario'] = pd.cut(df['Edad en años'], bins=[0, 18, 59, 120], labels=["0-18", "19-59", "60+"])
            promedio_estancia = df.groupby('Grupo Etario')['Estancia del Episodio'].mean()
            plt.figure(figsize=(8, 5))
            promedio_estancia.plot(kind='bar', color='skyblue')
            plt.title('Promedio de Estancia por Grupo Etario')
            plt.xlabel('Grupo Etario')
            plt.ylabel('Estancia Promedio')
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            resultados['barras_promedio_estancia.png'] = buffer.getvalue()
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
        return 6
