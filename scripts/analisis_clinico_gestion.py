import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AnalisisClinicoGestion:
    def __init__(self, page, nombre_archivo=None):
        self.page = page
        self.nombre_archivo = nombre_archivo

    def generar_tablas(self, df: pd.DataFrame, update_progress=None):
        resultados = {}
        df = df.copy()
        df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
        df = df.dropna(subset=['Fecha de egreso completa'])
        df.loc[:, 'Año'] = df['Fecha de egreso completa'].dt.year #AÑO SIN DECIMALES
        df.loc[:, 'Mes'] = df['Fecha de egreso completa'].dt.month
                # Asegurar que el año sea un entero en todas las tablas y gráficos
        if 'Año' in df.columns:
            df['Año'] = df['Año'].astype(int)
        max_fecha = df['Fecha de egreso completa'].max()
        max_anio = max_fecha.year
        max_mes = max_fecha.month
        df_filtrado = df[(df['Mes'] <= max_mes) | (df['Año'] < max_anio)].copy()

        # Promedio de estancia por "Tipo Ingreso (Descripción)"
        if 'Tipo Ingreso (Descripción)' in df.columns and 'Estancia del Episodio' in df.columns:
            resultados['estancia_promedio_por_tipo_ingreso'] = (
                df.groupby('Tipo Ingreso (Descripción)', observed=False)['Estancia del Episodio']
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )
            # Convertir el año a entero en todas las tablas generadas
            for key, table in resultados.items():
                if 'Año' in table.columns:
                    table['Año'] = table['Año'].astype(int)
            if update_progress:
                update_progress()
        return resultados

    def generar_graficos(self, df: pd.DataFrame, update_progress=None):
        resultados = {}
        
        # Definir colores constantes para los años
        COLOR_2024 = '#4CAF50'  # Verde
        COLOR_2025 = '#2196F3'  # Azul
        
        df = df.copy()
        # Procesar fechas
        df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
        df = df.dropna(subset=['Fecha de egreso completa'])
        df['Año'] = df['Fecha de egreso completa'].dt.year
        df['Mes'] = df['Fecha de egreso completa'].dt.month

        # Asegurar que el año sea un entero en todas las tablas y gráficos
        if 'Año' in df.columns:
            df['Año'] = df['Año'].astype(int)

        # Validación de datos
        if df.empty:
            print("⚠️ El DataFrame está vacío luego del procesamiento de fechas.")
            return resultados

        # Limitar al rango de comparación acumulado (hasta el mes más reciente del último año)
        max_fecha = df['Fecha de egreso completa'].max()
        max_anio = max_fecha.year
        max_mes = max_fecha.month
        anios_comparar = [max_anio - 1, max_anio]

        df_comp = df[df['Año'].isin(anios_comparar) & (df['Mes'] <= max_mes)].copy()
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
            resultados['boxplot_estancia_por_prevision.png'] = buf.getvalue()
            if update_progress:
                update_progress()
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
            resultados['scatter_peso_vs_estancia.png'] = buf.getvalue()
            if update_progress:
                update_progress()
        return resultados

    def ejecutar_analisis(self, df: pd.DataFrame, update_progress=None):
        resultados = {}
        resultados['tablas'] = self.generar_tablas(df, update_progress)
        resultados['graficos'] = self.generar_graficos(df, update_progress)
        return resultados

    @staticmethod
    def get_total_steps():
        return 3
