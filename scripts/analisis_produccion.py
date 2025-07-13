import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

class AnalisisProduccion:
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
        if 'Motivo Egreso (Descripción)' in df.columns:
            conteo = df_filtrado.groupby(['Año', 'Mes', 'Motivo Egreso (Descripción)']).size().reset_index(name='Frecuencia')
            
            resultados['conteo_motivo_egreso_por_anio_mes'] = conteo
            conteo_total = df_filtrado['Motivo Egreso (Descripción)'].value_counts().reset_index()
            conteo_total.columns = ['Motivo Egreso', 'Frecuencia']
            resultados['conteo_motivo_egreso'] = conteo_total
            if update_progress:
                update_progress()
        if 'Tipo Ingreso (Descripción)' in df.columns:
            distribucion = df_filtrado.groupby(['Año', 'Mes', 'Tipo Ingreso (Descripción)']).size().reset_index(name='Frecuencia')
            resultados['distribucion_tipo_ingreso_por_anio_mes'] = distribucion
            distribucion_total = df_filtrado['Tipo Ingreso (Descripción)'].value_counts().reset_index()
            distribucion_total.columns = ['Tipo Ingreso', 'Frecuencia']
            resultados['distribucion_tipo_ingreso'] = distribucion_total
            if update_progress:
                update_progress()
        if 'Sexo (Desc)' in df.columns:
            distribucion_sexo = df_filtrado.groupby(['Año', 'Mes', 'Sexo (Desc)']).size().reset_index(name='Frecuencia')
            resultados['distribucion_sexo_por_anio_mes'] = distribucion_sexo
            distribucion_sexo_total = df_filtrado['Sexo (Desc)'].value_counts().reset_index()
            distribucion_sexo_total.columns = ['Sexo', 'Frecuencia']
            resultados['distribucion_sexo'] = distribucion_sexo_total
            if update_progress:
                update_progress()
        if 'Hospital (Descripción)' in df.columns:
            hospitales_cols = ['Hospital (Descripción)', 'Año', 'Mes']
            extra_cols = []
            if 'Peso GRD' in df.columns:
                extra_cols.append('Peso GRD')
            if 'Estancia' in df.columns:
                extra_cols.append('Estancia')
            if 'Edad en años' in df.columns:
                extra_cols.append('Edad en años')
            cols = hospitales_cols + extra_cols
            df_hosp = df_filtrado[df_filtrado['Año'].isin([2024, 2025])][cols].copy()
            if not df_hosp.empty:
                resumen = df_hosp.groupby(['Año', 'Hospital (Descripción)']).agg(
                    egresos=('Hospital (Descripción)', 'count'),
                    peso_grd_medio=('Peso GRD', 'mean') if 'Peso GRD' in df_hosp.columns else ('Hospital (Descripción)', 'size'),
                    estancia_media=('Estancia', 'mean') if 'Estancia' in df_hosp.columns else ('Hospital (Descripción)', 'size'),
                    edad_media=('Edad en años', 'mean') if 'Edad en años' in df_hosp.columns else ('Hospital (Descripción)', 'size')
                ).reset_index()
                
                # Separar los datos por año
                resumen_2024 = resumen[resumen['Año'] == 2024].drop('Año', axis=1)
                resumen_2025 = resumen[resumen['Año'] == 2025].drop('Año', axis=1)
                
                # Renombrar columnas para cada año
                resumen_2024 = resumen_2024.add_suffix('_2024').rename(columns={'Hospital (Descripción)_2024': 'Hospital'})
                resumen_2025 = resumen_2025.add_suffix('_2025').rename(columns={'Hospital (Descripción)_2025': 'Hospital'})
                
                # Hacer el merge por Hospital
                comparativo = pd.merge(resumen_2024, resumen_2025, on='Hospital', how='outer')
                
                # Llenar NaN with 0 para evitar errores en el cálculo
                for col in ['egresos_2024', 'egresos_2025']:
                    comparativo[col] = comparativo[col].fillna(0)
                
                # Calcular variación
                comparativo['variacion_egresos_%'] = ((comparativo['egresos_2025'] - comparativo['egresos_2024']) / comparativo['egresos_2024'].replace(0, 1)) * 100
                
                resultados['comparativo_hospital_2024_2025'] = comparativo
                resultados['hospitales_2024'] = resumen_2024
                resultados['hospitales_2025'] = resumen_2025
                if update_progress:
                    update_progress()
        return resultados

    def generar_graficos(self, df: pd.DataFrame, update_progress=None):
        resultados = {}
        
        # Definir colores constantes para los años
        COLOR_2024 = '#4CAF50'  # Verde
        COLOR_2025 = '#2196F3'  # Azul
        
        # Colores definidos para las actividades
        COLOR_CMA = "#CE79FF"
        COLOR_HOSPITALIZACION = "#FAD155"
        
        COLOR_VARIACION = "#FF5733"  # Rojo para variación porcentual
        
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
        # Mapeo de nombres de hospitales a abreviaturas
        mapeo_hospitales = {
            'Hospital Carlos Van Buren (Valparaíso)': 'HCVB',
            'Hospital Claudio Vicuña ( San Antonio)': 'HCV',
            'Hospital Dr. Eduardo Pereira Ramírez (Valparaíso)': 'HEP'
        }
        
        
        if 'Motivo Egreso (Descripción)' in df.columns:
            pivot = df_comp.pivot_table(index='Motivo Egreso (Descripción)', columns='Año', aggfunc='size', fill_value=0)
            fig, ax = plt.subplots(figsize=(10, 6))

            # Crear barras horizontales con los colores específicos
            bar_height = 0.35
            y = np.arange(len(pivot.index))

            datos_2024 = pivot[2024] if 2024 in pivot.columns else pd.Series(0, index=pivot.index)
            datos_2025 = pivot[2025] if 2025 in pivot.columns else pd.Series(0, index=pivot.index)

            bars1 = ax.barh(y - bar_height/2, datos_2024, bar_height, label='2024', color=COLOR_2024)
            bars2 = ax.barh(y + bar_height/2, datos_2025, bar_height, label='2025', color=COLOR_2025)

            ax.set_title(f'Frecuencia por Motivo de Egreso ({max_anio-1} vs {max_anio})')
            ax.set_ylabel('Motivo de Egreso')
            ax.set_xlabel('Cantidad de Egresos')
            ax.set_yticks(y)
            ax.set_yticklabels(pivot.index, rotation=0, ha='right')
            ax.legend(title='Año')

            # Llamar a la función modular para configurar el gráfico
            configurar_grafico(ax)

            # Añadir etiquetas en las barras
            def autolabel_horizontal(bars):
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width, bar.get_y() + bar.get_height()/2,
                            f'{int(width):,}',
                            ha='left', va='center', rotation=0)

            autolabel_horizontal(bars1)
            autolabel_horizontal(bars2)

            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            resultados['barras_motivo_egreso_comparativo.png'] = buf.getvalue()
            if update_progress:
                update_progress()
        if 'Tipo Ingreso (Descripción)' in df.columns:
            pivot = df_comp.pivot_table(index='Tipo Ingreso (Descripción)', columns='Año', aggfunc='size', fill_value=0)
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Crear barras con los colores específicos
            bar_width = 0.35
            x = np.arange(len(pivot.index))
            
            # Asegurarse de que las columnas existan, si no, usar ceros
            datos_2024 = pivot[2024] if 2024 in pivot.columns else pd.Series(0, index=pivot.index)
            datos_2025 = pivot[2025] if 2025 in pivot.columns else pd.Series(0, index=pivot.index)
            
            bars1 = ax.bar(x - bar_width/2, datos_2024, bar_width, label='2024', color=COLOR_2024)
            bars2 = ax.bar(x + bar_width/2, datos_2025, bar_width, label='2025', color=COLOR_2025)
            
            ax.set_title(f'Distribución por Tipo de Ingreso de la Red ({max_anio-1} vs {max_anio})')
            ax.set_xlabel('Tipo de Ingreso')
            ax.set_ylabel('Cantidad de Egresos')
            ax.set_xticks(x)
            ax.set_xticklabels(pivot.index, rotation=0, ha='right')
            ax.legend(title='Año')
            
            # Llamar a la función modular para configurar el gráfico
            configurar_grafico(ax)
            
            # Añadir etiquetas en las barras
            def autolabel(bars):
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2, height,
                           f'{int(height):,}',
                           ha='center', va='bottom', rotation=0)
            
            autolabel(bars1)
            autolabel(bars2)
            
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            resultados['barras_tipo_ingreso_comparativo.png'] = buf.getvalue()
            if update_progress:
                update_progress()
                
        if 'Sexo (Desc)' in df.columns:
            pivot = df_comp.pivot_table(index='Sexo (Desc)', columns='Año', aggfunc='size', fill_value=0)
            fig, ax = plt.subplots(figsize=(8, 5))
            
            # Crear barras con los colores específicos
            bar_width = 0.35
            x = np.arange(len(pivot.index))
            
            # Asegurarse de que las columnas existan, si no, usar ceros
            datos_2024 = pivot[2024] if 2024 in pivot.columns else pd.Series(0, index=pivot.index)
            datos_2025 = pivot[2025] if 2025 in pivot.columns else pd.Series(0, index=pivot.index)
            
            bars1 = ax.bar(x - bar_width/2, datos_2024, bar_width, label='2024', color=COLOR_2024)
            bars2 = ax.bar(x + bar_width/2, datos_2025, bar_width, label='2025', color=COLOR_2025)
            
            ax.set_title(f'Distribución por Sexo ({max_anio-1} vs {max_anio})')
            ax.set_xlabel('Sexo')
            ax.set_ylabel('Cantidad de Egresos')
            ax.set_xticks(x)
            ax.set_xticklabels(pivot.index, rotation=0, ha='center')
            ax.legend(title='Año')
            
            # Llamar a la función modular para configurar el gráfico
            configurar_grafico(ax)
            
            # Añadir etiquetas en las barras
            def autolabel(bars):
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2, height,
                           f'{int(height):,}',
                           ha='center', va='bottom', rotation=0)
            
            autolabel(bars1)
            autolabel(bars2)
            
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            resultados['barras_sexo_comparativo.png'] = buf.getvalue()
            if update_progress:
                update_progress()
        if 'Hospital (Descripción)' in df.columns:
            df_evo = df[(df['Año'].isin([max_anio - 1, max_anio])) & (df['Mes'] <= max_mes)].copy()
            hospitales = df_evo['Hospital (Descripción)'].dropna().unique()
            for hospital in hospitales:
                try:
                    hospital_abreviado = mapeo_hospitales.get(hospital, hospital)
                    df_hosp = df_evo[df_evo['Hospital (Descripción)'] == hospital]
                    idx = pd.MultiIndex.from_product([[max_anio - 1, max_anio], range(1, max_mes + 1)], names=['Año', 'Mes'])
                    pivot = df_hosp.groupby(['Año', 'Mes']).size().reindex(idx, fill_value=0).unstack(0)
                    fig, ax = plt.subplots(figsize=(8, 5))
                    
                    # Usar los colores constantes para las líneas
                    linea_2024 = ax.plot(pivot.index, pivot[2024], marker='o', color=COLOR_2024, label='2024')
                    linea_2025 = ax.plot(pivot.index, pivot[2025], marker='o', color=COLOR_2025, label='2025')
                    
                    ax.set_title(f'Evolución de Egresos - {hospital_abreviado} ({max_anio-1} vs {max_anio})')
                    ax.set_xlabel('Mes')
                    ax.set_ylabel('Egresos')
                    ax.set_xticks(range(1, max_mes + 1))
                    ax.set_xticklabels([
                        'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
                    ][:max_mes])
                    ax.legend(title='Año')
                    # Llamar a la función modular para configurar el gráfico
                    configurar_grafico(ax)
                    plt.tight_layout()
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight')
                    plt.close(fig)
                    buf.seek(0)

                    resultados[f'evolucion_egresos_{hospital_abreviado}.png'] = buf.getvalue()
                    print(f"✅ Gráfico generado para hospital: {hospital}")
                    if update_progress:
                        update_progress()
                except Exception as ex:
                    print(f"❌ Error generando gráfico para {hospital}: {ex}")
        else:
            print("⚠️ Columna 'Hospital de Egreso (Descripción)' no encontrada.")

        if 'Año' in df.columns and 'Hospital (Descripción)' in df.columns:
            df_egresos = df[df['Año'].isin([2024, 2025])].copy()
            # Aplicar el mapeo de abreviaturas usando el diccionario completo
            df_egresos['Hospital (Descripción)'] = df_egresos['Hospital (Descripción)'].map(mapeo_hospitales)
            
            # Agrupar por año y hospital
            egresos_por_hospital = df_egresos.groupby(['Año', 'Hospital (Descripción)']).size().reset_index(name='Egresos')
            
            # Crear un DataFrame con todos los hospitales para ambos años
            hospitales = df_egresos['Hospital (Descripción)'].unique()
            años = [2024, 2025]
            datos_completos = []
            
            for año in años:
                for hospital in hospitales:
                    valor = egresos_por_hospital[
                        (egresos_por_hospital['Año'] == año) & 
                        (egresos_por_hospital['Hospital (Descripción)'] == hospital)
                    ]['Egresos'].values
                    
                    datos_completos.append({
                        'Año': año,
                        'Hospital': hospital,
                        'Egresos': valor[0] if len(valor) > 0 else 0
                    })
            
            df_final = pd.DataFrame(datos_completos)
            
            # Ordenar hospitales por total de egresos
            total_por_hospital = df_final.groupby('Hospital')['Egresos'].sum().sort_values(ascending=False)
            orden_hospitales = total_por_hospital.index.tolist()
            
            # Configurar el gráfico
            fig, ax = plt.subplots(figsize=(10, 6))
            bar_width = 0.35
            x = np.arange(len(orden_hospitales))
            
            # Obtener datos para cada año
            datos_2024 = df_final[df_final['Año'] == 2024].set_index('Hospital').reindex(orden_hospitales)['Egresos']
            datos_2025 = df_final[df_final['Año'] == 2025].set_index('Hospital').reindex(orden_hospitales)['Egresos']
            
            # Crear barras
            bars1 = ax.bar(x - bar_width/2, datos_2024, bar_width, label='2024', color=COLOR_2024)
            bars2 = ax.bar(x + bar_width/2, datos_2025, bar_width, label='2025', color=COLOR_2025)
            
            ax.set_title(f'Egresos Hospitalarios por Hospital y Año')
            ax.set_xlabel('Hospital')
            ax.set_ylabel('Cantidad de Egresos')
            ax.set_xticks(x)
            ax.set_xticklabels(orden_hospitales, rotation=0, ha='center')
            ax.legend(title='Año')
            
            # Llamar a la función modular para configurar el gráfico
            configurar_grafico(ax)
            
            # Añadir etiquetas en las barras
            def autolabel(bars):
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2, height,
                           f'{int(height):,}',
                           ha='center', va='bottom', rotation=0)
            
            autolabel(bars1)
            autolabel(bars2)
            
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            resultados['barras_egresos_por_hospital_y_ano.png'] = buf.getvalue()
            if update_progress:
                update_progress()
        if 'Hospital (Descripción)' in df.columns and 'Tipo Actividad' in df.columns:
            df_cma = df[(df['Tipo Actividad'] == 'Cirugía Mayor Ambulatoria (CMA)') & (df['Año'].isin([max_anio - 1, max_anio])) & (df['Mes'] <= max_mes)].copy()
            hospitales = df_cma['Hospital (Descripción)'].dropna().unique()
            for hospital in hospitales:
                try:
                    hospital_abreviado = mapeo_hospitales.get(hospital, hospital)
                    df_hosp = df_cma[df_cma['Hospital (Descripción)'] == hospital]
                    idx = pd.MultiIndex.from_product([[max_anio - 1, max_anio], range(1, max_mes + 1)], names=['Año', 'Mes'])
                    pivot = df_hosp.groupby(['Año', 'Mes']).size().reindex(idx, fill_value=0).unstack(0)
                    fig, ax = plt.subplots(figsize=(8, 5))

                    # Usar los colores constantes para las líneas
                    linea_2024 = ax.plot(pivot.index, pivot[2024], marker='o', color=COLOR_2024, label='2024')
                    linea_2025 = ax.plot(pivot.index, pivot[2025], marker='o', color=COLOR_2025, label='2025')

                    ax.set_title(f'Evolución de Egresos - {hospital_abreviado} (CMA)')
                    ax.set_xlabel('Mes')
                    ax.set_ylabel('Egresos')
                    ax.set_xticks(range(1, max_mes + 1))
                    ax.set_xticklabels([
                        'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
                    ][:max_mes])
                    ax.legend(title='Año')
                    # Llamar a la función modular para configurar el gráfico
                    configurar_grafico(ax)
                    plt.tight_layout()
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight')
                    plt.close(fig)
                    buf.seek(0)

                    resultados[f'evolucion_egresos_cma_{hospital_abreviado}.png'] = buf.getvalue()
                    print(f"✅ Gráfico generado para hospital (CMA): {hospital}")
                    if update_progress:
                        update_progress()
                except Exception as ex:
                    print(f"❌ Error generando gráfico para {hospital} (CMA): {ex}")
        

        # Asegurarse de que 'Tipo Actividad' esté en el DataFrame
        if 'Tipo Actividad' in df.columns:
            
            # Crear una tabla pivotante para contar los egresos (pacientes) por tipo de actividad y mes
            pivot = df_comp.pivot_table(index='Mes', columns='Tipo Actividad', values='Egresos', aggfunc='count', fill_value=0)
            
            # Calcular la variación porcentual de los egresos (frecuencia de pacientes)
            variacion_porcentual = pivot.pct_change().fillna(0) * 100

            fig, ax = plt.subplots(figsize=(10, 6))

            # Ajustes para barras agrupadas
            bar_width = 0.35
            index = np.arange(len(pivot.index))

            # Barras para 'Cirugía Mayor Ambulatoria (CMA)'
            if 'Cirugía Mayor Ambulatoria (CMA)' in pivot.columns:
                ax.bar(index, pivot['Cirugía Mayor Ambulatoria (CMA)'], bar_width, label='CMA', color=COLOR_CMA)

            # Barras para 'Hospitalización'
            if 'Hospitalización' in pivot.columns:
                ax.bar(index + bar_width, pivot['Hospitalización'], bar_width, label='Hospitalización', color=COLOR_HOSPITALIZACION)

            # Añadir líneas de variación porcentual
            for tipo, color in zip(['Cirugía Mayor Ambulatoria (CMA)', 'Hospitalización'], [COLOR_VARIACION, COLOR_VARIACION]):
                if tipo in variacion_porcentual.columns:
                    # Obtener las alturas de las barras correspondientes
                    alturas_barras = pivot[tipo].values
                    # Ajustar las líneas para que comiencen desde el máximo de las barras
                    ax.plot(index + (bar_width if tipo == 'Hospitalización' else 0), alturas_barras + variacion_porcentual[tipo].values, 
                            marker='o', linestyle='-', color=color, label=f'Variación % {tipo}')

            # Títulos y etiquetas
            ax.set_title('Producción Mensual por Tipo de Actividad y Variación Porcentual')
            ax.set_xlabel('Mes')
            ax.set_ylabel('Frecuencia de Egresos')
            ax.set_xticks(index + bar_width / 2)
            ax.set_xticklabels([
                'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
            ][:len(pivot.index)])
            ax.legend(title='Indicadores')

            # Configuración modular para mejorar visualización
            configurar_grafico(ax)

            # Ajustar la disposición del gráfico para que no se solapen elementos
            plt.tight_layout()

            # Guardar el gráfico en un buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)

            # Guardar el gráfico como imagen en el diccionario de resultados
            resultados['barras_agrupadas_variacion_con_linea.png'] = buf.getvalue()
            print("✅ Gráfico de barras agrupadas con variación porcentual generado.")
            
            # Actualización del progreso
            if update_progress:
                update_progress()

        return resultados

    def ejecutar_analisis(self, df: pd.DataFrame, update_progress=None):
        resultados = {}
        resultados['tablas'] = self.generar_tablas(df, update_progress)
        resultados['graficos'] = self.generar_graficos(df, update_progress)
        
        # Convertir el año a entero en todas las tablas generadas
        for key, table in resultados.items():
            if isinstance(table, pd.DataFrame) and 'Año' in table.columns:
                table['Año'] = table['Año'].astype(int)
        
        return resultados

    @staticmethod
    def get_total_steps():
        return 16
        

def configurar_grafico(ax):
    """
    Configura aspectos comunes de los gráficos, como el grid.
    """
    ax.grid(True)
