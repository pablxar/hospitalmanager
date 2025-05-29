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

       # Promedio de estancia por grupo etario
        if 'Estancia del Episodio' in df.columns:
            # Asignar grupos etarios usando pd.cut con los rangos especificados
            df.loc[:, 'Grupo Etario'] = pd.cut(
                df['Edad en años'], 
                bins=[-1, 1, 5, 15, 55, 65, float('inf')], 
                labels=["-1", "1-4", "5-14", "15-54", "55-64", "65+"])

            # Calcular el promedio de estancia por grupo etario
            if 'Grupo Etario' in df.columns and 'Estancia del Episodio' in df.columns:
                promedio_estancia = df.groupby('Grupo Etario', observed=False)['Estancia del Episodio'].mean().reset_index()
                resultados['promedio_estancia_por_grupo_etario'] = promedio_estancia
                if update_progress:
                    update_progress()
        # Conteo de egresos por mes (usando "Fecha egreso completa")
        if 'Fecha de egreso completa' in df.columns:
            df = df.copy()
            df.loc[:, 'Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
            df = df.dropna(subset=['Fecha de egreso completa'])
            df.loc[:, 'Mes de Egreso'] = df['Fecha de egreso completa'].dt.to_period('M')
            conteo_egresos = df.groupby('Mes de Egreso', observed=False).size().reset_index(name='Egresos')
            resultados['egresos_por_mes'] = conteo_egresos
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

        # Heatmap diagnósticos por grupo etario
        if 'Edad en años' in df.columns and 'Diag 01 Principal (cod+des)' in df.columns:
            df.loc[:, 'Grupo Etario'] = pd.cut(
                df['Edad en años'],
                bins=[-1, 1, 5, 15, 55, 65, float('inf')],
                labels=["-1", "1-4", "5-14", "15-54", "55-64", "65+"])
            heatmap_data = df.pivot_table(index='Grupo Etario', columns='Diag 01 Principal (cod+des)', aggfunc='size', fill_value=0, observed=False)
            plt.figure(figsize=(14, 10))
            import seaborn as sns
            sns.heatmap(heatmap_data, annot=False, cmap="YlGnBu")
            plt.title('Heatmap de Diagnósticos por Grupo Etario')
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            resultados['heatmap_diagnosticos_etario.png'] = buffer.getvalue()
            plt.close()
            if update_progress:
                update_progress()
        # Línea comparativa de egresos mensuales por año
        if 'Fecha de egreso completa' in df.columns:
            df = df.copy()
            df.loc[:, 'Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
            df = df.dropna(subset=['Fecha de egreso completa'])
            df.loc[:, 'Año'] = df['Fecha de egreso completa'].dt.year
            df.loc[:, 'Mes'] = df['Fecha de egreso completa'].dt.month
            egresos = df.groupby(['Año', 'Mes']).size().unstack(level=0, fill_value=0)
            fig, ax = plt.subplots(figsize=(12, 6))
            egresos.plot(ax=ax)
            ax.set_title('Egresos Mensuales Comparativos por Año')
            ax.set_xlabel('Mes')
            ax.set_ylabel('Cantidad de Egresos')
            ax.legend(title='Año')
            ax.set_xticks(range(1, 13))
            ax.set_xticklabels([
                'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
            ])
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            resultados['linea_egresos_mensuales_comparativo.png'] = buf.getvalue()
            if update_progress:
                update_progress()
        # Línea comparativa de egresos mensuales por año (solo año más reciente y anterior, hasta el mes máximo)
        egresos = df_comp.groupby(['Mes', 'Año']).size().unstack(level=1, fill_value=0)
        fig, ax = plt.subplots(figsize=(12, 6))
        egresos.plot(ax=ax)

        nivel_ideal = 2000
        ax.axhline(y=nivel_ideal, color='r', linestyle='--', linewidth=2, label='Nivel Ideal')
        ax.set_title(f'Egresos Mensuales {max_anio-1} vs {max_anio})')
        ax.set_xlabel('Mes')
        ax.set_ylabel('Cantidad de Egresos')
        ax.legend(title='Año')
        ax.grid(True, linestyle='-.')
        ax.set_xticks(range(1, max_mes+1))
        ax.set_xticklabels([
            'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
            'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
        ][:max_mes])
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        resultados['linea_egresos_mensuales_comparativo.png'] = buf.getvalue()
        if update_progress:
            update_progress()
        # Barras promedio estancia por grupo etario
        if 'Edad en años' in df.columns and 'Estancia del Episodio' in df.columns:
            # Asignar grupos etarios usando pd.cut con los nuevos rangos
            df.loc[:, 'Grupo Etario'] = pd.cut(
                df['Edad en años'], 
                bins=[-1, 1, 5, 15, 55, 65, float('inf')], 
                labels=["-1", "1-4", "5-14", "15-54", "55-64", "65+"])

            # Calcular el promedio de estancia por grupo etario
            promedio_estancia = df.groupby('Grupo Etario', observed=False)['Estancia del Episodio'].mean()
            

            # Crear el gráfico de barras
            plt.figure(figsize=(8, 5))
            promedio_estancia.plot(kind='bar', color='skyblue')
            plt.title('Promedio de Estancia por Grupo Etario')
            plt.xlabel('Grupo Etario')
            plt.ylabel('Estancia Promedio')

            # Guardar el gráfico en un buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            resultados['barras_promedio_estancia.png'] = buffer.getvalue()
            plt.close()

            if update_progress:
                update_progress()
        return resultados

    def ejecutar_analisis(self, df: pd.DataFrame, update_progress=None):
        tablas = self.generar_tablas(df, update_progress)
        graficos = self.generar_graficos(df, update_progress)
        return {"tablas": tablas, "graficos": graficos}

    @staticmethod
    def get_total_steps():
        return 5
