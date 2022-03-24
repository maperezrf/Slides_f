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
    gb_var = base.groupby(var)['TOTAL_COSTO'].sum().reset_index()
    gb_var.set_index(var, inplace=True)
    for item in lista:
        base.loc[base[var]==item, var] = f'{item} ${round(gb_var.loc[item, "TOTAL_COSTO"]/1e6):,.0f}M'
    return base 

def set_columns_nunique(base, var):    
    lista = base.loc[base[var].notna()][var].unique()
    gb_var = base.groupby(var)['NRO_F11'].sum().reset_index()
    gb_var.set_index(var, inplace=True)
    for item in lista:
        base.loc[base[var]==item, var] = f'{item} {round(gb_var.loc[item, "NRO_F11"]):,.0f}'
    return base 

# F11 

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