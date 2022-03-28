# Libraries
import pandas as pd
import plotly.express as px
from   datetime import date, timedelta, datetime
import plotly.graph_objects as go
import numpy as np
from data import var_f11 as dtagco

class F11():

    # Constants
    dt_string = datetime.now().strftime('%y%m%d')
    mes=['Jan-21','Feb-21','Mar-21','Apr-21','May-21','Jun-21','Jul-21','Aug-21','Sep-21','Oct-21','Nov-21','Dec-21'] # Editar esta lista cada vez 

    def __init__(self) -> None:
        self.f11 = pd.read_excel(dtagco['path_df'], dtype=str, sheet_name='DB')
        self.f11_ant = pd.read_excel(dtagco['trend_path'], dtype=str, sheet_name='f11')
        self.f11_ant_3m = pd.read_excel(dtagco['trend_path'], dtype=str, sheet_name='f11-3meses')
        self.transform()
        self.f11 = self.f11.sort_values(dtagco['fech_creacion'])
        self.f11_rf = self.f11_filters() # F11 con todos los filtros iniciales
        self.f11_m90 = self.fltr_riesgo(self.f11_rf) # F11 empresa abiertos mayores a 90 días de creados

        self.print_numbers()

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

    def get_f11_cutoff(self):
        # Costo 
        gb_f11_gm_m90 = self.f11_m90.groupby([dtagco['grupo'], dtagco['mes']])[dtagco['costo']].sum().reset_index()
        gb_f11_gm_m90.to_excel(f'input/{self.dt_string}_f11_corte_90.xlsx') # TODO Guardar automatico

        # Cantidad
        gb_f11_gm_m90_cant = self.f11_m90.groupby([dtagco['grupo'], dtagco['mes']])[dtagco['f11_id']].nunique().reset_index()
        gb_f11_gm_m90_cant.to_excel(f'input/{self.dt_string}_f11_corte_90_cant.xlsx') # TODO Guardar automatico

    def print_numbers(self):
        print(f'Estados de F11 encontrados: {self.f11_rf[dtagco["estado"]].unique()}')
        print(f'Propietario de f11: {self.f11_rf[dtagco["propietario"]].unique()}')
        print(self.f11_rf.groupby([dtagco['grupo']], sort=False)[dtagco['costo']].sum().sort_values(ascending=False))

    def f11_resfil(self):
        # Gráfica para costo
        gb_f11_gm = self.f11_rf.groupby([dtagco['grupo'], dtagco['mes']], sort=False)[dtagco['costo']].sum().reset_index()
        gb_f11_gm.to_excel(f'input/{self.dt_string}_f11_corte.xlsx') # TODO Guardar automatico
        gb_f11_gm = set_columns_sum(gb_f11_gm, dtagco['mes'])
        gb_f11_gm = set_columns_sum(gb_f11_gm, dtagco['grupo'])
        orden_grupo = gb_f11_gm.groupby([dtagco['grupo']], sort=False)[dtagco['costo']].sum().sort_values(ascending=False).reset_index()[dtagco['grupo']].to_list()
        orden_mes = gb_f11_gm[dtagco['mes']].unique().tolist()
        total_abierto = gb_f11_gm[dtagco['costo']].sum()
        gb_f11_3m_grupo = self.f11_m90.groupby(dtagco['grupo'])[dtagco['costo']].sum().reset_index().set_index(dtagco['grupo']) # Calcula los totales de costo por grupo 
        self.fig_f11_costo(gb_f11_gm, gb_f11_3m_grupo, orden_grupo, orden_mes, total_abierto)

        # Gráfica por cantidad 
        gb_f11_gm_cant = self.f11_rf.groupby([dtagco['grupo'], dtagco['mes']], sort=False)[dtagco['f11_id']].nunique().reset_index()
        gb_f11_gm_cant.to_excel(f'input/{self.dt_string}_f11_corte_cant.xlsx') # TODO Guardar automatico
        gb_f11_gm_cant = set_columns_nunique(gb_f11_gm_cant, dtagco['mes'])
        gb_f11_gm_cant = set_columns_nunique(gb_f11_gm_cant, dtagco['grupo'])
        orden_grupo_cant = gb_f11_gm_cant.groupby([dtagco['grupo']], sort=False)[dtagco['f11_id']].sum().sort_values(ascending=False).reset_index()[dtagco['grupo']].to_list()
        orden_mes_cant = gb_f11_gm_cant[dtagco['mes']].unique().tolist()
        total_abierto_cant = gb_f11_gm_cant[dtagco['f11_id']].sum()
        gb_f11_3m_cant_grupo = self.f11_m90.groupby(dtagco['grupo'])[dtagco['f11_id']].nunique().reset_index().set_index(dtagco['grupo']) # Calcula los totales de costo por grupo 
        self.fig_f11_cantidad(gb_f11_gm_cant, gb_f11_3m_cant_grupo, orden_grupo_cant, orden_mes_cant, total_abierto_cant)

    def fig_f11_costo(self, df, gb_annotations, orden_grupo, orden_mes, ta):
        f11_empresa_sede = px.bar(df, x=dtagco['mes'], y=dtagco['costo'], color=dtagco['grupo'], text=dtagco['costo'], text_auto='.2s', category_orders={dtagco['grupo']:orden_grupo, dtagco['mes']:orden_mes})
        f11_empresa_sede.update_layout(barmode='stack',title_text=f"F11s empresa abiertos por sede - Total abierto {ta/1e6:,.0f}M") #,uniformtext=dict(mode="hide", minsize=10),legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.1))
        f11_empresa_sede.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="right", x=0.5))
        f11_empresa_sede.add_shape(type="rect",xref="paper", yref="paper",x0=0, y0=0,x1=0.77, y1=0.75,line=dict(color="red", width=2,))
        mes_ref = orden_mes[0] 
        f11_empresa_sede.add_annotation(x=mes_ref, y=0.8*1e9, text= f"Total > 90 días = {gb_annotations.sum()[0]/1e6:,.0f}M", showarrow=False, font = dict (color = "red",size = 17), xanchor='left') # TODO Estas líneas pueden agrupar, en un solo add_annotation, utilizando <br>, y se alinea mejor utilizando fig.update_annotations(align="left") 
        f11_empresa_sede.add_annotation(x=mes_ref, y=0.75*1e9, text= f"CD = {gb_annotations.loc['CD'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
        f11_empresa_sede.add_annotation(x=mes_ref, y=0.7*1e9, text= f"TIENDAS = {gb_annotations.loc['TIENDAS'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
        f11_empresa_sede.add_annotation(x=mes_ref, y=0.65*1e9, text= f"BODEGA PRODUCTO EN PROCESO = {gb_annotations.loc['BODEGA PRODUCTO EN PROCESO'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
        f11_empresa_sede.add_annotation(x=mes_ref, y=0.6*1e9, text= f"DVD ADMINISTRATIVO = {gb_annotations.loc['DVD ADMINISTRATIVO'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')

        f11_empresa_sede.layout.yaxis.title.text='Total costo promedio'
        f11_empresa_sede.layout.xaxis.title.text='Mes de creación'
        f11_empresa_sede.write_image(F"images/{self.dt_string}_f11_empresa_abiertos_sede_monto.svg",scale=1, height=800,width=800, engine='orca')
        
    def fig_f11_cantidad(self, df, gb_annotations, orden_grupo, orden_mes, ta):
        f11_es_cantidad = px.bar(df, x=dtagco['mes'], y=dtagco['f11_id'], color=dtagco['grupo'], text=dtagco['f11_id'], text_auto='.0f', category_orders={dtagco['grupo']:orden_grupo, dtagco['mes']:orden_mes})
        f11_es_cantidad.update_layout(barmode='stack',title_text=f"F11s empresa abiertos por sede - Total abierto {ta:,.0f} folios de F11" ) #,uniformtext=dict(mode="hide", minsize=10),legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.1))
        f11_es_cantidad.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="right", x=0.5))
        f11_es_cantidad.add_shape(type="rect",xref="paper", yref="paper",x0=0, y0=0,x1=0.77, y1=1,line=dict(color="red", width=2,))
        mes_ref = orden_mes[0]
        f11_es_cantidad.add_annotation(x=mes_ref, y=1100, text= f"Total > 90 días = {gb_annotations.sum()[0]:,.0f} folios", showarrow=False, font = dict (color = "red",size = 17), xanchor='left') # TODO igual que en la lina 88
        f11_es_cantidad.add_annotation(x=mes_ref, y=1000,text= f"CD = {gb_annotations.loc['CD'][0]:,.0f} folios",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
        f11_es_cantidad.add_annotation(x=mes_ref, y=900,text= f"TIENDAS = {gb_annotations.loc['TIENDAS'][0]:,.0f} folios",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
        f11_es_cantidad.add_annotation(x=mes_ref, y=800,text= f"BODEGA PRODUCTO EN PROCESO = {gb_annotations.loc['BODEGA PRODUCTO EN PROCESO'][0]:,.0f} folios",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
        f11_es_cantidad.add_annotation(x=mes_ref, y=700,text= f"DVD ADMINISTRATIVO = {gb_annotations.loc['DVD ADMINISTRATIVO'][0]:,.0f} folios",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')

        f11_es_cantidad.layout.yaxis.title.text='Cantidad de folios de F11'
        f11_es_cantidad.layout.xaxis.title.text='Mes de creación'
        f11_es_cantidad.write_image(F"images/{self.dt_string}_f11_empresa_abiertos_sede_cantidad.svg",scale=1, height=700,width=850, engine='orca')

# General methods 
def fltr_empresa(df):
    return df.loc[df[dtagco['propietario']] == dtagco['prop_empresa']].reset_index(drop=True)

def fltr_abiertos(df):
    return df.loc[df[dtagco['estado']].isin(dtagco['estados_abiertos'])].reset_index(drop=True)
    
def fltr_fecha_desde(df):
    return df.loc[df[dtagco['fech_creacion']] >= dtagco['fecha_inicial']].reset_index(drop=True)

def set_columns_sum(base, var):    
    lista = base.loc[base[var].notna()][var].unique()
    gb_var = base.groupby(var)[dtagco['costo']].sum().reset_index()
    gb_var.set_index(var, inplace=True)
    for item in lista:
        base.loc[base[var]==item, var] = f'{item} ${round(gb_var.loc[item, dtagco["costo"]]/1e6):,.0f}M'
    return base 

def set_columns_nunique(base, var):    
    lista = base.loc[base[var].notna()][var].unique()
    gb_var = base.groupby(var)[dtagco['f11_id']].sum().reset_index()
    gb_var.set_index(var, inplace=True)
    for item in lista:
        base.loc[base[var]==item, var] = f'{item} {round(gb_var.loc[item, dtagco["f11_id"]]):,.0f}'
    return base 
""" 
    # Tendencias 

    # Rango de fechas a graficar
    rango_fechas = ['2021-12-15','2022-03-31']

    f11_ant['COSTO'] = pd.to_numeric(f11_ant['COSTO'])
    f11_ant['Fecha PPT'] = pd.to_datetime(f11_ant['Fecha PPT'], format='%Y-%m-%d')
    gb_f11_ant = f11_ant.groupby(['Fecha PPT', 'SEDE'])['COSTO'].sum().reset_index()
    ult_corte = gb_f11_ant.loc[gb_f11_ant['Fecha PPT']>'2021-12-15'].reset_index(drop=True)
    ult_corte["COSTO"] = round(ult_corte["COSTO"]/1e6)

    # CD 
    trend_cd = ult_corte.loc[ult_corte['SEDE']=='CD']
    fig_f11_cd_trend = px.line(trend_cd, x="Fecha PPT", y="COSTO", labels={'Fecha PPT':'Fecha de corte', "COSTO": "Costo total (Millones)" }, 
    text='COSTO', color_discrete_sequence=['rgb(204, 97, 176)'], title=f"F11 abiertos CD según fecha de corte" )
    fig_f11_cd_trend.update_layout(legend=dict(yanchor="top", y=1, xanchor="left", x=0.45))
    fig_f11_cd_trend.update_traces(textposition="bottom right")
    fig_f11_cd_trend.update_xaxes(range=rango_fechas, constrain="domain")
    fig_f11_cd_trend.write_image(f"images/{dt_string}_F11_TENDENCIA_CD.svg",width=650, height=400, engine='orca')

    # Tienda
    trend_tienda = ult_corte.loc[ult_corte['SEDE']=='TIENDAS']
    fig_f11_tienda_trend = px.line(trend_tienda, x="Fecha PPT", y="COSTO", labels={'Fecha PPT':'Fecha de corte', "COSTO": "Costo total (Millones)" },
    text='COSTO', color_discrete_sequence=['rgb(36, 121, 108)'], title=f"F11 abiertos Tienda según fecha de corte" )
    fig_f11_tienda_trend.update_layout(legend=dict(yanchor="top", y=1, xanchor="left", x=0.45))
    fig_f11_tienda_trend.update_traces(textposition="bottom right")
    fig_f11_tienda_trend.update_xaxes(range=rango_fechas, constrain="domain")
    fig_f11_tienda_trend.write_image(f"images/{dt_string}_F11_TENDENCIA_TIENDA.svg",width=650, height=400, engine='orca')

    # tend 90 dias 

    f11_ant_3m[dtagco['costo']] = pd.to_numeric(f11_ant_3m[dtagco['costo']])
    f11_ant_3m['FECHA_CORTE'] = pd.to_datetime(f11_ant_3m['FECHA_CORTE'], format='%Y-%m-%d')
    gb_corte = f11_ant_3m.groupby(['FECHA_CORTE', dtagco['grupo']])[dtagco['costo']].sum().reset_index()
    gb_corte[dtagco['costo']] = round(gb_corte[dtagco['costo']]/1e6)

    rango_fechas = ['2021-12-30','2022-03-31']
    trend_cd_3m = gb_corte.loc[gb_corte[dtagco['grupo']]=='CD'].reset_index(drop=True)

    fig_f11_cd_trend_90 = px.line(trend_cd_3m, x="FECHA_CORTE", y=dtagco['costo'], labels={'FECHA_CORTE':'Fecha de corte', dtagco['costo']: "Costo total (Millones)" },
    text=dtagco['costo'], color_discrete_sequence=['rgb(204, 97, 176)'], title=f"F11 CD abiertos con más de 90 días" )
    fig_f11_cd_trend_90.update_layout(legend=dict(yanchor="top", y=1, xanchor="left", x=0.45))
    fig_f11_cd_trend_90.update_traces(textposition="bottom right")
    fig_f11_cd_trend_90.update_xaxes(range=rango_fechas, constrain="domain")
    fig_f11_cd_trend_90.write_image(f"images/{dt_string}_f11_trend_CD_90.svg",width=600, height=400, engine='orca')

    trend_cd_3m = gb_corte.loc[(gb_corte[dtagco['grupo']]=='TIENDAS') ].reset_index(drop=True)
    fig_f11_tienda_trend_90 = px.line(trend_cd_3m, x="FECHA_CORTE", y=dtagco['costo'], labels={'FECHA_CORTE':'Fecha de corte', dtagco['costo']: "Costo total (Millones)" },
    text=dtagco['costo'], color_discrete_sequence=['rgb(36, 121, 108)'], title=f"F11 Tienda abiertos con más de 90 días" )
    fig_f11_tienda_trend_90.update_layout(legend=dict(yanchor="top", y=1, xanchor="left", x=0.45))
    fig_f11_tienda_trend_90.update_traces(textposition="bottom right")
    fig_f11_tienda_trend_90.update_xaxes(range=rango_fechas, constrain="domain")
    fig_f11_tienda_trend_90.write_image(f"images/{dt_string}_f11_trend_TIENDA_90.svg",width=600, height=400, engine='orca') """

    ## ------ Output 
    # TODO guardar figuras en una carpeta para cada corte 

f11 = F11()
f11.get_f11_cutoff()
f11.f11_resfil()