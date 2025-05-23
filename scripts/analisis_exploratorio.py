import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class AnalisisExploratorio:
    def __init__(self, page, nombre_archivo=None):
        self.page = page
        self.nombre_archivo = nombre_archivo

    def generar_tablas(self, df: pd.DataFrame):
        resultados = {}
        # Siempre extraer año y mes de la fecha de egreso
        df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
        df = df.dropna(subset=['Fecha de egreso completa'])
        df['Año'] = df['Fecha de egreso completa'].dt.year
        df['Mes'] = df['Fecha de egreso completa'].dt.month
        # Determinar el mes y año más reciente
        max_fecha = df['Fecha de egreso completa'].max()
        max_anio = max_fecha.year
        max_mes = max_fecha.month
        # Filtrar para que todos los años solo lleguen hasta el último mes disponible
        df_filtrado = df[(df['Mes'] <= max_mes) | (df['Año'] < max_anio)]

        # Conteo por Motivo Egreso (Descripción) comparativo por año y mes
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

        return resultados

    def generar_graficos(self, df: pd.DataFrame):
        resultados = {}
        # Siempre extraer año y mes de la fecha de egreso
        df['Fecha de egreso completa'] = pd.to_datetime(df['Fecha de egreso completa'], errors='coerce')
        df = df.dropna(subset=['Fecha de egreso completa'])
        df['Año'] = df['Fecha de egreso completa'].dt.year
        df['Mes'] = df['Fecha de egreso completa'].dt.month
        # Determinar el año y mes más reciente
        max_fecha = df['Fecha de egreso completa'].max()
        max_anio = max_fecha.year
        max_mes = max_fecha.month
        # Filtrar solo los datos del año más reciente y su anterior, hasta el mes máximo
        anios_comparar = [max_anio - 1, max_anio]
        df_comp = df[df['Año'].isin(anios_comparar) & (df['Mes'] <= max_mes)]

        # Histograma de Edad en años (solo para el año más reciente y anterior, hasta el mes máximo)
        if 'Edad en años' in df.columns:
            for anio in anios_comparar:
                if anio in df_comp['Año'].unique():
                    fig, ax = plt.subplots()
                    df_comp[df_comp['Año'] == anio]['Edad en años'].hist(bins=20, ax=ax)
                    ax.set_title(f'Histograma de Edad - {int(anio)} (hasta mes {max_mes})')
                    ax.set_xlabel('Edad')
                    ax.set_ylabel('Frecuencia')
                    buf = io.BytesIO()
                    fig.savefig(buf, format='png')
                    plt.close(fig)
                    buf.seek(0)
                    resultados[f'histograma_edad_{int(anio)}.png'] = buf.getvalue()
            # Histograma total de ambos años
            fig, ax = plt.subplots()
            df_comp['Edad en años'].hist(bins=20, ax=ax)
            ax.set_title(f'Histograma de Edad ({max_anio-1} y {max_anio}, hasta mes {max_mes})')
            ax.set_xlabel('Edad')
            ax.set_ylabel('Frecuencia')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            resultados['histograma_edad_comparativo.png'] = buf.getvalue()

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
