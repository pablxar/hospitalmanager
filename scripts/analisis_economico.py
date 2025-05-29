import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AnalisisEconomico:
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
        
        # Conteo por "Especialidad (Descripción)"
        if 'Especialidad (Descripción )' in df.columns:
            conteo_esp = df['Especialidad (Descripción )'].value_counts().reset_index()
            conteo_esp.columns = ['Especialidad', 'Frecuencia']
            resultados['conteo_especialidad'] = conteo_esp
            if update_progress:
                update_progress()
        # Distribución por "Nivel de severidad (Descripción)"
        if 'Nivel de severidad (Descripción)' in df.columns:
            distrib_severidad = df['Nivel de severidad (Descripción)'].value_counts().reset_index()
            distrib_severidad.columns = ['Nivel de severidad', 'Frecuencia']
            resultados['distribucion_nivel_severidad'] = distrib_severidad
            if update_progress:
                update_progress()
        # Promedio de estancia por nivel de severidad
        if 'Nivel de severidad (Descripción)' in df.columns and 'Estancia del Episodio' in df.columns:
            promedio_estancia = df.groupby('Nivel de severidad (Descripción)')['Estancia del Episodio'].mean().reset_index()
            resultados['promedio_estancia_por_severidad'] = promedio_estancia
            if update_progress:
                update_progress()

        # Convertir el año a entero en todas las tablas generadas
        for key, table in resultados.items():
            if 'Año' in table.columns:
                table['Año'] = table['Año'].astype(int)

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
            resultados['barras_especialidad.png'] = buf.getvalue()
            if update_progress:
                update_progress()
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
            resultados['barras_nivel_severidad.png'] = buf.getvalue()
            if update_progress:
                update_progress()
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
            resultados['promedio_estancia_severidad.png'] = buf.getvalue()
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
        return 6
