# Libraries
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np
import constants as const
dt_string = datetime.now().strftime('%y%m%d')

# Variables 

f4 = pd.read_csv(f'input/220322_f4.csv', sep=';', dtype=str)
marcas = pd.read_excel("input/Marcas.xlsx", dtype=str)

# Trasform 
marcas.Marca.str.capitalize()
f4.total_precio_costo = pd.to_numeric(f4.total_precio_costo)
fechas = ['fecha_creacion', 'fecha_reserva']
f4.loc[:, fechas] = f4[fechas].apply(lambda x: x.replace(["ene", "abr", "ago", "dic"], ["jan", "apr", "aug", "dec"], regex=True))
for i in fechas: f4[i] = pd.to_datetime(f4[i])
f4 = f4.sort_values("fecha_reserva")
f4['mes'] = f4['fecha_reserva'].dt.strftime('%b')

f4['Posible Causa'] = np.nan
f4.loc[f4.local.isin(const.tienda), 'local_agg'] = 'TIENDA'
f4.loc[f4.local.isin(const.cd), 'local_agg'] = 'CD'
f4.loc[f4.local == "3001", 'local_agg'] = 'DVD ADMINISTRATIVO'
f4.loc[f4.local == "11", 'local_agg'] = 'VENTA EMPRESA'

# Filters
f4_db_res = f4.loc[(f4.tipo_redinv == "dado de baja") & (f4.estado =='reservado') & (f4.fecha_reserva >= "2022-01-01")].reset_index(drop=True)

