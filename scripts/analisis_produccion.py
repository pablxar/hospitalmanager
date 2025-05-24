import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AnalisisProduccion:
    def __init__(self, page, nombre_archivo=None):
        self.page = page
        self.nombre_archivo = nombre_archivo

    def generar_tablas(self, df: pd.DataFrame):
        resultados = {}
        # Siempre extraer año y mes de la fecha de egreso
        df = df.copy()  # Evita SettingWithCopyWarning
        df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
        df = df.dropna(subset=['Fecha de egreso completa'])
        df.loc[:, 'Año'] = df['Fecha de egreso completa'].dt.year
        df.loc[:, 'Mes'] = df['Fecha de egreso completa'].dt.month
        # Determinar el mes y año más reciente
        max_fecha = df['Fecha de egreso completa'].max()
        max_anio = max_fecha.year
        max_mes = max_fecha.month
        # Filtrar para que todos los años solo lleguen hasta el último mes disponible
        df_filtrado = df[(df['Mes'] <= max_mes) | (df['Año'] < max_anio)].copy()


        
        if 'Motivo Egreso (Descripción)' in df.columns:
            conteo = df_filtrado.groupby(['Año', 'Mes', 'Motivo Egreso (Descripción)']).size().reset_index(name='Frecuencia')
            resultados['conteo_motivo_egreso_por_anio_mes'] = conteo
            conteo_total = df_filtrado['Motivo Egreso (Descripción)'].value_counts().reset_index()
            conteo_total.columns = ['Motivo Egreso', 'Frecuencia']
            resultados['conteo_motivo_egreso'] = conteo_total

        # Distribución por Tipo Ingreso (Descripción) comparativo por año y mes
        if 'Tipo Ingreso (Descripción)' in df.columns:
            distribucion = df_filtrado.groupby(['Año', 'Mes', 'Tipo Ingreso (Descripción)']).size().reset_index(name='Frecuencia')
            resultados['distribucion_tipo_ingreso_por_anio_mes'] = distribucion
            distribucion_total = df_filtrado['Tipo Ingreso (Descripción)'].value_counts().reset_index()
            distribucion_total.columns = ['Tipo Ingreso', 'Frecuencia']
            resultados['distribucion_tipo_ingreso'] = distribucion_total

        # Distribución por Sexo (Desc) comparativo por año y mes
        if 'Sexo (Desc)' in df.columns:
            distribucion_sexo = df_filtrado.groupby(['Año', 'Mes', 'Sexo (Desc)']).size().reset_index(name='Frecuencia')
            resultados['distribucion_sexo_por_anio_mes'] = distribucion_sexo
            distribucion_sexo_total = df_filtrado['Sexo (Desc)'].value_counts().reset_index()
            distribucion_sexo_total.columns = ['Sexo', 'Frecuencia']
            resultados['distribucion_sexo'] = distribucion_sexo_total

        # Tabla comparativa por Hospital de egresos 2024 y 2025: egresos, peso grd medio, estancia media, edad media, y variación porcentual
        if 'Hospital de Egreso (Descripción)' in df.columns:
            # Filtrar solo 2024 y 2025 hasta el mes acumulado
            hospitales_cols = ['Hospital de Egreso (Descripción)', 'Año', 'Mes']
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
                # Agrupar y calcular métricas
                resumen = df_hosp.groupby(['Año', 'Hospital de Egreso (Descripción)']).agg(
                    egresos=('Hospital de Egreso (Descripción)', 'count'),
                    peso_grd_medio=('Peso GRD', 'mean') if 'Peso GRD' in df_hosp.columns else ('Hospital de Egreso (Descripción)', 'size'),
                    estancia_media=('Estancia', 'mean') if 'Estancia' in df_hosp.columns else ('Hospital de Egreso (Descripción)', 'size'),
                    edad_media=('Edad en años', 'mean') if 'Edad en años' in df_hosp.columns else ('Hospital de Egreso (Descripción)', 'size')
                ).reset_index()
                # Separar por año
                resumen_2024 = resumen[resumen['Año'] == 2024].copy()
                resumen_2025 = resumen[resumen['Año'] == 2025].copy()
                # Renombrar columnas para merge
                resumen_2024 = resumen_2024.rename(columns={
                    'egresos': 'egresos_2024',
                    'peso_grd_medio': 'peso_grd_medio_2024',
                    'estancia_media': 'estancia_media_2024',
                    'edad_media': 'edad_media_2024'
                })
                resumen_2025 = resumen_2025.rename(columns={
                    'egresos': 'egresos_2025',
                    'peso_grd_medio': 'peso_grd_medio_2025',
                    'estancia_media': 'estancia_media_2025',
                    'edad_media': 'edad_media_2025'
                })
                # Unir por hospital
                comparativo = pd.merge(resumen_2024, resumen_2025, on='Hospital de Egreso (Descripción)', how='outer')
                # Variación porcentual de egresos
                comparativo['variacion_egresos_%'] = ((comparativo['egresos_2025'] - comparativo['egresos_2024']) / comparativo['egresos_2024']) * 100
                resultados['comparativo_hospital_2024_2025'] = comparativo
                # También guardar tablas individuales
                resultados['hospitales_2024'] = resumen_2024
                resultados['hospitales_2025'] = resumen_2025

        return resultados

    def generar_graficos(self, df: pd.DataFrame):
        resultados = {}
        # Siempre extraer año y mes de la fecha de egreso
        df = df.copy()  # Evita SettingWithCopyWarning
        df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
        df = df.dropna(subset=['Fecha de egreso completa'])
        df.loc[:, 'Año'] = df['Fecha de egreso completa'].dt.year
        df.loc[:, 'Mes'] = df['Fecha de egreso completa'].dt.month
        # Determinar el año y mes más reciente
        max_fecha = df['Fecha de egreso completa'].max()
        max_anio = max_fecha.year
        max_mes = max_fecha.month
        # Filtrar solo los datos del año más reciente y su anterior, hasta el mes máximo
        anios_comparar = [max_anio - 1, max_anio]
        df_comp = df[df['Año'].isin(anios_comparar) & (df['Mes'] <= max_mes)].copy()


        # Barras Motivo Egreso (Descripción) comparativo por año y mes (solo año más reciente y anterior, hasta el mes máximo)
        if 'Motivo Egreso (Descripción)' in df.columns:
            pivot = df_comp.pivot_table(index='Motivo Egreso (Descripción)', columns='Año', aggfunc='size', fill_value=0)
            fig, ax = plt.subplots(figsize=(10, 6))
            pivot.plot(kind='bar', ax=ax)
            ax.set_title(f'Frecuencia por Motivo de Egreso ({max_anio-1} vs {max_anio}, hasta mes {max_mes})')
            ax.set_xlabel('Motivo de Egreso')
            ax.set_ylabel('Frecuencia')
            ax.legend(title='Año')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            resultados['barras_motivo_egreso_comparativo.png'] = buf.getvalue()

        # Barras Tipo Ingreso (Descripción) comparativo por año y mes (solo año más reciente y anterior, hasta el mes máximo)
        if 'Tipo Ingreso (Descripción)' in df.columns:
            pivot = df_comp.pivot_table(index='Tipo Ingreso (Descripción)', columns='Año', aggfunc='size', fill_value=0)
            fig, ax = plt.subplots(figsize=(10, 6))
            pivot.plot(kind='bar', ax=ax)
            ax.set_title(f'Distribución por Tipo de Ingreso ({max_anio-1} vs {max_anio}, hasta mes {max_mes})')
            ax.set_xlabel('Tipo de Ingreso')
            ax.set_ylabel('Frecuencia')
            ax.legend(title='Año')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            resultados['barras_tipo_ingreso_comparativo.png'] = buf.getvalue()

        # Barras Sexo (Desc) comparativo por año y mes (solo año más reciente y anterior, hasta el mes máximo)
        if 'Sexo (Desc)' in df.columns:
            pivot = df_comp.pivot_table(index='Sexo (Desc)', columns='Año', aggfunc='size', fill_value=0)
            fig, ax = plt.subplots(figsize=(8, 5))
            pivot.plot(kind='bar', ax=ax)
            ax.set_title(f'Distribución por Sexo ({max_anio-1} vs {max_anio}, hasta mes {max_mes})')
            ax.set_xlabel('Sexo')
            ax.set_ylabel('Frecuencia')
            ax.legend(title='Año')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            resultados['barras_sexo_comparativo.png'] = buf.getvalue()

        # Gráfico de evolución de egresos hospitalarios: líneas 2024 vs 2025 por hospital (solo hasta el mes máximo acumulado)
        if 'Hospital de Egreso (Descripción)' in df.columns:
            # Filtrar solo 2024 y 2025 hasta el mes máximo acumulado
            df_evo = df[(df['Año'].isin([2024, 2025])) & (df['Mes'] <= max_mes)].copy()
            hospitales = df_evo['Hospital de Egreso (Descripción)'].unique()
            for hospital in hospitales:
                df_hosp = df_evo[df_evo['Hospital de Egreso (Descripción)'] == hospital]
                if df_hosp.empty:
                    continue
                # Crear MultiIndex con todos los meses y años posibles
                idx = pd.MultiIndex.from_product([[2024, 2025], range(1, max_mes+1)], names=['Año', 'Mes'])
                pivot = df_hosp.groupby(['Año', 'Mes']).size().reindex(idx, fill_value=0).unstack(0)
                if pivot.empty:
                    continue
                fig, ax = plt.subplots(figsize=(8, 5))
                pivot.plot(ax=ax, marker='o')
                ax.set_title(f'Evolución de Egresos - {hospital} (2024 vs 2025, hasta mes {max_mes})')
                ax.set_xlabel('Mes')
                ax.set_ylabel('Egresos')
                ax.set_xticks(range(1, max_mes+1))
                ax.set_xticklabels(range(1, max_mes+1))
                ax.legend(title='Año')
                plt.tight_layout()
                buf = io.BytesIO()
                fig.savefig(buf, format='png')
                plt.close(fig)
                buf.seek(0)
                resultados[f'evolucion_egresos_{hospital}.png'] = buf.getvalue()

        return resultados

    def ejecutar_analisis(self, df: pd.DataFrame, update_progress=None):
        resultados = {}
        resultados['tablas'] = self.generar_tablas(df)
        if update_progress:
            update_progress()
        resultados['graficos'] = self.generar_graficos(df)
        if update_progress:
            update_progress()
        return resultados

    @staticmethod
    def get_total_steps():
        return 6
