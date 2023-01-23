import pandas as pd 
from general import make_tables, set_age
from datetime import datetime
import pytz
from data import var_global, var_f5
dtstring = datetime.now().strftime('%y%m%d')

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
        self.group_by()
        self.save_images()

    def transform(self):
        print("Transformando datos...")
        print(self.f5['TRF_ENTRY_DATE'])
        self.f5['TRF_ENTRY_DATE'] = pd.to_datetime(self.f5['TRF_ENTRY_DATE'], format='%Y/%m/%d')
        self.f5['TRF_SHIP_DATE'] = pd.to_datetime(self.f5['TRF_SHIP_DATE'], format='%Y/%m/%d')
        self.f5['TOTAL_COST'] = pd.to_numeric(self.f5['TOTAL_COST'])
        self.f5 = self.f5.loc[self.f5['TRF_ENTRY_DATE'] >= '2022-01-01'].reset_index()
        
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
        f5_list = self.f5.loc[self.f5['Estado'] == 'Enviados'].groupby(['NAME_REC'])['TOTAL_COST'].sum().sort_values(ascending = False).reset_index()['NAME_REC'][0:10]
        self.f5_env = self.f5.loc[(self.f5['Estado'] == 'Enviados') & (self.f5['NAME_REC'].isin(f5_list))]
        self.f5_env.rename(columns={'NAME_REC' : 'Local que recibe'}, inplace=True)

        f5_list = self.f5.loc[self.f5['Estado'] == 'Reservados'].groupby(['NAME_SHIP'])['TOTAL_COST'].sum().sort_values(ascending = False).reset_index()['NAME_SHIP'][0:10]
        self.f5_res = self.f5.loc[(self.f5['Estado'] == 'Reservados') & (self.f5['NAME_SHIP'].isin(f5_list))]
        self.f5_res.rename(columns={'NAME_SHIP' : 'Local que envia'}, inplace=True)

        self.tb_env = make_tables(self.f5_env, 'Local que recibe', 'age', 'TOTAL_COST' , types = 'ant')
        self.tb_res = make_tables(self.f5_res, 'Local que envia', 'age', 'TOTAL_COST' , types = 'ant')
        self.tabla_gral = make_tables(f5_2,'Estado', 'age', 'TOTAL_COST', types = 'ant')
    
    def save_images(self):
        print('Guardando tablas...')
        self.tabla_gral.write_image(f'{self.path}/antiguedad_f5.jpg', width=1000, height=100, engine='orca')
        self.tb_res.write_image(f'{self.path}/antiguedad_res.jpg', width= 2000, height=700, engine='orca')
        self.tb_env.write_image(f'{self.path}/antiguedad_env.jpg', width= 2000, height=700, engine='orca')
    