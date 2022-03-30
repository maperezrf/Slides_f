# Libraries
import re
from shutil import register_unpack_format
import pandas as pd
import plotly.express as px
from   datetime import date, timedelta, datetime
import plotly.graph_objects as go
import numpy as np
from data import var_f11 as dtagco
from general import set_columns_nunique, set_columns_sum, generate_structure

class F11():
    
    # Constants
    dt_string = datetime.now().strftime('%y%m%d')
    mes=['Jan-21','Feb-21','Mar-21','Apr-21','May-21','Jun-21','Jul-21','Aug-21','Sep-21','Oct-21','Nov-21','Dec-21'] # Editar esta lista cada vez 
    rango_fechas = ['2022-02-20','2022-04-05']

    f11_tcosto  = None
    f11_tm90_costo  = None
    f11_tcant = None
    f11_tm90_cant = None 

    def __init__(self) -> None:
        #self.f11 = pd.read_excel(dtagco['path_df'], dtype=str)
        self.f11 = pd.read_csv(dtagco['path_df'], dtype='object', sep=';')
        self.path = generate_structure("f11")
        self.transform()
        self.f11 = self.f11.sort_values(dtagco['fech_creacion'])
        self.f11_rf = self.f11_filters() # F11 con todos los filtros iniciales
        self.f11_m90 = self.fltr_riesgo(self.f11_rf) # F11 empresa abiertos mayores a 90 días de creados
        self.print_numbers()

    def get_f11(self):
        return self.f11_rf

    def get_f11_m90(self):
        return self.f11_m90

    ## ------ Trasform 
    def transform(self):
        # Dates 
        self.f11[dtagco['fech_creacion']] = pd.to_datetime(self.f11[dtagco['fech_creacion']], format='%Y-%m-%d')
        self.f11[dtagco['mes']] = self.f11[dtagco['fech_creacion']].dt.strftime('%b-%y')
        # Numbers 
        self.f11[dtagco['costo']] = pd.to_numeric(self.f11[dtagco['costo']])
        # Text

    ## ------ Filters
    def f11_filters(self):
        f11_initial = fltr_fecha_desde(self.f11)
        f11_empresa = fltr_empresa(f11_initial)
        f11_emp_abiertos = fltr_abiertos(f11_empresa)
        return f11_emp_abiertos

    def fltr_riesgo(self, df):
        return df.loc[df[dtagco['mes']].isin(self.mes)].reset_index(drop=True) # TODO mejorar estructura

    def load_trend_files(self):
        self.f11_tcosto = pd.read_excel(dtagco['trend_path'], sheet_name='f11_abiertos_costo')
        self.f11_tm90_costo = pd.read_excel(dtagco['trend_path'], sheet_name='f11_abiertos_m90_costo')
        self.f11_tcant = pd.read_excel(dtagco['trend_path'], sheet_name='f11_abiertos_cant')
        self.f11_tm90_cant = pd.read_excel(dtagco['trend_path'], sheet_name='f11_abiertos_m90_cant')

    def get_f11_cutoff(self):
        gb_f11_gm = self.f11_rf.groupby([dtagco['grupo'], dtagco['mes']], sort=False)[dtagco['costo']].sum().reset_index()
        gb_f11_gm_m90 = self.f11_m90.groupby([dtagco['grupo'], dtagco['mes']])[dtagco['costo']].sum().reset_index()
        gb_f11_gm_cant = self.f11_rf.groupby([dtagco['grupo'], dtagco['mes']], sort=False)[dtagco['f11_id']].nunique().reset_index()
        gb_f11_gm_m90_cant = self.f11_m90.groupby([dtagco['grupo'], dtagco['mes']])[dtagco['f11_id']].nunique().reset_index()

        gb_f11_gm = set_fecha_corte(gb_f11_gm)
        gb_f11_gm_m90 = set_fecha_corte(gb_f11_gm_m90)
        gb_f11_gm_cant = set_fecha_corte(gb_f11_gm_cant)
        gb_f11_gm_m90_cant = set_fecha_corte(gb_f11_gm_m90_cant)

        self.f11_tcosto = pd.concat([self.f11_tcosto, gb_f11_gm], axis=0)
        self.f11_tm90_costo = pd.concat([self.f11_tm90_costo, gb_f11_gm_m90], axis=0)
        self.f11_tcant = pd.concat([self.f11_tcant, gb_f11_gm_cant], axis=0)
        self.f11_tm90_cant = pd.concat([self.f11_tm90_cant, gb_f11_gm_m90_cant], axis=0)

        # Transform 
        self.f11_tcosto = transform_df_trend(self.f11_tcosto, dtagco['costo'])
        self.f11_tm90_costo = transform_df_trend(self.f11_tm90_costo, dtagco['costo'])
        self.f11_tcant = transform_df_trend(self.f11_tcant, dtagco['f11_id'])
        self.f11_tm90_cant = transform_df_trend(self.f11_tm90_cant, dtagco['f11_id'])

        writer = pd.ExcelWriter(dtagco['trend_path'], engine='xlsxwriter')
        self.f11_tcosto.to_excel(writer, sheet_name='f11_abiertos_costo', index=False)
        self.f11_tm90_costo.to_excel(writer, sheet_name='f11_abiertos_m90_costo', index=False)
        self.f11_tcant.to_excel(writer, sheet_name='f11_abiertos_cant', index=False)
        self.f11_tm90_cant.to_excel(writer, sheet_name='f11_abiertos_m90_cant', index=False)
        writer.save()

    def tendencias(self):
        self.load_trend_files()
        self.get_f11_cutoff()
        self.get_tendencias_costo()
        self.get_tendencias_cantidad()

    def print_numbers(self):
        print(f'Estados de F11 encontrados: {self.f11_rf[dtagco["estado"]].unique()}')
        print(f'Propietario de f11: {self.f11_rf[dtagco["propietario"]].unique()}')
        print(self.f11_rf.groupby([dtagco['grupo']], sort=False)[dtagco['costo']].sum().sort_values(ascending=False))

    def f11_resfil(self):
        # Gráfica para costo
        gb_f11_gm = self.f11_rf.groupby([dtagco['grupo'], dtagco['mes']], sort=False)[dtagco['costo']].sum().reset_index() # TODO repetido 
        gb_f11_gm = set_columns_sum(gb_f11_gm, dtagco['mes'],dtagco['costo'])
        gb_f11_gm = set_columns_sum(gb_f11_gm, dtagco['grupo'],dtagco['costo'])
        orden_grupo = gb_f11_gm.groupby([dtagco['grupo']], sort=False)[dtagco['costo']].sum().sort_values(ascending=False).reset_index()[dtagco['grupo']].to_list()
        orden_mes = gb_f11_gm[dtagco['mes']].unique().tolist()
        total_abierto = gb_f11_gm[dtagco['costo']].sum()
        gb_f11_3m_grupo = self.f11_m90.groupby(dtagco['grupo'])[dtagco['costo']].sum().reset_index().set_index(dtagco['grupo']) # Calcula los totales de costo por grupo 
        self.fig_f11_costo(gb_f11_gm, gb_f11_3m_grupo, orden_grupo, orden_mes, total_abierto)

        # Gráfica por cantidad 
        gb_f11_gm_cant = self.f11_rf.groupby([dtagco['grupo'], dtagco['mes']], sort=False)[dtagco['f11_id']].nunique().reset_index() # TODO repetido
        gb_f11_gm_cant = set_columns_nunique(gb_f11_gm_cant, dtagco['mes'],dtagco['f11_id'])
        gb_f11_gm_cant = set_columns_nunique(gb_f11_gm_cant, dtagco['grupo'],dtagco['f11_id'])
        orden_grupo_cant = gb_f11_gm_cant.groupby([dtagco['grupo']], sort=False)[dtagco['f11_id']].sum().sort_values(ascending=False).reset_index()[dtagco['grupo']].to_list()
        orden_mes_cant = gb_f11_gm_cant[dtagco['mes']].unique().tolist()
        total_abierto_cant = gb_f11_gm_cant[dtagco['f11_id']].sum()
        gb_f11_3m_cant_grupo = self.f11_m90.groupby(dtagco['grupo'])[dtagco['f11_id']].nunique().reset_index().set_index(dtagco['grupo']) # Calcula los totales de costo por grupo 
        self.fig_f11_cantidad(gb_f11_gm_cant, gb_f11_3m_cant_grupo, orden_grupo_cant, orden_mes_cant, total_abierto_cant)

    def fig_f11_costo(self, df, gb_annotations, orden_grupo, orden_mes, ta):
        f11_empresa_sede = px.bar(df, x=dtagco['mes'], y=dtagco['costo'], color=dtagco['grupo'], text=dtagco['costo'], text_auto='.2s', category_orders={dtagco['grupo']:orden_grupo, dtagco['mes']:orden_mes})
        f11_empresa_sede.update_layout(barmode='stack',title_text=f"F11s empresa abiertos por sede - Total abierto {ta/1e6:,.0f}M") #,uniformtext=dict(mode="hide", minsize=10),legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.1))
        f11_empresa_sede.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="right", x=0.5))
        f11_empresa_sede.add_shape(type="rect",xref="paper", yref="paper",x0=0, y0=0,x1=0.75, y1=0.75,line=dict(color="red", width=2,))
        mes_ref = orden_mes[0] 
        f11_empresa_sede.add_annotation(x=mes_ref, y=1.2*1e9, text= f"Total > 90 días = {gb_annotations.sum()[0]/1e6:,.0f}M", showarrow=False, font = dict (color = "red",size = 17), xanchor='left') # TODO Estas líneas pueden agrupar, en un solo add_annotation, utilizando <br>, y se alinea mejor utilizando fig.update_annotations(align="left") 
        f11_empresa_sede.add_annotation(x=mes_ref, y=1.1*1e9, text= f"CD = {gb_annotations.loc['CD'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
        f11_empresa_sede.add_annotation(x=mes_ref, y=1*1e9, text= f"TIENDAS = {gb_annotations.loc['TIENDAS'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
        f11_empresa_sede.add_annotation(x=mes_ref, y=0.9*1e9, text= f"BODEGA PRODUCTO EN PROCESO = {gb_annotations.loc['BODEGA PRODUCTO EN PROCESO'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
        f11_empresa_sede.add_annotation(x=mes_ref, y=0.8*1e9, text= f"DVD ADMINISTRATIVO = {gb_annotations.loc['DVD ADMINISTRATIVO'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')

        f11_empresa_sede.layout.yaxis.title.text='Total costo promedio'
        f11_empresa_sede.layout.xaxis.title.text='Mes de creación'
        f11_empresa_sede.write_image(f"{self.path}/{self.dt_string}_f11_empresa_abiertos_sede_monto.svg",scale=1, height=800,width=800, engine='orca')
        
    def fig_f11_cantidad(self, df, gb_annotations, orden_grupo, orden_mes, ta):
        f11_es_cantidad = px.bar(df, x=dtagco['mes'], y=dtagco['f11_id'], color=dtagco['grupo'], text=dtagco['f11_id'], text_auto='.0f', category_orders={dtagco['grupo']:orden_grupo, dtagco['mes']:orden_mes})
        f11_es_cantidad.update_layout(barmode='stack',title_text=f"F11s empresa abiertos por sede - Total abierto {ta:,.0f} folios de F11" ) #,uniformtext=dict(mode="hide", minsize=10),legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.1))
        f11_es_cantidad.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="right", x=0.5))
        f11_es_cantidad.add_shape(type="rect",xref="paper", yref="paper",x0=0, y0=0,x1=0.75, y1=1,line=dict(color="red", width=2,))
        mes_ref = orden_mes[0]
        f11_es_cantidad.add_annotation(x=mes_ref, y=1100, text= f"Total > 90 días = {gb_annotations.sum()[0]:,.0f} folios", showarrow=False, font = dict (color = "red",size = 17), xanchor='left') # TODO igual que en la lina 88
        f11_es_cantidad.add_annotation(x=mes_ref, y=1000,text= f"CD = {gb_annotations.loc['CD'][0]:,.0f} folios",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
        f11_es_cantidad.add_annotation(x=mes_ref, y=900,text= f"TIENDAS = {gb_annotations.loc['TIENDAS'][0]:,.0f} folios",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
        f11_es_cantidad.add_annotation(x=mes_ref, y=800,text= f"BODEGA PRODUCTO EN PROCESO = {gb_annotations.loc['BODEGA PRODUCTO EN PROCESO'][0]:,.0f} folios",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
        f11_es_cantidad.add_annotation(x=mes_ref, y=700,text= f"DVD ADMINISTRATIVO = {gb_annotations.loc['DVD ADMINISTRATIVO'][0]:,.0f} folios",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')

        f11_es_cantidad.layout.yaxis.title.text='Cantidad de folios de F11'
        f11_es_cantidad.layout.xaxis.title.text='Mes de creación'
        f11_es_cantidad.write_image(F"{self.path}/{self.dt_string}_f11_empresa_abiertos_sede_cantidad.svg",scale=1, height=800,width=800, engine='orca')

    # ---------------- Trend methods 
    def get_tendencias_costo(self):
        # Total flujo 
        tcd = self.f11_tcosto.loc[self.f11_tcosto[dtagco['grupo']]=='CD']
        ttienda = self.f11_tcosto.loc[(self.f11_tcosto[dtagco['grupo']]=='TIENDAS')|(self.f11_tcosto[dtagco['grupo']]=='DVD ADMINISTRATIVO')]

        gb_tcd = tcd.groupby([dtagco['fecha_corte']])[dtagco['costo']].sum().reset_index()
        gb_ttienda = ttienda.groupby([dtagco['fecha_corte']])[dtagco['costo']].sum().reset_index()

        self.fig_f11_trend_costo(gb_tcd, 'CD', ['rgb(204, 97, 176)'])
        self.fig_f11_trend_costo(gb_ttienda, 'Tiendas & DVD', ['rgb(36, 121, 108)'])

        # Mayores a 90 días 
        tm90_cd = self.f11_tm90_costo.loc[self.f11_tm90_costo[dtagco['grupo']]=='CD']
        tm90_tienda = self.f11_tm90_costo.loc[(self.f11_tm90_costo[dtagco['grupo']]=='TIENDAS')|(self.f11_tm90_costo[dtagco['grupo']]=='DVD ADMINISTRATIVO')]

        gb_tm90_cd = tm90_cd.groupby([dtagco['fecha_corte']])[dtagco['costo']].sum().reset_index()
        gb_tm90_tienda = tm90_tienda.groupby([dtagco['fecha_corte']])[dtagco['costo']].sum().reset_index()

        self.fig_f11_trend_costo(gb_tm90_cd, 'CD mayores a 90 días', ['rgb(204, 97, 176)'])
        self.fig_f11_trend_costo(gb_tm90_tienda, 'Tiendas & DVD mayores a 90 días', ['rgb(36, 121, 108)'])

    def fig_f11_trend_costo(self, df, local, color):
        df[dtagco['costo']] = round(df[dtagco['costo']]/1e6)
        fig_f11_cd_trend = px.line(df, x=dtagco['fecha_corte'], y=dtagco['costo'], labels={dtagco['fecha_corte']:'Fecha de corte', 
        dtagco['costo']: "Costo total (Millones)" }, text=dtagco['costo'], color_discrete_sequence=color, 
        title=f"F11 abiertos {local} según fecha de corte" )
        fig_f11_cd_trend.update_layout(legend=dict(yanchor="top", y=1, xanchor="left", x=0.45))
        fig_f11_cd_trend.update_traces(textposition="bottom right")
        fig_f11_cd_trend.update_xaxes(range=self.rango_fechas, constrain="domain")
        fig_f11_cd_trend.write_image(f"{self.path}/{self.dt_string}_f11_trend_{local}.svg",width=650, height=400, engine='orca')

    def get_tendencias_cantidad(self):
        # Cantidad 
        self.f11_tcant = transform_df_trend(self.f11_tcant, dtagco['f11_id'])
        
        tcd = self.f11_tcant.loc[self.f11_tcant[dtagco['grupo']]=='CD']
        ttienda = self.f11_tcant.loc[(self.f11_tcant[dtagco['grupo']]=='TIENDAS')|(self.f11_tcant[dtagco['grupo']]=='DVD ADMINISTRATIVO')]

        gb_tcd = tcd.groupby([dtagco['fecha_corte']])[dtagco['f11_id']].sum().reset_index()
        gb_ttienda = ttienda.groupby([dtagco['fecha_corte']])[dtagco['f11_id']].sum().reset_index()

        self.fig_f11_trend_cantidad(gb_tcd, 'CD', ['rgb(204, 97, 176)'])
        self.fig_f11_trend_cantidad(gb_ttienda, 'Tiendas & DVD', ['rgb(36, 121, 108)'])

        # Cantidad 90 días 
        self.f11_tm90_cant = transform_df_trend(self.f11_tm90_cant, dtagco['f11_id'])

        tm90_cd = self.f11_tm90_cant.loc[self.f11_tm90_cant[dtagco['grupo']]=='CD']
        tm90_tienda = self.f11_tm90_cant.loc[(self.f11_tm90_cant[dtagco['grupo']]=='TIENDAS')|(self.f11_tm90_cant[dtagco['grupo']]=='DVD ADMINISTRATIVO')]

        gb_tm90_cd = tm90_cd.groupby([dtagco['fecha_corte']])[dtagco['f11_id']].sum().reset_index()
        gb_tm90_tienda = tm90_tienda.groupby([dtagco['fecha_corte']])[dtagco['f11_id']].sum().reset_index()

        self.fig_f11_trend_cantidad(gb_tm90_cd, 'CD mayores a 90 días', ['rgb(204, 97, 176)'])
        self.fig_f11_trend_cantidad(gb_tm90_tienda, 'Tiendas & DVD mayores a 90 días', ['rgb(36, 121, 108)'])

    def fig_f11_trend_cantidad(self, df, local, color):
        fig_f11_cd_trend = px.line(df, x=dtagco['fecha_corte'], y=dtagco['f11_id'], labels={dtagco['fecha_corte']:'Fecha de corte', 
        dtagco['f11_id']: "Cantidad de folios F11" }, text=dtagco['f11_id'], color_discrete_sequence=color, 
        title=f"F11 abiertos {local} según fecha de corte" )
        fig_f11_cd_trend.update_layout(legend=dict(yanchor="top", y=1, xanchor="left", x=0.45))
        fig_f11_cd_trend.update_traces(textposition="bottom right")
        fig_f11_cd_trend.update_xaxes(range=self.rango_fechas, constrain="domain")
        fig_f11_cd_trend.write_image(f"{self.path}/{self.dt_string}_f11_tcant_{local}.svg",width=650, height=400, engine='orca')

# General methods 
def fltr_empresa(df):
    return df.loc[df[dtagco['propietario']] == dtagco['prop_empresa']].reset_index(drop=True)

def fltr_abiertos(df):
    return df.loc[df[dtagco['estado']].isin(dtagco['estados_abiertos'])].reset_index(drop=True)
    
def fltr_fecha_desde(df):
    return df.loc[df[dtagco['fech_creacion']] >= dtagco['fecha_inicial']].reset_index(drop=True)

def transform_df_trend(df, value):
    df[value] = pd.to_numeric(df[value])
    df[dtagco['fecha_corte']] = pd.to_datetime(df[dtagco['fecha_corte']], format='%Y-%m-%d')
    return df 

def set_fecha_corte(df, fecha_corte=date.today()):
    df['FECHA_CORTE']= fecha_corte
    return df

f11 = F11()
f11.f11_resfil()
f11.tendencias()