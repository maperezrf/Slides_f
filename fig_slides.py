# Libraries
import pandas as pd
import plotly.express as px
from   datetime import date, timedelta, datetime
import plotly.graph_objects as go
import numpy as np
import data as dtagco

# Constants
dt_string = datetime.now().strftime('%y%m%d')
mes=['Jan-21','Feb-21','Mar-21','Apr-21','May-21','Jun-21','Jul-21','Aug-21','Sep-21','Oct-21','Nov-21','Dec-21'] # Editar esta lista cada vez 

## ------ Variables 
# TODO cargar archivos f3, f4, f11
f11 = pd.read_excel(dtagco['path_df'], dtype=str, sheet_name='DB')
f11_ant = pd.read_excel('input/tendencias.xlsx', dtype=str, sheet_name='f11')
f11_ant_3m = pd.read_excel('input/tendencias.xlsx', dtype=str, sheet_name='f11-3meses')

## ------ Trasform 
# TODO transformar variables 

# Dates 
f11[dtagco['fech_creacion']] = pd.to_datetime(f11[dtagco['fech_creacion']], format='%Y-%m-%d')
f11[dtagco['mes']] = f11[dtagco['fech_creacion']].dt.strftime('%b-%y')

# Numbers 
f11[dtagco['costo']] = pd.to_numeric(f11[dtagco['costo']])

# Text

## ------ Filters 
# TODO realizar filtrol a los dataframes

f11 = f11.sort_values(dtagco['fech_creacion'])

f11_empresa = f11.loc[f11[dtagco['propietario']] == dtagco['prop_empresa']]
f11_empresa = f11_empresa.loc[f11_empresa[dtagco['estado']].isin(dtagco['estados_abiertos'])]
f11_empresa = f11_empresa.loc[f11_empresa[dtagco['fech_creacion']] >= dtagco['fecha_inicial']].reset_index(drop=True)
f11_3m = f11_empresa.loc[f11_empresa[dtagco['mes']].isin(mes)]

# TODO REVISAR POSICION 
f11_corte = f11_empresa.groupby([dtagco['grupo'], dtagco['mes']])[dtagco['costo']].sum().reset_index()
f11_corte.to_excel(f'input/{dt_string}_f11_corte.xlsx')
f11_corte_3m = f11_3m.groupby([dtagco['grupo'], dtagco['mes']])[dtagco['costo']].sum().reset_index()
f11_corte_3m.to_excel(f'input/{dt_string}_f11_corte_90.xlsx')

## ------ Methods 
# TODO crear método por f y por imagen 
# Nombralos fx_slide() y fig_fx_xxx()

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

# F11 

## ------ Groupbys

gb_f11_grupo_mes = f11_empresa.groupby([dtagco['grupo'],dtagco['mes']], sort=False)[dtagco['costo']].sum().reset_index()


gb_f11_grupo_mes = set_columns_sum(gb_f11_grupo_mes, dtagco['mes'])
gb_f11_grupo_mes = set_columns_sum(gb_f11_grupo_mes, dtagco['grupo'])

f11_grupo = gb_f11_grupo_mes.groupby([dtagco['grupo']], sort=False)[dtagco['costo']].sum().sort_values(ascending=False).reset_index()
orden_grupo = f11_grupo[dtagco['grupo']].to_list()
orden_mes = gb_f11_grupo_mes[dtagco['mes']].unique().tolist()
total_abierto = gb_f11_grupo_mes[dtagco['costo']].sum()

gb_f11_3m_grupo = f11_3m.groupby('GRUPO')['TOTAL_COSTO'].sum().reset_index().set_index('GRUPO') # Calcula los totales de costo por grupo 


print(f'Estados de F11 encontrados: {f11_empresa.ESTADO.unique()}')

def fig_f11_costo():
    f11_empresa_sede = px.bar(gb_f11_grupo_mes, x=dtagco['mes'], y=dtagco['costo'], color=dtagco['grupo'], text=dtagco['costo'], text_auto='.2s', category_orders={dtagco['grupo']:orden_grupo, dtagco['mes']:orden_mes})
    f11_empresa_sede.update_layout(barmode='stack',title_text=f"F11s empresa abiertos por sede - Total abierto {total_abierto/1e6:,.0f}M") #,uniformtext=dict(mode="hide", minsize=10),legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.1))
    f11_empresa_sede.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="right", x=0.5))
    f11_empresa_sede.add_shape(type="rect",xref="paper", yref="paper",x0=0, y0=0,x1=0.77, y1=0.75,line=dict(color="red", width=2,))

    #TODO arreglar para que se ponga el mes automatico 
    mes_ref = 'Mar-21 $1M'
    f11_empresa_sede.add_annotation(x=mes_ref, y=0.8*1e9, text= f"Total > 90 días = {gb_f11_3m_grupo.sum()[0]/1e6:,.0f}M", showarrow=False, font = dict (color = "red",size = 17), xanchor='left')
    f11_empresa_sede.add_annotation(x=mes_ref, y=0.75*1e9, text= f"CD = {gb_f11_3m_grupo.loc['CD'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
    f11_empresa_sede.add_annotation(x=mes_ref, y=0.7*1e9, text= f"TIENDAS = {gb_f11_3m_grupo.loc['TIENDAS'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
    f11_empresa_sede.add_annotation(x=mes_ref, y=0.65*1e9, text= f"BODEGA PRODUCTO EN PROCESO = {gb_f11_3m_grupo.loc['BODEGA PRODUCTO EN PROCESO'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')
    f11_empresa_sede.add_annotation(x=mes_ref, y=0.6*1e9, text= f"DVD ADMINISTRATIVO = {gb_f11_3m_grupo.loc['DVD ADMINISTRATIVO'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 12), xanchor='left')

    f11_empresa_sede.layout.yaxis.title.text='Total costo promedio'
    f11_empresa_sede.layout.xaxis.title.text='Mes de creación'
    f11_empresa_sede.write_image(F"images/{dt_string}_f11_empresa_abiertos_sede.svg",scale=1, height=800,width=800, engine='orca')

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
fig_f11_tienda_trend_90.write_image(f"images/{dt_string}_f11_trend_TIENDA_90.svg",width=600, height=400, engine='orca')


# F3 

# F4 

## ------ Output 
# TODO guardar figuras en una carpeta para cada corte 
