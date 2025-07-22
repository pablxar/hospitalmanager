import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

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
        
        # Gráfico 1
        if 'Nivel de severidad (Descripción)' in df.columns:
            for year in sorted(df['Año'].unique()):
                df_year = df[df['Año'] == year]
                if df_year.empty:
                    continue
                # Gráfico de barras por nivel de severidad
                fig, ax = plt.subplots()
                df_year['Nivel de severidad (Descripción)'].value_counts().plot(kind='barh', colormap='RdYlGn', ax=ax)
                ax.set_title('Distribución por Nivel de severidad')
                ax.set_ylabel('Nivel de severidad')
                ax.set_xlabel('Cantidad de Egresos')
                
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                
                plt.close(fig)
                buf.seek(0)
                resultados[f'barras_nivel_severidad_{year}.png'] = buf.getvalue()
            if update_progress:
                update_progress()
                
        # Gráfico 2: Promedio de estancia por nivel de severidad
        if 'Nivel de severidad (Descripción)' in df.columns and 'Estancia del Episodio' in df.columns:
            for year in sorted(df['Año'].unique()):
                df_year = df[df['Año'] == year]
                if df_year.empty:
                    continue
                
                # Calcular promedio de estancia por nivel de severidad
                promedio_estancia = df_year.groupby('Nivel de severidad (Descripción)')['Estancia del Episodio'].mean()
                
                fig, ax = plt.subplots()
                promedio_estancia.plot(kind='barh', colormap='RdYlGn', ax=ax)
                ax.set_title(f'Promedio de Estancia por Nivel de severidad - {year}')
                ax.set_ylabel('Nivel de severidad')
                ax.set_xlabel('Días de Estancia Promedio')
                
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                plt.close(fig)
                buf.seek(0)
                resultados[f'promedio_estancia_severidad_{year}.png'] = buf.getvalue()
            if update_progress:
                update_progress()
        
        
        
        # Gráfico 3: Evolución mensual de egresos por tipo de actividad
        df['Fecha'] = pd.to_datetime(df['Fecha de egreso completa'])
        df['Mes'] = df['Fecha'].dt.month
        df['Año'] = df['Fecha'].dt.year
        
        # Filtrar solo años completos
        df = df[df['Año'].isin([2024, 2025])]
        
        # Agrupar por tipo de actividad, año y mes
        evolucion = df.groupby(['Tipo Actividad', 'Año', 'Mes']).size().unstack([0,1]).fillna(0)
        
        # Configurar gráfico
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # Colores y estilos
        colores = {
            'Hospitalización': '#ff7f0e',
            'Cirugía Mayor Ambulatoria (CMA)': '#1f77b4'
        }
        
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        
        # Graficar para cada año
        for año in [2024, 2025]:
            for tipo in ['Hospitalización', 'Cirugía Mayor Ambulatoria (CMA)']:
                if (tipo, año) in evolucion.columns:
                    ax.plot(meses[:len(evolucion)], evolucion[(tipo, año)], 
                        marker='o', label=f'{tipo} {año}', 
                        color=colores[tipo], 
                        linestyle='--' if año == 2024 else '-')
        
        # Configuración
        ax.set_title('Evolución Mensual de Egresos por Tipo de Actividad (2024 vs 2025)', fontsize=16, fontweight='semibold', pad=20)
        ax.set_xlabel('Mes')
        ax.set_ylabel('Cantidad de Egresos')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, axis='y', alpha=0.2)

        # Guardar
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        plt.close(fig)
        buf.seek(0)
        resultados['evolucion_tipo_actividad.png'] = buf.getvalue()
        if update_progress:
            update_progress()
            
        
        
        # Gráfico 4: Comparación de estancia promedio por tipo de actividad
        stats = df.groupby(['Tipo Actividad', 'Año egreso'])['Estancia del Episodio'].agg(['mean', 'median', 'count'])

        # Configuración de estilo profesional
        try:
            plt.style.use('seaborn-v0_8')  # Intenta con el nuevo nombre del estilo
        except:
            plt.style.use('ggplot')  # Fallback a otro estilo profesional

        fig, ax = plt.subplots(figsize=(12, 7))

        # Paleta de colores profesional (ahora definida independientemente del estilo)
        colors = ['#1f77b4', '#ff7f0e']  # Azul corporativo y naranja complementario

        # Barras para media con estilo mejorado
        stats['mean'].unstack().T.plot(kind='bar', ax=ax, color=colors, width=0.8, 
                                    edgecolor='white', linewidth=0.5)

        # Configuración del gráfico
        ax.set_title('Estancia Promedio por Tipo de Actividad\nPeriodo 2024-2025', 
                    fontsize=16, pad=20, fontweight='semibold')
        ax.set_ylabel('Días de Estancia Promedio', fontsize=12, labelpad=10)
        ax.set_xlabel('Año de Egreso', fontsize=12, labelpad=10)
        ax.tick_params(axis='both', which='major', labelsize=11)

        # Personalización de la leyenda
        ax.legend(title='Tipo de Actividad', title_fontsize=12, 
                fontsize=11, framealpha=1, edgecolor='none')

        # Grid y ejes
        ax.grid(True, axis='y', linestyle='--', alpha=0.2)
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        for spine in ['left', 'bottom']:
            ax.spines[spine].set_alpha(0.3)

        # Añadir valores con formato profesional
        for p in ax.patches:
            height = p.get_height()
            ax.text(p.get_x() + p.get_width()/2., 
                    height + 0.05, 
                    f'{height:.1f} días', 
                    ha='center', va='bottom',
                    fontsize=10,
                    color='black',
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', 
                            facecolor='white', 
                            edgecolor='none', 
                            alpha=0.8))

        # Ajustar márgenes
        plt.tight_layout()
        plt.subplots_adjust(top=0.88)

        # Guardar con calidad profesional
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        resultados['estancia_comparativa.png'] = buf.getvalue()

        if update_progress:
            update_progress()


        # Gráfico 5: Distribución de niveles de severidad por actividad
        for year in sorted(df['Año'].unique()):
            df_year = df[df['Año'] == year]
            if df_year.empty:
                continue

            # Calcular distribución de severidad por actividad
            distrib_severidad = df_year.groupby(['Tipo Actividad', 'Nivel de severidad (Descripción)']).size().unstack(fill_value=0)

            # Normalizar para obtener porcentajes
            distrib_severidad_pct = distrib_severidad.div(distrib_severidad.sum(axis=1), axis=0) * 100

            # Configuración del gráfico
            fig, ax = plt.subplots(figsize=(12, 6))

            # Colores y estilo
            distrib_severidad_pct.plot(kind='barh', stacked=True, 
                                colormap='RdYlGn', 
                                ax=ax, width=0.7)

            # Configuración
            ax.set_title(f'Distribución de Niveles de Severidad por Tipo de Actividad - {year}', fontsize=16, fontweight='bold')
            ax.set_xlabel('Porcentaje (%)')
            ax.legend(title='Nivel de Severidad', bbox_to_anchor=(1.05, 1))
            ax.grid(True, axis='x', alpha=0.3)

            # Añadir etiquetas
            for i, (idx, row) in enumerate(distrib_severidad_pct.iterrows()):
                acumulado = 0
                for val in row:
                    if val > 5:  # Mostrar solo porcentajes mayores al 5%
                        ax.text(acumulado + val / 2, i, 
                                f'{val:.1f}%', 
                                va='center', ha='center',
                                color='black', fontsize=10, fontweight='bold')
                    acumulado += val

            # Ajustar layout
            plt.tight_layout()
            plt.subplots_adjust(top=0.88)

            # Guardar con calidad profesional
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            resultados[f'distribucion_severidad_{year}.png'] = buf.getvalue()
        if update_progress:
            update_progress()

       # Gráfico 6: Distribución de egresos por hospital y tipo de actividad
        if 'Hospital (Descripción)' not in df.columns or 'Tipo Actividad' not in df.columns:
            print("⚠️ Columnas necesarias no encontradas.")
            return resultados
        
        # Definir mapeo de hospitales (debe estar definido previamente)
        mapeo_hospitales = {
            'Hospital Carlos Van Buren (Valparaíso)': 'HCVB',
            'Hospital Claudio Vicuña ( San Antonio)': 'HCV',
            'Hospital Dr. Eduardo Pereira Ramírez (Valparaíso)': 'HEP'
        }
        
        # Crear copia explícita del DataFrame para evitar el warning
        df = df.copy()
        
        # Aplicar el mapeo de hospitales al DataFrame completo (más eficiente)
        df['Hospital'] = df['Hospital (Descripción)'].map(mapeo_hospitales).fillna(df['Hospital (Descripción)'])
        
        # Filtrar por año y generar gráficos
        for year in sorted(df['Año'].unique()):
            # Filtrar por año (esto crea una vista, pero no modificaremos esta vista)
            df_year = df[df['Año'] == year]
            
            # Calcular distribución
            distribucion_year = df_year.groupby(['Hospital', 'Tipo Actividad']).size().unstack(fill_value=0)
            
            # Ordenar por el total de egresos
            distribucion_year['Total'] = distribucion_year.sum(axis=1)
            distribucion_year = distribucion_year.sort_values('Total', ascending=False).drop('Total', axis=1)
            
            if distribucion_year.empty:
                continue
                
            # Configuración del gráfico mejorado
            fig, ax = plt.subplots(figsize=(12, 7))
            
            # Colores y estilo
            colores = {
                'Hospitalización': "#ff7f0e",
                'Cirugía Mayor Ambulatoria (CMA)': "#1f77b4"
            }
            
            # Graficar
            bottom = None
            for actividad in distribucion_year.columns:
                ax.bar(distribucion_year.index, distribucion_year[actividad], 
                    bottom=bottom,
                    color=colores.get(actividad, '#777777'),
                    label=actividad,
                    edgecolor='white',
                    linewidth=1,
                    width=0.7)
                
                bottom = distribucion_year[actividad] if bottom is None else bottom + distribucion_year[actividad]
            
            # Configuración visual
            ax.set_title(f'Distribución de Actividades por Hospital - {year}\n', 
                        fontsize=14, fontweight='bold')
            ax.set_ylabel('Cantidad de Egresos', labelpad=10)
            ax.set_xlabel('Hospital', labelpad=10)
            
            # Rotar etiquetas X si son largas
            ax.tick_params(axis='x', rotation=45 if any(len(x) > 10 for x in distribucion_year.index) else 0)
            
            # Leyenda
            ax.legend(title='Tipo de Actividad', title_fontsize=12, 
                    fontsize=11, framealpha=1, edgecolor='none', loc='upper right')
            
            # Grid
            ax.grid(True, axis='y', alpha=0.2, linestyle='--')
            
            # Añadir etiquetas de valor y porcentaje
            totals = distribucion_year.sum(axis=1)
            for i, hospital in enumerate(distribucion_year.index):
                acumulado = 0
                for actividad in distribucion_year.columns:
                    valor = distribucion_year.loc[hospital, actividad]
                    if valor > 0:
                        porcentaje = (valor / totals.loc[hospital]) * 100
                        y_pos = acumulado + (valor / 2)
                        
                        # Determinar si el segmento es demasiado pequeño para texto interno
                        if valor < totals.loc[hospital] * 0.08:  # Umbral del 8% del total
                            # Mostrar texto fuera de la barra (a la derecha)
                            ax.text(i + 0.3, y_pos,  # Ajustar posición horizontal
                                f'{valor}\n({porcentaje:.1f}%)',
                                ha='left', va='center',
                                color='black',  # Color fijo para mejor legibilidad
                                fontsize=9,
                                fontweight='bold',
                                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1))
                        else:
                            # Mostrar texto dentro de la barra
                            text_color = 'black' if valor > totals.loc[hospital] * 0.2 else 'black'
                                    
                            ax.text(i, y_pos, 
                                f'{valor}\n({porcentaje:.1f}%)',
                                ha='center', va='center',
                                color=text_color,
                                fontsize=9,
                                fontweight='bold')
                        
                        acumulado += valor
            
            plt.tight_layout()
            
            # Guardar gráfico
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
            plt.close(fig)
            buf.seek(0)
            
            resultados[f'distribucion_hospitales_{year}.png'] = buf.getvalue()
            
            if update_progress:
                update_progress()
            
        # Gráfico 7: Egresos por tipo de actividad y hospital
        df_egresos = df.groupby(['Hospital', 'Año egreso', 'Tipo Actividad']).size().unstack()

        # Colores profesionales
        colors = ['#1f77b4', '#ff7f0e']  # CMA (azul), Hospitalización (naranja)
        
        # Generar un gráfico por año
        años = df['Año egreso'].unique()
        for año in sorted(años):
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Filtrar datos para el año actual
            datos_año = df_egresos.xs(año, level='Año egreso').fillna(0)
            
            # Ordenar hospitales por cantidad total de egresos
            datos_año = datos_año.loc[datos_año.sum(axis=1).sort_values(ascending=False).index]
            
            # Preparar posiciones para barras agrupadas
            n_hospitales = len(datos_año)
            index = np.arange(n_hospitales)
            bar_width = 0.35
            
            # Graficar barras agrupadas
            bar1 = ax.bar(index - bar_width/2, datos_año['Cirugía Mayor Ambulatoria (CMA)'], 
                        bar_width, color=colors[0], label='Cirugía Mayor Ambulatoria (CMA)', edgecolor='white', linewidth=0.5)
            
            bar2 = ax.bar(index + bar_width/2, datos_año['Hospitalización'], 
                        bar_width, color=colors[1], label='Hospitalización', edgecolor='white', linewidth=0.5)
            
            # Configuración del gráfico
            ax.set_title(f'Egresos por Tipo de Actividad - Año {año}\nDistribución por Hospital', 
                        fontsize=16, pad=20, fontweight='semibold')
            ax.set_ylabel('Cantidad de Egresos', fontsize=12, labelpad=10)
            ax.set_xlabel('Hospital', fontsize=12, labelpad=10)
            ax.set_xticks(index)
            ax.set_xticklabels(datos_año.index, ha='right', fontsize=10)
            ax.tick_params(axis='y', labelsize=11)
            
            # Leyenda
            ax.legend(title='Tipo de Actividad', title_fontsize=12, 
                    fontsize=11, framealpha=1, edgecolor='none', loc='upper right')
            
            # Grid y ejes
            ax.grid(True, axis='y', linestyle='--', alpha=0.2)
            for spine in ['top', 'right']:
                ax.spines[spine].set_visible(False)
            for spine in ['left', 'bottom']:
                ax.spines[spine].set_alpha(0.3)
            
            # Añadir etiquetas de valor
            for bars in [bar1, bar2]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., 
                                height + 0.5, 
                                f'{int(height)}', 
                                ha='center', va='bottom',
                                fontsize=10,
                                color='black',
                                fontweight='bold')
            
            # Ajustar layout
            plt.tight_layout()
            plt.subplots_adjust(top=0.9, right=0.85, bottom=0.2)
            
            # Guardar en buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            resultados[f'egresos_{año}.png'] = buf.getvalue()
            
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
        return 15  # Total de pasos para el análisis económico
