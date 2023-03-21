import pandas as pd 
from general import make_tables, set_age
from datetime import datetime
import pytz
from data import var_global, var_f5
dtstring = datetime.now().strftime('%y%m%d')
import numpy as np

class F5():

    fc = None
    f5 = None
    path = None
 
    def __init__(self, fc, f5_name) -> None:
        print("Cargando planilla F5's...")
        self.fecha_corte = fc
        self.f5 = pd.read_csv(var_f5['path_df'] + f5_name + '.csv', sep = ';', dtype = str)
        self.path = f"{var_global['path_cortes']}/{fc}_corte/images/f5"
        self.transform()
        self.set_age()
        self.replace_loc('COD_LOCAL_RECEPCIÓN','NAME_REC')
        self.replace_loc('COD_LOCAL_ENVIO','NAME_SHIP')
        self.group_by()
        self.save_images()

    def transform(self):
        print("Transformando datos...")
        print(self.f5['TRF_ENTRY_DATE'])
        self.f5['TRF_ENTRY_DATE'] = pd.to_datetime(self.f5['TRF_ENTRY_DATE'], format='%Y/%m/%d')
        self.f5['TRF_SHIP_DATE'] = pd.to_datetime(self.f5['TRF_SHIP_DATE'], format='%Y/%m/%d')
        self.f5['TOTAL_COST'] = pd.to_numeric(self.f5['TOTAL_COST'])
        self.f5 = self.f5.loc[self.f5['TRF_ENTRY_DATE'] >= '2022-01-01'].reset_index()

    def replace_loc(self,column,column2):
        condiciones=[(self.f5[column]=='101'),(self.f5[column]=='2000'),(self.f5[column]=='43'),(self.f5[column]=='98'),(self.f5[column]=='131'),
        (self.f5[column]=='183'),(self.f5[column]=='2001'),(self.f5[column]=='72'),(self.f5[column]=='85'),(self.f5[column]=='2002'),(self.f5[column]=='108'),
        (self.f5[column]=='9903'),(self.f5[column]=='35'),(self.f5[column]=='3001'),(self.f5[column]=='182'),(self.f5[column]=='9902'),
        (self.f5[column]=='82'),(self.f5[column]=='9912'),(self.f5[column]=='9921'),(self.f5[column]=='50'),(self.f5[column]=='9965'),(self.f5[column]=='138'),
        (self.f5[column]=='9951'),(self.f5[column]=='123'),(self.f5[column]=='9970'),(self.f5[column]=='3000'),(self.f5[column]=='13'),(self.f5[column]=='19'),
        (self.f5[column]=='3002'),(self.f5[column]=='53'),(self.f5[column]=='93'),(self.f5[column]=='99'),(self.f5[column]=='143'),(self.f5[column]=='30'),
        (self.f5[column]=='36'),(self.f5[column]=='9961'),(self.f5[column]=='9901'),(self.f5[column]=='25'),(self.f5[column]=='45'),(self.f5[column]=='11'),
        (self.f5[column]=='9910'),(self.f5[column]=='56'),(self.f5[column]=='96'),(self.f5[column]=='3004'),(self.f5[column]=='6'),(self.f5[column]=='60'),
        (self.f5[column]=='38'),(self.f5[column]=='3008')]

        opciones=['Tienda Caracoli - Bucaramanga','Tienda Falabella.com','Tienda Santafé - Medellín','Tienda Jardín Plaza - Cali','Tienda El Castillo - Cartagena',
        'Tienda Santafé - Bogotá','CD Falabella Alto Valor','Tienda La Felicidad - Bogotá','Tienda Titán - Bogotá','CD Falabella Rack',
        'Tienda Suba - Bogotá','CD Falabella','Tienda World Trade Center - Cali','DVD Administrativo','Expo Hayuelos','CT Verde',
        'Tienda Hayuelos - Bogotá','Centro de Transferencia Medellín','CD Linea Blanca','Primavera - Villavicencio','Logistica Inversa','Tienda Colina - Bogotá',
        'CD Crate & Barrel','Tienda Unicentro Bogotá','CD FALABELLA Big Ticket','Falabella.com Alterno','Tienda Plaza Central - Bogotá','Tienda Buenavista - Barranquilla',
        'Fotografia DVD','Tienda Galerías - Bogota','Tienda Cacique - Bucaramanga','Administrativo','La Martina El Tesoro - Medellín','Tienda Allegra - Barranquilla',
        'Tienda San Diego - Medellín','BODEGA EXTERNA 1 - SUBA','CD Bogotá','Tienda Fontanar - Chia','Tienda Arkadia - Medellín','Venta Empresa',
        'Bodega MAVESA (Segundas)','Tienda La Carola - Manizales','Tienda Diver Plaza - Bogotá','Entrega Express La Felicidad','Tienda Parque Arboleda - Pereira','Tienda Acqua - Ibagué',
        'Tienda Centro Mayor','Entrega Express WTC']

        self.f5[column2]=np.select(condiciones,opciones)

        
    def set_age(self):
        print('Seteando edades...')
        self.f5['DIAS_CREACION'] = (self.f5['TRF_ENTRY_DATE'].max() - self.f5['TRF_ENTRY_DATE'])
        self.f5['DIAS_CREACION'] = self.f5['DIAS_CREACION'].apply(lambda x :x.days)
        self.f5['DIAS_ENVIO'] = (self.f5['TRF_ENTRY_DATE'].max() - self.f5['TRF_SHIP_DATE'])
        self.f5['DIAS_ENVIO'] = self.f5['DIAS_ENVIO'].apply(lambda x :x.days)

        self.f5.loc[self.f5['DIAS_CREACION'] <30, 'age'] = 'Menor a 30' 
        self.f5.loc[(self.f5['DIAS_CREACION'] >= 30) & (self.f5['DIAS_CREACION']<=60), 'age'] ='31 a 60'
        self.f5.loc[(self.f5['DIAS_CREACION'] > 60) & (self.f5['DIAS_CREACION']<=90), 'age'] ='61 a 90'
        self.f5.loc[(self.f5['DIAS_CREACION'] > 90) & (self.f5['DIAS_CREACION']<=120), 'age'] ='91 a 120'
        self.f5.loc[(self.f5['DIAS_CREACION'] > 120)&(self.f5['DIAS_CREACION']<=180), 'age']='121 a 180'
        self.f5.loc[(self.f5['DIAS_CREACION'] > 180), 'age'] ='Mayor a 181'

        self.f5.loc[self.f5['DIAS_ENVIO'] <30, 'age'] = 'Menor a 30' 
        self.f5.loc[(self.f5['DIAS_ENVIO'] >= 30) & (self.f5['DIAS_ENVIO']<=60), 'age'] ='31 a 60'
        self.f5.loc[(self.f5['DIAS_ENVIO'] > 60) & (self.f5['DIAS_ENVIO']<=90), 'age'] ='61 a 90'
        self.f5.loc[(self.f5['DIAS_ENVIO'] > 90) & (self.f5['DIAS_ENVIO']<=120), 'age'] ='91 a 120'
        self.f5.loc[(self.f5['DIAS_ENVIO'] > 120)&(self.f5['DIAS_ENVIO']<=180), 'age']='121 a 180'
        self.f5.loc[(self.f5['DIAS_ENVIO'] > 180), 'age'] ='Mayor a 181'
        self.f5.rename(columns={'estado_kpi':'Estado'}, inplace=True)

    def group_by(self):
        print('Generando tablas...')
        f5_2 = self.f5.groupby(['age','Estado'])['TOTAL_COST'].sum().reset_index()
        f5_list = self.f5.loc[self.f5['Estado'] == 'Enviado'].groupby(['NAME_REC'])['TOTAL_COST'].sum().sort_values(ascending = False).reset_index()['NAME_REC'][0:10]
        self.f5_env = self.f5.loc[(self.f5['Estado'] == 'Enviado') & (self.f5['NAME_REC'].isin(f5_list))]
        self.f5_env.rename(columns={'NAME_REC' : 'Local que recibe'}, inplace=True)

        f5_list = self.f5.loc[self.f5['Estado'] == 'Reservado'].groupby(['NAME_SHIP'])['TOTAL_COST'].sum().sort_values(ascending = False).reset_index()['NAME_SHIP'][0:10]
        self.f5_res = self.f5.loc[(self.f5['Estado'] == 'Reservado') & (self.f5['NAME_SHIP'].isin(f5_list))]
        self.f5_res.rename(columns={'NAME_SHIP' : 'Local que envia'}, inplace=True)

        self.tb_env = make_tables(self.f5_env, 'Local que recibe', 'age', 'TOTAL_COST' ,'f5', types = 'ant')
        self.tb_res = make_tables(self.f5_res, 'Local que envia', 'age', 'TOTAL_COST' , 'f5',types = 'ant')
        self.tabla_gral = make_tables(f5_2,'Estado', 'age', 'TOTAL_COST', types = 'ant')
    
    def save_images(self):
        print('Guardando tablas...')
        self.tabla_gral.write_image(f'{self.path}/antiguedad_f5.jpg', width=1000, height=800, engine='orca')
        self.tb_res.write_image(f'{self.path}/antiguedad_res.jpg', width= 2000, height=700, engine='orca')
        self.tb_env.write_image(f'{self.path}/antiguedad_env.jpg', width= 2000, height=700, engine='orca')
    