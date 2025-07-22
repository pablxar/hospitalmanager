import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FuncFormatter
from textwrap import wrap
import numpy as np

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
        
        # Gráfico 1: EEstancia promedio por "Tipo Ingreso (Descripción)"
        if 'Estancia del Episodio' in df.columns and 'Tipo Ingreso (Descripción)' in df.columns:
            try:
                # Configuración de estilo profesional
                plt.style.use('seaborn-v0_8')
            except:
                plt.style.use('ggplot')
            
            # Configurar figura con tamaño óptimo
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Procesar datos
            agrupado = df.groupby('Tipo Ingreso (Descripción)')['Estancia del Episodio'].sum().sort_values(ascending=True)  # Orden ascendente para mejor visualización
            
            # Paleta de colores corporativa mejorada
            colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']  # Colores profesionales
            
            # Crear gráfico de barras horizontales
            bars = ax.barh(agrupado.index, agrupado.values, 
                        color=colores[:len(agrupado)],
                        height=0.7,  # Grosor de barras
                        edgecolor='white',
                        linewidth=0.5)
            
            # Configuración del gráfico
            ax.set_title('Distribución Acumulada de Días de Estancia\npor Tipo de Ingreso', 
                        fontsize=14, fontweight='semibold')
            ax.set_xlabel('Total de Días de Estancia', fontsize=12, labelpad=10)
            ax.set_ylabel('Tipo de Ingreso', fontsize=12, labelpad=10)
            ax.tick_params(axis='both', which='major', labelsize=11)
            
            # Grid y ejes
            ax.grid(True, axis='x', linestyle='--', alpha=0.4)
            for spine in ['top', 'right']:
                ax.spines[spine].set_visible(False)
            for spine in ['left', 'bottom']:
                ax.spines[spine].set_alpha(0.3)
            
            # Añadir etiquetas de valor con formato
            for bar in bars:
                width = bar.get_width()
                ax.text(width + max(agrupado.values)*0.01,  # Posición a la derecha de la barra
                        bar.get_y() + bar.get_height()/2,
                        f'{width:,.0f} días',  # Formato con separadores de miles
                        va='center',
                        fontsize=10,
                        color='black',
                        bbox=dict(boxstyle='round,pad=0.2', 
                                facecolor='white', 
                                edgecolor='none', 
                                alpha=0.8))
            
            # Añadir información contextual
            total_estancia = agrupado.sum()
            ax.text(0.95, 0.95, 
                f'Total días de estancia: {total_estancia:,.0f}\nPeriodo analizado: {df["Año"].min()}-{df["Año"].max()}', 
                transform=ax.transAxes,
                ha='right', va='top',
                bbox=dict(facecolor='white', alpha=0.8),
                fontsize=10)
            
            # Ajustar márgenes y layout
            plt.tight_layout()
            plt.subplots_adjust(left=0.2)  # Más espacio para etiquetas Y
            
            # Guardar con calidad profesional
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            
            resultados['barras_estancia_por_tipo_ingreso.png'] = buf.getvalue()
            
            if update_progress:
                update_progress()
        
        # Gráfico 2: Evolución mensual de egresos
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
        
        # Gráfico 3: Comparativo de Egresos Mensuales con Nivel de Intervención Quirúrgica
        if 'Egresos' in df.columns and '(S/N) Egreso Quirúrgico' in df.columns:
            try:
                # Configuración de estilo profesional
                plt.style.use('seaborn-v0_8')
            except:
                plt.style.use('ggplot')
            
            # Configuración de colores corporativos
            COLOR_EGRESOS = "#1f77b4"  # Azul corporativo
            COLOR_QUIRURGICOS = "#ff7f0e"  # Naranja corporativo
            COLOR_VARIACION = "#d62728"  # Rojo para variación
            
            # Crear figura con tamaño óptimo
            fig, ax1 = plt.subplots(figsize=(14, 7))
            
            # Procesamiento de datos mejorado
            pivot = df_comp.pivot_table(
                index='Mes', 
                columns='Tipo Actividad', 
                values='Egresos', 
                aggfunc='count', 
                fill_value=0
            )
            
            # Calcular variación porcentual con rolling mean para suavizar
            variacion = pivot.pct_change().rolling(2).mean().fillna(0) * 100
            
            # Barras para egresos generales (Hospitalización)
            bars = ax1.bar(
                pivot.index, 
                pivot['Hospitalización'], 
                width=0.7,
                color=COLOR_EGRESOS, 
                alpha=0.8,
                edgecolor='white',
                linewidth=1,
                label='Egresos Generales'
            )
            
            # Añadir etiquetas de valor en las barras
            for bar in bars:
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width()/2., 
                    height + 0.5, 
                    f'{int(height)}',
                    ha='center', 
                    va='bottom',
                    fontsize=10,
                    color=COLOR_EGRESOS
                )
            
            # Configuración del primer eje
            ax1.set_title('Comparativo Mensual de Egresos Hospitalarios\nvs. Intervenciones Quirúrgicas', 
                        fontsize=16, pad=20, fontweight='semibold')
            ax1.set_xlabel('Mes', fontsize=12, labelpad=10)
            ax1.set_ylabel('Cantidad de Egresos', fontsize=12, labelpad=10, color=COLOR_EGRESOS)
            ax1.set_xticks(range(1, 13))
            ax1.set_xticklabels(['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
                            fontsize=11)
            ax1.tick_params(axis='y', labelcolor=COLOR_EGRESOS)
            
            # Segundo eje para variación porcentual
            ax2 = ax1.twinx()
            line = ax2.plot(
                variacion.index, 
                variacion['Hospitalización'], 
                marker='o', 
                markersize=8,
                linestyle='-', 
                linewidth=2,
                color=COLOR_VARIACION, 
                label='Variación % Mensual'
            )
            
            # Configuración del segundo eje
            ax2.set_ylabel('Variación Porcentual (%)', fontsize=12, labelpad=10, color=COLOR_VARIACION)
            ax2.tick_params(axis='y', labelcolor=COLOR_VARIACION)
            ax2.grid(False)
            
            # Línea horizontal en y=0 para referencia
            ax2.axhline(0, color='gray', linestyle='--', alpha=0.5)
            
            # Leyenda unificada
            lines = [bars, line[0]]
            labels = [l.get_label() for l in lines]
            ax1.legend(lines, labels, 
                    loc='upper left',
                    fontsize=11,
                    framealpha=1,
                    edgecolor='none')
            
            # Grid y estilo de ejes
            ax1.grid(True, axis='y', linestyle='--', alpha=0.3)
            for spine in ['top', 'right', 'left', 'bottom']:
                ax1.spines[spine].set_alpha(0.3)
            
            # Añadir información contextual
            total_egresos = pivot['Hospitalización'].sum()
            ax1.text(
                0.95, 0.95, 
                f'Total egresos: {total_egresos:,}\nAño: {df["Año"].max()}', 
                transform=ax1.transAxes,
                ha='right', 
                va='top',
                bbox=dict(facecolor='white', alpha=0.8),
                fontsize=10
            )
            
            # Ajustar layout
            plt.tight_layout()
            
            # Guardar con calidad profesional
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            
            resultados['grafico_egresos_comparativo_mejorado.png'] = buf.getvalue()
            
            if update_progress:
                update_progress()
        
        # Gráfico 4: Comparativo de Estancia del Episodio por Tipo de Ingreso (2024 vs 2025)
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
        
        
        # Gráfico 5: Comparativo de Estancia Promedio por Hospital (2024 vs 2025)
        columnas_requeridas = ['Hospital (Descripción)', 'Fecha de egreso completa', 'Estancia del Episodio']
        if not all(col in df.columns for col in columnas_requeridas):
            print("⚠️ Columnas necesarias no encontradas en el DataFrame.")
            return resultados
        
        # Procesar fechas y filtrar años
        df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
        df = df.dropna(subset=['Fecha de egreso completa'])
        df['Año'] = df['Fecha de egreso completa'].dt.year
        df = df[df['Año'].isin([2024, 2025])].copy()
        
        if df.empty:
            print("⚠️ No hay datos válidos después de procesar fechas.")
            return resultados
        
        # Simplificar nombres de hospitales usando un mapeo
        mapeo_hospitales = {
            'Hospital Carlos Van Buren (Valparaíso)': 'HCVB',
            'Hospital Claudio Vicuña ( San Antonio)': 'HCV',
            'Hospital Dr. Eduardo Pereira Ramírez (Valparaíso)': 'HEP'
        }
        df['Hospital'] = df['Hospital (Descripción)'].map(mapeo_hospitales).fillna(df['Hospital (Descripción)'])
        
        # Calcular estancia promedio por hospital y año
        estancia_promedio = df.groupby(['Hospital', 'Año'])['Estancia del Episodio'].mean().unstack()
        
        # Ordenar hospitales por estancia promedio en 2025 (descendente)
        hospitales_ordenados = estancia_promedio[2025].sort_values(ascending=False).index
        
        # Configurar el gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Colores para cada año (consistentes con el TS)
        colores = {
            2024: COLOR_2024,  # Verde
            2025: COLOR_2025   # Azul
        }
        
        # Ancho de las barras
        bar_width = 0.35
        indice = np.arange(len(hospitales_ordenados))
        
        # Crear barras para cada año
        for i, año in enumerate([2024, 2025]):
            datos = estancia_promedio.loc[hospitales_ordenados, año].values
            ax.bar(indice + (i * bar_width), datos, bar_width,
                color=colores[año],
                label=f'Estancia Promedio {año}',
                edgecolor='white',
                linewidth=1)
        
        # Configuración del gráfico
        ax.set_title('Estancia Promedio por Hospital (Comparativo 2024-2025)', fontsize=14, fontweight='semibold')
        ax.set_xlabel('Hospital', labelpad=10)
        ax.set_ylabel('Días Promedio', labelpad=10)
        
        # Posiciones y etiquetas del eje X
        ax.set_xticks(indice + bar_width/2)
        ax.set_xticklabels(hospitales_ordenados, rotation=0, ha='center')
        
        # Ajustar límites del eje Y
        max_estancia = estancia_promedio.max().max()
        ax.set_ylim(0, max_estancia * 1.15)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Leyenda
        ax.legend(title='Año', loc='upper right')
        
        # Grid solo en el eje Y
        ax.grid(True, axis='y', alpha=0.3)
        
        # Añadir etiquetas a las barras
        for rect in ax.patches:
            height = rect.get_height()
            if height > 0:
                ax.text(rect.get_x() + rect.get_width() / 2, height,
                        f'{height:.1f} días', 
                        ha='center', va='bottom',
                        fontsize=10, fontweight='semibold')

        # Ajustar márgenes
        plt.tight_layout()
        
        # Guardar gráfico
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        plt.close(fig)
        buf.seek(0)
        
        resultados['comparacion_estancia.png'] = buf.getvalue()
        
        if update_progress:
            update_progress()
            
        # Gráfico 6: Top 10 Especialidades por Estancia Promedio (2024 vs 2025)
        columnas_requeridas = ['Especialidad (Descripción )', 'Fecha de egreso completa', 'Estancia del Episodio']
        if not all(col in df.columns for col in columnas_requeridas):
            print("⚠️ Columnas necesarias no encontradas en el DataFrame.")
            return resultados
        
        # Procesar fechas y filtrar años
        df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
        df = df.dropna(subset=['Fecha de egreso completa'])
        df['Año'] = df['Fecha de egreso completa'].dt.year
        df = df[df['Año'].isin([2024, 2025])].copy()
        
        if df.empty:
            print("⚠️ No hay datos válidos después de procesar fechas.")
            return resultados
        
        # Limpiar nombres de especialidades
        df['Especialidad'] = df['Especialidad (Descripción )'].str.strip()
        
        # Calcular estancia promedio por especialidad y año
        estancia_promedio = df.groupby(['Especialidad', 'Año'])['Estancia del Episodio'].mean().unstack()
        
        # Seleccionar top 10 especialidades con mayor estancia en 2025
        top_10 = estancia_promedio[2025].nlargest(10).index
        estancia_promedio = estancia_promedio.loc[top_10]
        
        # Configurar el gráfico horizontal
        fig, ax = plt.subplots(figsize=(12, 8))  # Más alto para mejor legibilidad
        
        # Colores para cada año
        colores = {
            2024: COLOR_2024,  # Azul
            2025: COLOR_2025   # Verde
        }
        
        # Ancho de las barras y posición
        bar_height = 0.35
        indice = np.arange(len(top_10))
        
        # Crear barras horizontales para cada año
        for i, año in enumerate([2024, 2025]):
            datos = estancia_promedio[año].values
            ax.barh(indice + (i * bar_height), datos, bar_height,
                color=colores[año],
                label=f'Estancia Promedio {año}',
                edgecolor='white',
                linewidth=1)
        
        # Configuración del gráfico
        ax.set_title('Top 10 Especialidades por Estancia Promedio (2024 vs 2025)', fontsize=14, fontweight='semibold')
        ax.set_xlabel('Días Promedio', labelpad=10)
        ax.set_ylabel('Especialidad Médica', labelpad=10)
        
        # Dividir nombres largos en múltiples líneas (máximo 3 palabras por línea)
        etiquetas = ['\n'.join(wrap(esp, width=25, max_lines=2)) for esp in top_10]
        
        # Posiciones y etiquetas del eje Y
        ax.set_yticks(indice + bar_height/2)
        ax.set_yticklabels(etiquetas, ha='right', va='center', fontsize=10)
        
        # Ajustar límites del eje X
        max_estancia = estancia_promedio.max().max()
        ax.set_xlim(0, max_estancia * 1.15)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Leyenda
        ax.legend(title='Año', loc='upper right')
        
        # Grid solo en el eje X
        ax.grid(True, axis='x', alpha=0.3)
        
        # Añadir etiquetas a las barras
        for rect in ax.patches:
            width = rect.get_width()
            if width > 0:
                ax.text(width + (max_estancia * 0.01), 
                    rect.get_y() + rect.get_height() / 2,
                    f'{width:.1f}d', 
                    ha='left', va='center',
                    fontsize=9,
                    fontweight='bold')
        
        # Ajustar márgenes
        plt.tight_layout()
        
        # Guardar gráfico
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
        plt.close(fig)
        buf.seek(0)
        
        resultados['estancia_especialidad.png'] = buf.getvalue()
        
        if update_progress:
            update_progress()
            
        # Gráfico 7: Top 10 Diagnósticos Principales más Frecuentes
        if 'Diag 01 Principal (cod+des)' not in df.columns:
            print("⚠️ Columna 'Diag 01 Principal (cod+des)' no encontrada.")
            return resultados
        
        # Contar frecuencia de diagnósticos
        conteo_diagnosticos = df['Diag 01 Principal (cod+des)'].value_counts().nlargest(10)
        
        if len(conteo_diagnosticos) == 0:
            print("⚠️ No hay datos de diagnósticos para mostrar.")
            return resultados
        
        # Configurar el gráfico horizontal con mayor altura
        fig, ax = plt.subplots(figsize=(12, 8))  # Aumenté la altura a 8 para mejor espacio
        
        # Color consistente con el estilo (azul)
        color_barras = "#57A0ED"
        
        # Dividir etiquetas largas en múltiples líneas (máximo 25 caracteres por línea)
        etiquetas = ['\n'.join(wrap(diagnostico, width=25, max_lines=2)) for diagnostico in conteo_diagnosticos.index]
        
        # Crear barras horizontales con las etiquetas ajustadas
        barras = ax.barh(etiquetas, conteo_diagnosticos.values, 
                        color=color_barras, alpha=0.8, edgecolor='white', height=0.7)  # Reduje height para más espacio
        
        # Configuración del gráfico
        ax.set_title('Top 10 Diagnósticos Principales más Frecuentes', fontsize=14, fontweight='semibold')
        ax.set_xlabel('Cantidad de Egresos', labelpad=10)
        ax.set_ylabel('Diagnóstico', labelpad=10)
        
        # Ajustar tamaño de fuente de las etiquetas Y
        ax.tick_params(axis='y', labelsize=10)
        
        # Añadir etiquetas de valor a las barras
        for bar in barras:
            width = bar.get_width()
            ax.text(width + (conteo_diagnosticos.max() * 0.01), 
                    bar.get_y() + bar.get_height()/2,
                    f'{int(width)}',
                    va='center',
                    fontsize=10,
                    fontweight='bold')
        
        # Grid solo en eje X
        ax.grid(True, axis='x', alpha=0.3)
        
        # Invertir orden para que el más frecuente quede arriba
        ax.invert_yaxis()
        
        # Ajustar márgenes para acomodar etiquetas multilínea
        plt.tight_layout(pad=3.0)
        plt.subplots_adjust(left=0.3)  # Ajustar margen izquierdo para etiquetas
        
        # Guardar gráfico
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
        plt.close(fig)
        buf.seek(0)
        
        resultados['top10_diagnosticos_mejorado.png'] = buf.getvalue()
        
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
        return 8
