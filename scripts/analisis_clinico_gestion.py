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
        # Gráfico de barras horizontales apiladas para distribución de estancia por tipo de ingreso
        if 'Estancia del Episodio' in df.columns and 'Tipo Ingreso (Descripción)' in df.columns:
            fig, ax = plt.subplots(figsize=(12, 8))

            # Agrupar datos por tipo de ingreso y calcular la suma de estancias
            agrupado = df.groupby('Tipo Ingreso (Descripción)')['Estancia del Episodio'].sum().sort_values(ascending=False)

            # Colores predefinidos para los tipos de ingreso
            colores = ['#FFEB3B', '#4CAF50', '#2196F3']

            # Crear gráfico de barras horizontales
            ax.barh(agrupado.index, agrupado.values, color=colores[:len(agrupado)])

            # Configurar etiquetas y título
            ax.set_title('Distribución de Estancia por Tipo de Ingreso')
            ax.set_xlabel('Total de Estancia del Episodio')
            ax.set_ylabel('Tipo de Ingreso')

            # Ajustar diseño
            plt.tight_layout()

            # Guardar gráfico en buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)

            resultados['barras_estancia_por_tipo_ingreso.png'] = buf.getvalue()
            if update_progress:
                update_progress()
        
        # Scatter Peso GRD vs Estancia del Episodio (en lugar de Valor a Pagar)
        if 'Peso GRD' in df.columns and 'Estancia del Episodio' in df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))

            # Obtener los tipos de ingreso únicos
            tipos_ingreso = df['Tipo Ingreso (Descripción)'].dropna().unique()
            colores = plt.cm.tab10.colors  # Usar una paleta de colores predefinida

            # Crear gráfico de dispersión para cada tipo de ingreso
            for tipo, color in zip(tipos_ingreso, colores):
                df_tipo = df[df['Tipo Ingreso (Descripción)'] == tipo]
                ax.scatter(df_tipo['Peso GRD'], df_tipo['Estancia del Episodio'], label=tipo, color=color, alpha=0.7)

            # Configurar etiquetas y título
            ax.set_title('Relación entre Peso GRD y Estancia del Episodio por Tipo de Ingreso')
            ax.set_xlabel('Peso GRD')
            ax.set_ylabel('Estancia del Episodio')
            ax.legend(title='Tipo de Ingreso')

            # Ajustar diseño
            plt.tight_layout()

            # Guardar gráfico en buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)

            resultados['scatter_peso_vs_estancia_tipo_ingreso.png'] = buf.getvalue()
            if update_progress:
                update_progress()
        
        # Gráfico comparativo de egresos mensuales con nivel de intervención quirúrgica
        if 'Egresos' in df.columns and '(S/N) Egreso Quirúrgico' in df.columns:
            
            # Colores definidos para las actividades
            COLOR_EGRESOS = "#2196F3"  # Azul para egresos generales
            COLOR_QUIRURGICOS = "#FF5722"  # Naranja para egresos quirúrgicos

            # Crear una tabla pivotante para contar los egresos (pacientes) por mes
            pivot = df_comp.pivot_table(index='Mes', columns='Tipo Actividad', values='Egresos', aggfunc='count', fill_value=0)

            # Calcular la variación porcentual de los egresos (frecuencia de pacientes)
            variacion_porcentual = pivot.pct_change().fillna(0) * 100

            fig, ax1 = plt.subplots(figsize=(10, 6))

            # Barras para 'Egresos' generales
            ax1.bar(pivot.index, pivot['Hospitalización'], label='Egresos Generales', color=COLOR_EGRESOS, alpha=0.6)

            # Añadir una segunda escala de eje para la línea de variación porcentual
            ax2 = ax1.twinx()
            ax2.plot(variacion_porcentual.index, variacion_porcentual['Hospitalización'], marker='o', linestyle='--', color=COLOR_QUIRURGICOS, label='Variación % Egresos Quirúrgicos')

            # Títulos y etiquetas
            ax1.set_title('Comparativo de Egresos Mensuales con Nivel de Intervención Quirúrgica')
            ax1.set_xlabel('Mes')
            ax1.set_ylabel('Cantidad de Egresos', color=COLOR_EGRESOS)
            ax1.set_xticks(range(1, len(pivot.index) + 1))
            ax1.set_xticklabels(['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'][:len(pivot.index)])
            ax1.tick_params(axis='y', labelcolor=COLOR_EGRESOS)

            ax2.set_ylabel('Variación %', color=COLOR_QUIRURGICOS)
            ax2.tick_params(axis='y', labelcolor=COLOR_QUIRURGICOS)

            # Añadir leyenda
            fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9), bbox_transform=ax1.transAxes)

            # Ajustar la disposición del gráfico
            plt.tight_layout()

            # Guardar el gráfico en un buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)

            # Guardar el gráfico como imagen en el diccionario de resultados
            resultados['grafico_egresos_comparativo_mejorado.png'] = buf.getvalue()
            if update_progress:
                update_progress()
        # Gráfico de dispersión comparativo para Peso GRD vs Estancia del Episodio por Tipo de Ingreso entre 2024 y 2025
        if 'Peso GRD' in df.columns and 'Estancia del Episodio' in df.columns and 'Tipo Ingreso (Descripción)' in df.columns:
            fig, ax = plt.subplots(figsize=(12, 8))

            # Filtrar datos para los años 2024 y 2025
            df_filtrado = df[df['Año'].isin([2024, 2025])]

            # Obtener los tipos de ingreso únicos
            tipos_ingreso = df_filtrado['Tipo Ingreso (Descripción)'].dropna().unique()
            colores = plt.cm.tab10.colors  # Usar una paleta de colores predefinida

            # Crear gráfico de dispersión para cada tipo de ingreso y año
            for tipo, color in zip(tipos_ingreso, colores):
                for year, marker in zip([2024, 2025], ['o', 's']):
                    df_tipo_year = df_filtrado[(df_filtrado['Tipo Ingreso (Descripción)'] == tipo) & (df_filtrado['Año'] == year)]
                    ax.scatter(df_tipo_year['Peso GRD'], df_tipo_year['Estancia del Episodio'], label=f'{tipo} ({year})', color=color, alpha=0.7, marker=marker)

            # Configurar etiquetas y título
            ax.set_title('Relación entre Peso GRD y Estancia del Episodio por Tipo de Ingreso (2024 vs 2025)')
            ax.set_xlabel('Peso GRD')
            ax.set_ylabel('Estancia del Episodio')
            ax.legend(title='Tipo de Ingreso y Año', loc='upper right', bbox_to_anchor=(1.3, 1))

            # Ajustar diseño
            plt.tight_layout()

            # Guardar gráfico en buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)

            resultados['scatter_peso_vs_estancia_comparativo.png'] = buf.getvalue()
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
        return 5
