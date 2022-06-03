import pandas as pd
from datetime import datetime
import numpy as np
import constants as const
from data import var_f4, var_global
from f4 import F4
dt_string = datetime.now().strftime('%y%m%d')

pd.options.display.float_format = '${:,.0f}'.format

# A tener en cuenta: 
# TODO 1. Entre método y método solo un espacio de separación 
# TODO 2. cuando hay signo "=" dejar un espacio antes y después  
# TODO 3. cuando vayan "," que queden pegadas a la palabra anterior y con un espacio después 

class CLASSIFIER_F4():

    dt_string = datetime.now().strftime('%y%m%d')
    f4_db_res = None
    f4_db_reg = None
    fecha_corte = None
    f4_clas_marc = None

    def __init__(self, fc, f4_name):
        self.f4 = pd.read_csv(var_f4['path_df'] + f4_name +".csv", sep=';', dtype=str)
        self.fecha_corte = fc
        self.path = f"{var_global['path_cortes']}/{fc}_corte/classifier" #'output/{fc}_corte/classifier'
        self.transform()
        self.set_local_agg()
        self.set_posible_causa()
        self.set_marca()

    # Trasform 
    def transform(self):
        self.f4.total_precio_costo = pd.to_numeric(self.f4.total_precio_costo)
        self.f4.local = pd.to_numeric(self.f4.local)
        self.f4.loc[:, var_f4["fechas"]] = self.f4[var_f4["fechas"]].apply(lambda x: x.replace(["ene", "abr", "ago", "dic"], ["jan", "apr", "aug", "dec"], regex=True))
        for i in var_f4["fechas"]: self.f4[i] = pd.to_datetime(self.f4[i])
        self.f4 = self.f4.sort_values(var_f4['fecha_res'])
        self.f4['mes'] = self.f4[var_f4['fecha_res']].dt.strftime('%b')
        self.f4["mes_creacion"] = self.f4['fecha_creacion'].dt.strftime('%b')
        self.f4['Posible Causa'] = np.nan
        for i in const.fechas_inv:
            self.f4.loc[(self.f4.local == i) & (self.f4.fecha_reserva <= const.fechas_inv[i]),"mes"] = "Inventario"
        
    
    def set_local_agg(self):
        self.f4.loc[self.f4[var_f4["local"]].isin(const.tienda), 'local_agg'] = 'TIENDA'
        self.f4.loc[self.f4[var_f4["local"]].isin(const.cd), 'local_agg'] = 'CD'
        self.f4.loc[self.f4[var_f4["local"]] == 3001, 'local_agg'] = 'DVD ADMINISTRATIVO'
        self.f4.loc[self.f4[var_f4["local"]] == 11, 'local_agg'] = 'VENTA EMPRESA'
        self.f4.loc[self.f4[var_f4["local"]] == 99, 'local_agg'] = 'ADMINISTRATIVO'
        self.f4.loc[self.f4[var_f4["local"]] == 9910, 'local_agg'] = 'BODEGA MAVESA'
        self.f4.loc[self.f4[var_f4["local"]].isna(), 'local_agg'] = 'OTROS'

    def get_f4_tp_res(self):
        return self.f4_tp_res

    def get_f4_classifier(self):
        return self.f4
        
    # Methods 
    def set_posible_causa(self):
        # Filtros para tienda 
        self.f4.loc[((self.f4['Posible Causa'].isna())) & (self.f4[var_f4['f4_id']].isin(const.f4_dup)),'Posible Causa']= 'F4 duplicado generado por CI'
        self.f4.loc[((self.f4['Posible Causa'].isna())) & (self.f4[var_f4['local']]==3000),'Posible Causa']='Conciliación NC 2021 - Local 3000'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='TIENDA') & self.f4[var_f4["destino"]].str.contains(r'pantalla\w? rota\w?|pantalla quebrada| pantalla\w? |pantalla rota'), 'Posible Causa'] = 'Pantallas rotas'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='TIENDA') & (self.f4[var_f4["destino"]].str.contains(r'calidad|cambio|politica|devolucion cliente|danocalida') | self.f4[var_f4['desccentro_e_costo']].str.contains(r'servicio al cliente|servicio cliente|calidad')), 'Posible Causa'] = 'Calidad'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='TIENDA') & (self.f4[var_f4['desccentro_e_costo']].str.contains(r'tester') | self.f4[var_f4["destino"]].str.contains(r'tester|tes ter|muestra')), 'Posible Causa'] = 'Testers' 
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='TIENDA') & (self.f4[var_f4['desccentro_e_costo']].str.contains(r'recupero empresa segurida') | self.f4[var_f4["destino"]].str.contains(r'recupero seguridad')), 'Posible Causa'] = 'Recobro fortox' 
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='TIENDA') & self.f4[var_f4["destino"]].str.contains(r'accidente cliente'), 'Posible Causa'] = 'Accidente cliente'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='TIENDA') & self.f4[var_f4["destino"]].str.contains(r'tapabocas|tapaboca|guantes|guante'), 'Posible Causa'] = 'Insumos bioseguridad'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='TIENDA') & self.f4[var_f4["destino"]].str.contains(r'[1][1]\d{7,}'), 'Posible Causa'] = 'Cierre de F11 - Tienda sin recupero'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='TIENDA') & (self.f4[var_f4["destino"]].str.contains('dano') | self.f4[var_f4["destino"]].str.contains('merma') | self.f4[var_f4["destino"]].str.contains('averia')), 'Posible Causa' ] = 'Avería'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='TIENDA') & ~self.f4[var_f4['desccentro_e_costo']].str.contains(r'servicio al cliente|servicio cliente', na=False), 'Posible Causa'] = 'Avería'

        # Locales DVD, ADMIN y VENTA EMPRESA
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='DVD ADMINISTRATIVO') & (self.f4[var_f4["destino"]].str.contains(r'[1][1]\d{7,}')), 'Posible Causa'] = 'Cierre de F11 - DVD sin recupero'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='ADMINISTRATIVO') & (self.f4[var_f4["destino"]].str.contains(r"cobro a deprisa")), 'Posible Causa'] = 'Recobro a transportadora (Administrativo)'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='ADMINISTRATIVO'), 'Posible Causa'] = 'Avería'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='VENTA EMPRESA'), 'Posible Causa'] = 'Venta empresa' 

        # Filtros para CD
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg == "CD") & self.f4[var_f4["destino"]].str.contains(r'patalla\w?|rota\w?|pantalla quebrada'), 'Posible Causa'] =  'Pantallas rotas'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg == "CD") & self.f4[var_f4["destino"]].str.contains(r'suma'), 'Posible Causa'] = 'Recobro suma'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg == "CD") & self.f4[var_f4["destino"]].str.contains(r'recobro suppla'), 'Posible Causa'] = 'Recobro DHL'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='CD') & (self.f4[var_f4["destino"]].str.contains(r'[1][1]\d{7,} sin recupero|[1][2]\d{7,} sin recupero')), 'Posible Causa'] = 'Cierre de F11 - CD sin recupero'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg == "CD") & self.f4[var_f4["destino"]].str.contains(r'cobro\b.*\d{10}|\d{10}.*cobro\b|recupero'), 'Posible Causa'] = 'Recobro a transportadora'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg == "CD") & self.f4[var_f4["destino"]].str.contains(r'recobro\b.*\d{10}|\d{10}.*recobro\b'), 'Posible Causa'] = 'Recobro a transportadora'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg == "CD") & self.f4[var_f4["destino"]].str.contains(r'recobrado\b.*\d{10}|\d{10}.*recobrado\b'), 'Posible Causa'] = 'Recobro a transportadora'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg == "CD") & (self.f4[var_f4["destino"]] == 'oc importaci inferior a 250 ud'), 'Posible Causa'] = "Avería"
        self.f4.loc[self.f4['Posible Causa'].isna() & self.f4[var_f4["destino"]].str.contains(r'prestamo\w?'), 'Posible Causa'] = 'Prestamo no devuelto'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg =='CD') & (self.f4[var_f4["destino"]].str.contains("baja por danoaveria en dvl")), 'Posible Causa'] = 'DVL'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg == "CD") & self.f4[var_f4["destino"]].str.contains(r'cambio agil'), 'Posible Causa'] = 'Cambio ágil'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg == "CD") & self.f4[var_f4["destino"]].str.contains(r'averias cd dvl'), 'Posible Causa'] = 'Avería'
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg == "CD") & self.f4[var_f4["destino"]].str.contains(r'calidad'), 'Posible Causa'] = 'Avería'

        # revisar 
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg == "CD") & self.f4[var_f4["destino"]].str.contains(r'importacion'), 'Posible Causa'] = "Avería"
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg == "CD") & self.f4[var_f4["destino"]].str.contains(r'destrucc oc inferior usd 250'), 'Posible Causa'] = "Avería"
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg == "CD") & self.f4[var_f4["destino"]].str.contains(r'destruc oc5677206 impo con nc'), 'Posible Causa'] = "Avería"
        self.f4.loc[self.f4['Posible Causa'].isna() & (self.f4.local_agg == "CD") & self.f4[var_f4["destino"]].str.contains(r'destruc oc460039 impo con nc'), 'Posible Causa'] = "Avería"

    def set_marca(self):
        marcas = pd.read_excel(var_f4["marcas_df"], dtype=str)
        marcas.Marca.str.capitalize()
        marcas.drop_duplicates("upc",inplace=True)
        self.f4 = self.f4.merge(marcas, how="left", on="upc") # [x] si f4_clas_marc es variable global entonces debe ir en el init o en inialización 
        self.calc_data_print()

    def calc_data_print(self):
        reg_sin_clasificar = self.f4.loc[(self.f4["Posible Causa"].isna()) & (self.f4[var_f4["tipo_redinv"]] == "dado de baja") & (self.f4[var_f4['estado']] =='reservado')].shape[0]
        reg_clasificados = self.f4.loc[(self.f4["Posible Causa"].notna() & (self.f4[var_f4["tipo_redinv"]] == "dado de baja") & (self.f4[var_f4['estado']] =='reservado'))].shape[0]
        reg_sin_marca = self.f4.loc[self.f4["Marca"].isna(), "upc"].nunique()
        montos_estado = self.f4.groupby([var_f4["estado"]])[[var_f4["costo"]]].sum()/1e6
        montos_estado = montos_estado.reset_index()
        self.registrado = self.f4.loc[self.f4[var_f4["estado"]] == "registrado"].groupby([var_f4["estado"],"fecha_creacion"])[[var_f4["costo"]]].sum()
        self.print_data(reg_clasificados,reg_sin_clasificar,reg_sin_marca,montos_estado)

    def calculos(self):
        reservado = self.f4.loc[(self.f4[var_f4["tipo_redinv"]] == "dado de baja") & (self.f4[var_f4['estado']] =='reservado')].reset_index(drop=True).groupby([var_f4["estado"],"local_agg"])[[var_f4["costo"]]].sum().reset_index()
        cd = '${:,.0f} M '.format(reservado.loc[reservado["local_agg"] == "CD", "total_precio_costo"].item() /1e6)
        tienda = '${:,.0f} M '.format(reservado.loc[reservado["local_agg"] == "TIENDA", "total_precio_costo"].item() /1e6)
        dvd = '${:,.0f} M '.format(reservado.loc[reservado["local_agg"] == "DVD ADMINISTRATIVO", "total_precio_costo"].item() /1e6)
        vent_emp = '${:,.0f} M '.format(reservado.loc[reservado["local_agg"] == "VENTA EMPRESA", "total_precio_costo"].item() /1e6)
        total = '${:,.0f} M '.format(reservado["total_precio_costo"].sum() /1e6)
        return [cd,tienda,dvd,vent_emp,total]

    def print_data(self,reg_clasificados,reg_sin_clasificar,reg_sin_marca,montos_estado):
        print(f"\nCantidad de registros clasificados posible causa: {reg_clasificados}")
        print(f"Cantidad de registros sin clasificar posible causa: {reg_sin_clasificar}")
        print(f"Cantidad de registros sin clasificar marca: {reg_sin_marca}")
        print(f" Montos por estado: {montos_estado}\n")
        self.save_files(reg_sin_marca,reg_sin_clasificar)

    def save_files(self,reg_sin_clasificar,reg_sin_marca):
        self.f4.to_csv(f"{self.path}/{self.fecha_corte}_f4_clasificado.csv",sep=";" , index=False)
        print("Se guardo archivo de F4s clasificado")
        self.f4.loc[(self.f4.local_agg == 'CD') & (self.f4[var_f4["fecha_res"]] < "2022-03-31")].to_csv(f"{self.path}/{self.fecha_corte}_f4_clasificado_CD.csv",sep=";" , index=False)
        self.f4.loc[(self.f4[var_f4["tipo_redinv"]] == "dado de baja") & (self.f4[var_f4['estado']] =='registrado')].reset_index(drop=True) .to_excel(f"{self.path}/{self.fecha_corte}_f4_registrados.xlsx", index=False)
        print("Se guardo archivo de F4s en estado registrado")
        self.f4.to_csv(f"{self.path}/{self.fecha_corte}_f4_clasificado.csv",sep=";" , index=False)
        if reg_sin_marca > 0:
            upc = self.f4.loc[self.f4["Marca"].isna(), "upc"].unique().tolist()
            pd.DataFrame(upc,columns=["UPC"]).to_excel(f"{self.path}/{self.fecha_corte}_UPCs_nuevos.xlsx", index=False)
            print("Se genero un archivo con los UPCs, a los cuales no se asociaron marcas")
        if reg_sin_clasificar > 0:
            self.f4.loc[(self.f4["Posible Causa"].isna()) & (self.f4[var_f4["tipo_redinv"]] == "dado de baja") & (self.f4[var_f4['estado']] =='reservado') ].to_excel(f"{self.path}/{self.fecha_corte}_f4_sin_clasificar.xlsx", index=False)
            print("Se guardo archivo el cual no se clasifico posible causa")


