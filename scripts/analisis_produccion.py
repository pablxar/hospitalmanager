import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AnalisisProduccion:
    def __init__(self, page, nombre_archivo=None):
        self.page = page
        self.nombre_archivo = nombre_archivo

    def generar_tablas(self, df: pd.DataFrame, update_progress=None):
        resultados = {}
        df = df.copy()
        df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
        df = df.dropna(subset=['Fecha de egreso completa'])
        df.loc[:, 'Año'] = df['Fecha de egreso completa'].dt.year
        df.loc[:, 'Mes'] = df['Fecha de egreso completa'].dt.month
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
                resumen_2024 = resumen[resumen['Año'] == 2024].copy()
                resumen_2025 = resumen[resumen['Año'] == 2025].copy()
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
                comparativo = pd.merge(resumen_2024, resumen_2025, on='Hospital (Descripción)', how='outer')
                comparativo['variacion_egresos_%'] = ((comparativo['egresos_2025'] - comparativo['egresos_2024']) / comparativo['egresos_2024']) * 100
                resultados['comparativo_hospital_2024_2025'] = comparativo
                resultados['hospitales_2024'] = resumen_2024
                resultados['hospitales_2025'] = resumen_2025
                if update_progress:
                    update_progress()
        return resultados

    def generar_graficos(self, df: pd.DataFrame, update_progress=None):
        resultados = {}
        df = df.copy()
        df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
        df = df.dropna(subset=['Fecha de egreso completa'])
        df.loc[:, 'Año'] = df['Fecha de egreso completa'].dt.year
        df.loc[:, 'Mes'] = df['Fecha de egreso completa'].dt.month
        if df.empty:
            print("⚠️ El DataFrame está vacío luego del procesamiento de fechas.")
            return resultados
        max_fecha = df['Fecha de egreso completa'].max()
        max_anio = max_fecha.year
        max_mes = max_fecha.month
        anios_comparar = [max_anio - 1, max_anio]
        df_comp = df[df['Año'].isin(anios_comparar) & (df['Mes'] <= max_mes)].copy()
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
            if update_progress:
                update_progress()
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
            if update_progress:
                update_progress()
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
            if update_progress:
                update_progress()
        if 'Hospital (Descripción)' in df.columns:
            df_evo = df[(df['Año'].isin([max_anio - 1, max_anio])) & (df['Mes'] <= max_mes)].copy()
            hospitales = df_evo['Hospital (Descripción)'].dropna().unique()
            for hospital in hospitales:
                try:
                    df_hosp = df_evo[df_evo['Hospital (Descripción)'] == hospital]
                    idx = pd.MultiIndex.from_product([[max_anio - 1, max_anio], range(1, max_mes + 1)], names=['Año', 'Mes'])
                    pivot = df_hosp.groupby(['Año', 'Mes']).size().reindex(idx, fill_value=0).unstack(0)
                    fig, ax = plt.subplots(figsize=(8, 5))
                    pivot.plot(ax=ax, marker='o')
                    ax.set_title(f'Evolución de Egresos - {hospital} ({max_anio-1} vs {max_anio}, hasta mes {max_mes})')
                    ax.set_xlabel('Mes')
                    ax.set_ylabel('Egresos')
                    ax.set_xticks(range(1, max_mes + 1))
                    ax.set_xticklabels([
                        'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
                    ][:max_mes])
                    ax.legend(title='Año')
                    plt.tight_layout()
                    buf = io.BytesIO()
                    fig.savefig(buf, format='png')
                    plt.close(fig)
                    buf.seek(0)

                    resultados[f'evolucion_egresos_{hospital}.png'] = buf.getvalue()
                    print(f"✅ Gráfico generado para hospital: {hospital}")
                    if update_progress:
                        update_progress()
                except Exception as ex:
                    print(f"❌ Error generando gráfico para {hospital}: {ex}")
        else:
            print("⚠️ Columna 'Hospital de Egreso (Descripción)' no encontrada.")
        return resultados

    def ejecutar_analisis(self, df: pd.DataFrame, update_progress=None):
        resultados = {}
        resultados['tablas'] = self.generar_tablas(df, update_progress)
        resultados['graficos'] = self.generar_graficos(df, update_progress)
        return resultados

    @staticmethod
    def get_total_steps():
        return 11