# Methods 
def classifier():
    # Filtros para tienda 

    f4_db_res.loc[(f4_db_res['Posible Causa'].isna()) & (f4_db_res.local=='3000'),'Posible Causa']='Conciliación NC 2021 - Local 3000'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.tipo_redinv == 'dado de baja') & (f4_db_res.local_agg =='TIENDA') & f4_db_res.destino.str.contains(r'pantalla\w? rota\w?|pantalla quebrada| pantalla\w? |pantalla rota'), 'Posible Causa'] = 'Pantallas rotas'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.tipo_redinv == 'dado de baja') & (f4_db_res.local_agg =='TIENDA') & (f4_db_res.destino.str.contains(r'calidad|cambio|politica|devolucion cliente|danocalida') | f4_db_res.desccentro_e_costo.str.contains(r'servicio al cliente|servicio cliente|calidad')), 'Posible Causa'] = 'Calidad'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.tipo_redinv == 'dado de baja') & (f4_db_res.local_agg =='TIENDA') & (f4_db_res.desccentro_e_costo.str.contains(r'tester') | f4_db_res.destino.str.contains(r'tester|tes ter|muestra')), 'Posible Causa'] = 'Testers' 
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.tipo_redinv == 'dado de baja') & (f4_db_res.local_agg =='TIENDA') & (f4_db_res.desccentro_e_costo.str.contains(r'recupero empresa segurida') | f4_db_res.destino.str.contains(r'recupero seguridad')), 'Posible Causa'] = 'Recobro fortox' 
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.tipo_redinv == 'dado de baja') & (f4_db_res.local_agg =='TIENDA') & f4_db_res.destino.str.contains(r'accidente cliente'), 'Posible Causa'] = 'Accidente cliente'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.tipo_redinv == 'dado de baja') & (f4_db_res.local_agg =='TIENDA') & f4_db_res.destino.str.contains(r'tapabocas|tapaboca|guantes|guante'), 'Posible Causa'] = 'Insumos bioseguridad'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.tipo_redinv == 'dado de baja') & (f4_db_res.local_agg =='TIENDA') & f4_db_res.destino.str.contains(r'[1][1]\d{7,}'), 'Posible Causa'] = 'Cierre de F11 - Tienda'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.tipo_redinv == 'dado de baja') & (f4_db_res.local_agg =='TIENDA') & (f4_db_res.destino.str.contains('dano') | f4_db_res.destino.str.contains('merma') | f4_db_res.destino.str.contains('averia')), 'Posible Causa' ] = 'Avería'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.tipo_redinv == 'dado de baja') & (f4_db_res.local_agg =='TIENDA') & ~f4_db_res.desccentro_e_costo.str.contains(r'servicio al cliente|servicio cliente', na=False), 'Posible Causa'] = 'Avería'

    # Locales DVD, ADMIN y VENTA EMPRESA
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.tipo_redinv == 'dado de baja') & (f4_db_res.local_agg =='DVD ADMINISTRATIVO') & (f4_db_res.destino.str.contains(r'[1][1]\d{7,}')), 'Posible Causa'] = 'Cierre de F11 - DVD'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.tipo_redinv == 'dado de baja') & (f4_db_res.local_agg =='ADMINISTRATIVO'), 'Posible Causa'] = 'Avería'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.tipo_redinv == 'dado de baja') & (f4_db_res.local_agg =='VENTA EMPRESA'), 'Posible Causa'] = 'Venta empresa' 

    # Filtros para CD
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == "CD") & f4_db_res.destino.str.contains(r'patalla\w?|rota\w?|pantalla quebrada'), 'Posible Causa'] =  'Pantallas rotas'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == "CD") & f4_db_res.destino.str.contains(r'recobro suppla'), 'Posible Causa'] = 'Recobro suppla'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == 'CD') & (f4_db_res.tipo_redinv == 'dado de baja')  & (f4_db_res.destino.str.contains(r'[1][1]\d{7,} sin recupero|[1][2]\d{7,} sin recupero')), 'Posible Causa'] = 'Cierre de F11 - CD'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == "CD") & f4_db_res.destino.str.contains(r'cobro\b.*\d{10}|\d{10}.*cobro\b|recupero'), 'Posible Causa'] = 'Recobro a transportadora'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == "CD") & f4_db_res.destino.str.contains(r'recobro\b.*\d{10}|\d{10}.*recobro\b'), 'Posible Causa'] = 'Recobro a transportadora'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == "CD") & f4_db_res.destino.str.contains(r'recobrado\b.*\d{10}|\d{10}.*recobrado\b'), 'Posible Causa'] = 'Recobro a transportadora'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == "CD")& (f4_db_res.destino == 'oc inferiores usd250 recibo'), 'Posible Causa'] = 'Merma importaciones - CD'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & f4_db_res.destino.str.contains(r'prestamo\w?'), 'Posible Causa'] = 'Prestamo no devuelto' # No tiene filtro por local
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == 'CD') & (f4_db_res.tipo_redinv == 'dado de baja')  & (f4_db_res.destino.str.contains("baja por danoaveria en dvl")), 'Posible Causa'] = 'DVL'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == "CD") & f4_db_res.destino.str.contains(r'cambio agil'), 'Posible Causa'] = 'Cambio ágil'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == "CD") & f4_db_res.destino.str.contains(r'averias cd dvl'), 'Posible Causa'] = 'Avería'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == "CD") & f4_db_res.destino.str.contains(r'calidad'), 'Posible Causa'] = 'Avería'

    # revisar 
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == "CD") & f4_db_res.destino.str.contains(r'importacion'), 'Posible Causa'] = 'Merma importaciones - CD'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == "CD") & f4_db_res.destino.str.contains(r'destrucc oc inferior usd 250'), 'Posible Causa'] = 'Merma importaciones - CD'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == "CD") & f4_db_res.destino.str.contains(r'destruc oc5677206 impo con nc'), 'Posible Causa'] = 'Merma importaciones - CD'
    f4_db_res.loc[f4_db_res['Posible Causa'].isna() & (f4_db_res.local_agg == "CD") & f4_db_res.destino.str.contains(r'destruc oc460039 impo con nc'), 'Posible Causa'] = 'Merma importaciones - CD'

def set_marca():
    marcas.drop_duplicates("upc",inplace=True)
    f4_clas_marc = f4_db_res.merge(marcas, how="left", on="upc")
    return f4_clas_marc

classifier()
final = set_marca()
final.to_excel(f"output/{dt_string}_f4_clasificado.xlsx", index=False)
reg_sin_clasificar = final.loc[final["Posible Causa"].isna()].shape[0]
reg_sin_marca = final.loc[final["Marca"].isna(), "upc"].nunique()

# TODO un método para las reglas de tiendas y otro para CD 

# Output 

# TODO imprimir monto y cantidad de f4 según estado, f4 clasificados, f4 sin clasificar

print(f"Cantidad de registros sin clasificar posible causa: {reg_sin_clasificar}")
print(f"Cantidad de registros sin clasificar marca: {reg_sin_marca}")

montos_estado = f4.groupby("estado")["total_precio_costo"].sum()/1e6
montos_estado = montos_estado.reset_index()
print(montos_estado)

if reg_sin_marca > 0:
    upc = final.loc[final["Marca"].isna(), "upc"].unique().tolist()
    pd.DataFrame(upc,columns=["UPC"]).to_excel(f"output/{dt_string}_UPCs_nuevos.xlsx", index=False)
    print("Se genero un archivo con los UPCs, a los cuales no se asociaron marcas")

# TODO guardar f4 en registrado, f4 no clasificados y consolidado nuevo