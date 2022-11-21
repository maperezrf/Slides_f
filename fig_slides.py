# Libraries
import pandas as pd
import plotly.express as px
from   datetime import date, timedelta, datetime
import plotly.graph_objects as go
import numpy as np
import constants as const
from calendar import monthrange
pd.set_option('display.max_columns', 500)
dt_string = datetime.now().strftime('%y%m%d')
mes=['Jan-21','Feb-21','Mar-21','Apr-21','May-21','Jun-21','Jul-21','Aug-21','Sep-21','Oct-21','Nov-21','Dec-21'] # Editar esta lista cada vez 

## ------ Variables 
# TODO cargar archivos f3, f4, f11
f11 = pd.read_excel('input/220322_f11.xlsx', dtype=str, sheet_name='DB')
f4 = pd.read_csv('input/220322_f4.csv', dtype=object, sep=";")

## ------ Trasform 
# TODO transformar variables 

# Dates
# F11 
f11['FECHA_CREACION'] = pd.to_datetime(f11['FECHA_CREACION'], format='%Y-%m-%d')
f11['MES'] = f11['FECHA_CREACION'].dt.strftime('%b-%y')

# F4
fechas = ['fecha_creacion', 'fecha_reserva', 'fecha_envio']
f4.loc[:, fechas] = f4[fechas].apply(lambda x: x.replace(["ene", "abr", "ago", "dic"], ["jan", "apr", "aug", "dec"], regex=True))
for i in fechas:
    f4[i] = pd.to_datetime(f4[i])
f4['mes'] = f4['fecha_reserva'].dt.strftime('%b')



# Numbers 
# F11
f11['TOTAL_COSTO'] = pd.to_numeric(f11['TOTAL_COSTO'])
# F4
f4['total_precio_costo'] = pd.to_numeric(f4['total_precio_costo'], downcast= 'integer')

# Text

## ------ Filters 
# TODO realizar filtrol a los dataframes
f11_empresa = f11.loc[f11.PROPIETARIO == 'EMPRESA'].reset_index(drop=True)
f11_empresa = f11_empresa.loc[f11_empresa.ESTADO.isin(['Despachado','Espera Retiro Clte.','Ingresado','Entrega parcial'])].reset_index(drop=True)
f11_empresa = f11_empresa.sort_values('FECHA_CREACION')
print(f'Estados de F11 encontrados: {f11_empresa.ESTADO.unique()}')

# F4 x semanas
f4 = f4.sort_values("fecha_reserva")
f4_dado_baja = f4.loc[(f4.tipo_redinv == 'dado de baja')]
f4_registrados = f4_dado_baja.loc[(f4_dado_baja.fecha_creacion >='2022-01-01') &(f4_dado_baja.estado =='registrado'), 'total_precio_costo'].sum()/1e6
f4_22 = f4_dado_baja.loc[(f4_dado_baja.fecha_reserva >='2022-01-01') & (f4_dado_baja.estado == "reservado")].reset_index()
f4_ults= f4_22.loc[f4_22.estado == "reservado"].reset_index(drop=True)
# F4 x años
f4_reservado = f4_dado_baja.loc[f4_dado_baja.estado == "reservado"].reset_index()
f4_reservado.loc[((f4_reservado.fecha_reserva >='2021-01-01') & (f4_reservado.fecha_reserva <'2021-12-31')), "año"] = "2021"
f4_reservado.loc[(f4_reservado.fecha_reserva >='2022-01-01'), "año"] = "2022"
print(f'Existen {f4_registrados:,.0f} M en estado registrado en 2022')


# Agregar local_agg
f4_22.loc[f4_22.local.isin(const.tienda), 'Local_agg'] = 'TIENDA'
f4_22.loc[f4_22.local.isin(const.cd), 'Local_agg'] = 'CD'
f4_22.loc[f4_22.local == "3001", 'Local_agg'] = 'DVD ADMINISTRATIVO'
f4_22.loc[f4_22.local == "11", 'Local_agg'] = 'VENTA EMPRESA'

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
def set_week_f4(base_f4):
    lista_mes = base_f4.mes.unique()
    f_inicio  = datetime.strptime('2022/01/01', '%Y/%m/%d')
    f_cortes = f_inicio
    for mes in enumerate(lista_mes):
        sem = 0
        while f_cortes <= base_f4.loc[base_f4.mes == mes[1], "fecha_reserva"].max():
            sem = sem + 1
            f_cortes = f_inicio + timedelta(days = 7)
            if sem == 4:
                dias = monthrange(2011,mes[0]+1)[1]
                if dias == 28:
                    pass
                elif dias == 30:
                    f_cortes = f_cortes + timedelta(days = 2)
                elif dias == 31:
                    f_cortes = f_cortes + timedelta(days = 3)
            base_f4.loc[(base_f4.fecha_reserva >= f_inicio) & (base_f4.fecha_reserva <= f_cortes), "Semana (fecha de reserva)"] = f"S{sem}{f_cortes.strftime('%b')}"
            f_inicio = f_cortes
# Groupby_f4
# F4 x semanas
f4_x_semanas = f4_ults.groupby(["Local", "Semana (fecha de reserva)"], sort =False)['total_precio_costo'].sum().reset_index()
# F4 x años
f4_x_años = f4_reservado.groupby(["año", "mes"],sort=False)['total_precio_costo'].sum().reset_index()
f4_x_años["total_precio_costo"] = f4_x_años["total_precio_costo"]/1e6
# F4 acumulado x sede
gb_local = f4_ults.groupby('Local')['total_precio_costo'].sum().reset_index()


# agrega costo a las columnas
def set_columns_f4(base,var):
    item = base[var].unique().tolist()
    for i in item:
        base.loc[base[var] == i, var] = (base.loc[base[var] == i, var] + " " + '${:,.0f} M '.format(base.loc[base[var] == i, "total_precio_costo"].sum()/1e6))

# F4 x semanas

grafica_f4_sem=px.bar(f4_x_semanas, x="Semana (fecha de reserva)", y='total_precio_costo', labels={'total_precio_costo': "Total costo"}, text='total_precio_costo', 
text_auto='.2s', color = 'Local', color_discrete_sequence=px.colors.qualitative.Vivid, title= "Creación F4 dados de baja por semana - 2022")

# F4 x años

ten_creac_x_año = px.bar(f4_x_años,  x="mes", y="total_precio_costo",
            color='año', barmode='group',text_auto=",.0f",labels={"total_precio_costo": "Costo total (Millones)","mes":"Mes de reserva ", "categoria":"Año" } ,color_discrete_sequence=['rgb(36, 121, 108)','rgb(204, 97, 176)'],title="Tendencia de creación F4 dados de baja según mes de reserva")
ten_creac_x_año.update_layout(legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.1))

# F4 acumulado x sede 
fig_torta_local = px.pie(gb_local, values='total_precio_costo', names='Local', title='F4 acumulado por sede')
fig_torta_local.update_traces( textposition='inside', textinfo='percent+label')


## ------ Output 
# TODO guardar figuras en una carpeta para cada corte
fig_torta_local.write_image(f"images/{dt_string}_f4_torta.svg", engine='orca') 
ten_creac_x_año.write_image(f"images/{dt_string}_tendencia_creacion_f4_x_años.svg", width = 800, height=450, engine='orca')
grafica_f4_sem.write_image(f"images/{dt_string}_grafica_f4_sem.svg", width = 700, height=500, engine='orca')