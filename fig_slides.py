# Libraries
import pandas as pd
import plotly.express as px
from   datetime import date, timedelta, datetime
import plotly.graph_objects as go
import numpy as np
pd.set_option('display.max_columns', 500)
dt_string = datetime.now().strftime('%y%m%d')

## ------ Variables 
# TODO cargar archivos f3, f4, f11
f11 = pd.read_excel('input/220322_f11.xlsx', dtype=str, sheet_name='DB')

## ------ Trasform 
# TODO transformar variables 

# Dates 
f11['FECHA_CREACION'] = pd.to_datetime(f11['FECHA_CREACION'], format='%Y-%m-%d')
f11['MES'] = f11['FECHA_CREACION'].dt.strftime('%b-%y')

# Numbers 
f11['TOTAL_COSTO'] = pd.to_numeric(f11['TOTAL_COSTO'])

# Text

## ------ Filters 
# TODO realizar filtrol a los dataframes
f11_empresa = f11.loc[f11.PROPIETARIO == 'EMPRESA'].reset_index(drop=True)
f11_empresa = f11_empresa.loc[f11_empresa.ESTADO.isin(['Despachado','Espera Retiro Clte.','Ingresado','Entrega parcial'])].reset_index(drop=True)
f11_empresa = f11_empresa.sort_values('FECHA_CREACION')

print(f'Estados de F11 encontrados: {f11_empresa.ESTADO.unique()}')

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

## ------ Output 
# TODO guardar figuras en una carpeta para cada corte 
