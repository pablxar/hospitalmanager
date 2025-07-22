import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FuncFormatter
import numpy as np

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

        # Gráfico 1: Egresos Mensuales Comparativos por Año
        if 'Fecha de egreso completa' in df.columns:
            df = df.copy()
            df.loc[:, 'Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
            df = df.dropna(subset=['Fecha de egreso completa'])
            df.loc[:, 'Año'] = df['Fecha de egreso completa'].dt.year
            df.loc[:, 'Mes'] = df['Fecha de egreso completa'].dt.month
            egresos = df.groupby(['Año', 'Mes']).size().unstack(level=0, fill_value=0)

            # Calcular la variación porcentual mes a mes
            variacion_porcentual = egresos.pct_change().fillna(0) * 100

            fig, ax = plt.subplots(figsize=(12, 6))
            egresos.plot(ax=ax)

            # Añadir marcas para la variación porcentual
            for year, color in zip(egresos.columns, ['#4CAF50', '#2196F3']):
                if year in variacion_porcentual.columns:
                    ax.scatter(egresos.index, egresos[year] + variacion_porcentual[year], color=color, alpha=0.6, label=f'Variación % {year}')

            ax.set_title('Egresos Mensuales Comparativos por Año con Variación Porcentual')
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
            resultados['linea_egresos_mensuales_comparativo2.png'] = buf.getvalue()
            if update_progress:
                update_progress()

        # Gráfico 2: Egresos Mensuales Comparativos con Variación Porcentual
        egresos = df_comp.groupby(['Mes', 'Año']).size().unstack(level=1, fill_value=0)

        # Calcular la variación porcentual mes a mes
        variacion_porcentual = egresos.pct_change().fillna(0) * 100

        fig, ax = plt.subplots(figsize=(12, 6))
        egresos.plot(ax=ax)

        nivel_ideal = 2000
        ax.axhline(y=nivel_ideal, color='r', linestyle='--', linewidth=2, label='Nivel Ideal')

        # Añadir marcas para la variación porcentual
        for year, color in zip(egresos.columns, ['#4CAF50', '#2196F3']):
            if year in variacion_porcentual.columns:
                ax.scatter(egresos.index, egresos[year] + variacion_porcentual[year], color=color, alpha=0.6, label=f'Variación % {year}')

        ax.set_title(f'Egresos Mensuales {max_anio-1} vs {max_anio} con Variación Porcentual')
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
        resultados['linea_egresos_mensuales_comparativo1.png'] = buf.getvalue()
        if update_progress:
            update_progress()
        
        # Gráfico 3: Promedio de Estancia por Grupo Etario
        if 'Edad en años' in df.columns and 'Estancia del Episodio' in df.columns:
            try:
                # Configuración de estilo profesional
                plt.style.use('seaborn-v0_8')
            except:
                plt.style.use('ggplot')
            
            # Definir rangos y etiquetas más descriptivas
            bins = [0, 1, 5, 15, 55, 65, 120]
            labels = ["<1 año", "1-4 años", "5-14 años", "15-54 años", "55-64 años", "65+ años"]
            
            # Crear copia para evitar SettingWithCopyWarning
            df_temp = df.copy()
            df_temp['Grupo Etario'] = pd.cut(
                df_temp['Edad en años'],
                bins=bins,
                labels=labels,
                right=False
            )
            
            # Calcular estadísticas
            stats = df_temp.groupby('Grupo Etario', observed=True)['Estancia del Episodio'].agg(['mean', 'median', 'count'])
            
            # Configurar figura
            fig, ax = plt.subplots(figsize=(12, 7))
            
            # Color corporativo
            bar_color = '#1f77b4'  # Azul corporativo
            
            # Graficar barras
            bars = ax.bar(stats.index, stats['mean'], 
                        color=bar_color, 
                        width=0.7,
                        edgecolor='white',
                        linewidth=1)
            
            # Configuración del gráfico
            ax.set_title('Promedio de Estancia Hospitalaria por Grupo Etario\n', 
                        fontsize=14, pad=20, fontweight='semibold')
            ax.set_ylabel('Días de Estancia Promedio', fontsize=12, labelpad=10)
            ax.set_xlabel('Grupo Etario', fontsize=12, labelpad=10)
            ax.tick_params(axis='x', rotation=45, labelsize=11)
            ax.tick_params(axis='y', labelsize=11)
            
            # Grid y ejes
            ax.grid(True, axis='y', linestyle='--', alpha=0.4)
            for spine in ['top', 'right']:
                ax.spines[spine].set_visible(False)
            for spine in ['left', 'bottom']:
                ax.spines[spine].set_alpha(0.3)
            
            # Añadir etiquetas de valor
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., 
                        height + 0.1, 
                        f'{height:.1f} días', 
                        ha='center', va='bottom',
                        fontsize=10,
                        color='black',
                        bbox=dict(boxstyle='round,pad=0.2', 
                                facecolor='white', 
                                edgecolor='none', 
                                alpha=0.8))
            
            # Añadir información de muestra en la esquina
            total_pacientes = stats['count'].sum()
            ax.text(0.95, 0.95, 
                    f'Total pacientes: {total_pacientes:,}\nPeriodo: {df["Año"].min()}-{df["Año"].max()}', 
                    transform=ax.transAxes,
                    ha='right', va='top',
                    bbox=dict(facecolor='white', alpha=0.8),
                    fontsize=10)
            
            # Ajustar layout
            plt.tight_layout()
            
            # Guardar con calidad profesional
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            resultados['barras_promedio_estancia.png'] = buf.getvalue()
            
            if update_progress:
                update_progress()
        
        # Gráfico 4: Comparación Anual de Egresos por Mes
        if 'Tipo Actividad' in df.columns and 'Mes' in df.columns and 'Año' in df.columns:
            fig, ax = plt.subplots(figsize=(12, 8))

            # Filtrar datos para los años más recientes
            df_filtrado = df[df['Año'].isin([max_anio - 1, max_anio])]

            # Crear tabla pivotante para contar los egresos por tipo de actividad y mes
            pivot = df_filtrado.pivot_table(index='Mes', columns=['Tipo Actividad', 'Año'], values='Egresos', aggfunc='sum', fill_value=0)

            # Calcular la variación porcentual mes a mes
            variacion_porcentual = pivot.pct_change().fillna(0) * 100

            # Dibujar líneas para cada tipo de actividad y año
            for tipo_actividad in pivot.columns.levels[0]:
                for year, color in zip([max_anio - 1, max_anio], ['#4CAF50', '#2196F3']):
                    if (tipo_actividad, year) in pivot.columns:
                        ax.plot(pivot.index, pivot[(tipo_actividad, year)], marker='o', linestyle='-', color=color, label=f'{tipo_actividad} ({year})')

                        # Añadir marcas para la variación porcentual
                        if (tipo_actividad, year) in variacion_porcentual.columns:
                            ax.scatter(pivot.index, pivot[(tipo_actividad, year)] + variacion_porcentual[(tipo_actividad, year)], color=color, alpha=0.6, label=f'Variación % {tipo_actividad} ({year})')

            # Configurar etiquetas y título
            ax.set_title('Evolución Mensual por Tipo de Actividad con Variación Porcentual')
            ax.set_xlabel('Mes')
            ax.set_ylabel('Cantidad de Egresos')
            ax.set_xticks(range(1, max_mes + 1))
            ax.set_xticklabels([
                'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
            ][:max_mes])
            ax.legend(title='Indicadores', loc='upper left', bbox_to_anchor=(1, 1))

            # Ajustar diseño
            plt.tight_layout()

            # Guardar gráfico en buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)

            resultados['lineas_comparativas_tipo_actividad.png'] = buf.getvalue()
            if update_progress:
                update_progress()
        
        if 'Fecha de egreso completa' not in df.columns:
            print("⚠️ Columna 'Fecha de egreso completa' no encontrada en el DataFrame.")
            return resultados
        
        # Gráfico 5: Comparación Anual de Egresos por Mes
        df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
        df = df.dropna(subset=['Fecha de egreso completa'])
        df['Año'] = df['Fecha de egreso completa'].dt.year
        df['Mes'] = df['Fecha de egreso completa'].dt.month
        
        if df.empty:
            print("⚠️ DataFrame vacío después del procesamiento de fechas.")
            return resultados
        
        # Filtrar solo los años de interés (2024 y 2025)
        df = df[df['Año'].isin([2024, 2025])].copy()
        
        # Obtener los años presentes
        años = sorted(df['Año'].unique())
        if len(años) < 2:
            print(f"⚠️ Solo hay datos para un año ({años[0]}), no se puede hacer comparación.")
            return resultados
        
        min_año, max_año = años[0], años[1]
        
        # Ordenar meses y nombres abreviados
        meses_orden = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        
        # Obtener meses presentes en los datos
        meses_presentes = sorted(df['Mes'].unique())
        meses_mostrar = [meses_orden[m-1] for m in meses_presentes if 1 <= m <= 12]
        
        fig = plt.figure(figsize=(12, 6))  # Altura reducida
        ax = plt.gca()  # Usamos un solo eje

        # Colores y datos (igual que antes)
        colores = {min_año: COLOR_2024, max_año: COLOR_2025}
        bar_width = 0.35
        indice = np.arange(len(meses_mostrar))
        
        for i, año in enumerate([min_año, max_año]):
            egresos = [df[(df['Año'] == año) & (df['Mes'] == m)].shape[0] 
                    for m in meses_presentes]
            ax.bar(indice + (i * bar_width), egresos, bar_width,
                color=colores[año], label=f'Egresos {año}',
                edgecolor='white', linewidth=1)

        # Título y leyenda integrados
        titulo = f'Comparación de Egresos ({min_año} vs {max_año})'
        plt.title(titulo, fontsize=14, fontweight='semibold', y=1.08)  # y=1.08 acerca el título

        # Leyenda justo debajo del título
        leg = ax.legend(
            loc='upper center', 
            bbox_to_anchor=(0.5, 1.05),  # Posición ajustada
            ncol=2, 
            frameon=False,
            borderaxespad=0.1  # Reducir espacio adicional
        )
        
        # Configuración de ejes (igual que antes)
        ax.set_xticks(indice + bar_width/2)
        ax.set_xticklabels(meses_mostrar)
        ax.set_xlabel('Mes', labelpad=10)
        max_egresos = df.groupby(['Año', 'Mes']).size().max()
        ax.set_ylim(0, max_egresos * 1.15)
        ax.set_ylabel('Cantidad de Egresos', labelpad=10)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(True, axis='y', alpha=0.3)
        
        # Etiquetas de valores
        for rect in ax.patches:
            height = rect.get_height()
            if height > 0:
                ax.text(rect.get_x() + rect.get_width()/2, height,
                        f'{int(height):,}', 
                        ha='center', va='bottom',
                        fontsize=9, fontweight='semibold',
                        color='black')

        # Ajuste final compacto
        plt.tight_layout(pad=2.0)  # Padding general reducido
        
        # Guardar gráfico
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        plt.close(fig)
        buf.seek(0)
        
        resultados['comparacion_anual.png'] = buf.getvalue()
        
        if update_progress:
            update_progress()
            
        # Gráfico 6: Variación Interanual por Mes        
        if 'Fecha de egreso completa' not in df.columns:
            print("⚠️ Columna 'Fecha de egreso completa' no encontrada.")
            return resultados
        
        # Procesar fechas
        df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce').ffill()
        #Rellenar fechas faltantes hacia adelante
        df = df.dropna(subset=['Fecha de egreso completa'])
        df['Año'] = df['Fecha de egreso completa'].dt.year
        df['Mes'] = df['Fecha de egreso completa'].dt.month
        
        if df.empty:
            print("⚠️ No hay datos válidos después de procesar fechas.")
            return resultados
        
        # Filtrar años de interés (los dos más recientes)
        años = sorted(df['Año'].unique())
        if len(años) < 2:
            print("⚠️ Se necesitan datos de al menos 2 años para comparación.")
            return resultados
        
        min_año, max_año = años[-2], años[-1]  # Los dos años más recientes
        
        # Ordenar meses y nombres abreviados
        meses_orden = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        meses_presentes = sorted(df['Mes'].unique())
        meses_mostrar = [meses_orden[m-1] for m in meses_presentes if 1 <= m <= 12]
        
        # Calcular variación porcentual por mes
        variaciones = []
        for mes in meses_presentes:
            egresos_año1 = df[(df['Año'] == min_año) & (df['Mes'] == mes)].shape[0]
            egresos_año2 = df[(df['Año'] == max_año) & (df['Mes'] == mes)].shape[0]
            
            if egresos_año1 == 0:
                variaciones.append(0)  # Evitar división por cero
            else:
                variacion = ((egresos_año2 - egresos_año1) / egresos_año1) * 100
                variaciones.append(variacion)
        
        # Configurar figura y eje
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Colores condicionales para las barras
        colores = ['#4CAF50' if v >= 0 else '#F44336' for v in variaciones]  # Verde/Rojo
        
        # Crear barras
        barras = ax.bar(meses_mostrar, variaciones, color=colores, alpha=0.7, edgecolor='white')
        
        # Línea de referencia en 0%
        ax.axhline(0, color='#2196F3', linestyle='--', linewidth=1.5, alpha=0.7)
        
        # Configurar título y etiquetas
        ax.set_title(f'Variación Interanual ({min_año} vs {max_año})', fontsize=14, fontweight='semibold')
        ax.set_xlabel('Mes', labelpad=10)
        ax.set_ylabel('Variación (%)', labelpad=10)
        
        # Formatear eje Y para mostrar porcentajes
        ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:+.0f}%'))
        
        # Ajustar límites del eje Y con margen
        max_variacion = max(abs(v) for v in variaciones) if variaciones else 10
        ax.set_ylim(-max_variacion * 1.2, max_variacion * 1.2)
        
        # Grid solo en eje Y
        ax.grid(True, axis='y', linestyle=':', alpha=0.5)
        
        # Añadir etiquetas con flechas y colores
        for bar, variacion in zip(barras, variaciones):
            height = bar.get_height()
            va = 'bottom' if height >= 0 else 'top'
            color = '#4CAF50' if height >= 0 else '#F44336'
            flecha = '↑' if height >= 0 else '↓'
            
            ax.text(bar.get_x() + bar.get_width()/2, 
                    height + (0.5 if height >=0 else -0.5), 
                    f'{flecha} {height:+.2f}%',
                    ha='center', 
                    va=va, 
                    color=color,
                    fontweight='bold',
                    fontsize=10,
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar gráfico
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        plt.close(fig)
        buf.seek(0)
        
        resultados['variacion_interanual.png'] = buf.getvalue()
        
        if update_progress:
            update_progress()
        
        return resultados

    def ejecutar_analisis(self, df: pd.DataFrame, update_progress=None):
        tablas = self.generar_tablas(df, update_progress)
        graficos = self.generar_graficos(df, update_progress)
        return {"tablas": tablas, "graficos": graficos}

    @staticmethod
    def get_total_steps():
        return 8
