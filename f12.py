import pandas as pd 
from general import make_tables, set_age, unif_colors,ord_mes, set_antiguedad
from datetime import datetime
import plotly.express as px
from data import var_global, var_f12
dtstring = datetime.now().strftime('%y%m%d')

class F12():

    fc = None
    f12 = None
    path = None

    def __init__(self, fc, f12_name) -> None:
        print("Cargando planilla f12's...")
        self.fecha_corte = fc
        self.f12 = pd.read_csv(var_f12['path_df'] + f12_name + '.csv', sep = ';', dtype = object)
        self.path = f"{var_global['path_cortes']}/{fc}_corte/images/f12"
        self.transform()
        self.set_age_f12()
        self.make_table()
        # self.group_by()
        self.save_images()
        
    def transform(self):
        print("Transformando datos...")
        self.f12['Fecha Estado'] = pd.to_datetime(self.f12['Fecha Estado'], format='%d/%m/%Y')
        self.f12['Importe Total'] = pd.to_numeric(self.f12['Importe Total'])
        self.f12 = self.f12.loc[self.f12['Fecha Estado'] >= '2022-01-01'].reset_index()
        self.f12.loc[self.f12['Fecha Estado'].notna(), 'mes_creacion'] = self.f12.loc[self.f12['Fecha Estado'].notna(), 'Fecha Estado'].apply(lambda  x : x.strftime('%b'))
    
    def set_age_f12(self):
        print('Seteando edades...')
        self.f12['DIAS'] = (self.f12['Fecha Estado'].max() - self.f12['Fecha Estado'])
        self.f12['DIAS'] = self.f12['DIAS'].apply(lambda x :x.days)
        self.f12 = set_antiguedad(self.f12, 'DIAS', 'f11')
        self.f12.rename(columns={'Estado Actual':'Estado'}, inplace=True)
        self.f12.to_excel('f12.xlsx')

    def make_table(self):
        print('Generando tabla...')
        f12_ab = self.f12.loc[self.f12['Estado'].isin(['EN RUTA', 'DIGITADO', 'RESERVADO','CONFIRMADO'])] 
        f12_ab.rename(columns={'Local Abastecedor': 'Local abastecimiento'}, inplace= True)
        f12_digitado = f12_ab.loc[f12_ab['Estado'] == 'DIGITADO']
        f12_ruta = f12_ab.loc[f12_ab['Estado'] == 'EN RUTA']
        self.tabla_estado = make_tables(f12_ab, 'Estado', 'age', 'Importe Total', types = 'ant' )
        self.tabla_ruta = make_tables(f12_ruta, 'Local abastecimiento', 'age', 'Importe Total', types = 'ant' )
        self.tabla_dgitado = make_tables(f12_digitado, 'Local abastecimiento', 'age', 'Importe Total', types = 'ant' )
        

    def make_pie(self):
        self.f12.loc[self.f12['Estado'].isin(['EN RUTA', 'DIGITADO', 'RESERVADO','CONFIRMADO']), 'estado_agg'] = 'Abiertos'
        self.f12.loc[self.f12['Estado'].isna(), 'estado_agg'] = 'Cerrados'
        f12gb = self.f12.groupby('estado_agg')['Importe Total'].sum().reset_index()
        torta_f12 = px.pie(f12gb, values = 'Importe Total', names = 'estado_agg', color = 'estado_agg', color_discrete_map = {'Cerrados':'rgb(51, 102, 102)', 'Abiertos':'rgb(204, 204, 51)'})
        torta_f12.update_traces( textposition ='outside', textinfo = 'percent+label')
        torta_f12.update_layout(font =dict(size = 15), margin=dict(l=0,r=10,b=0) )
        return torta_f12

    def make_bar(self):
        f12_mes = self.f12.groupby(['mes_creacion','estado_agg'])['Importe Total'].sum().reset_index()
        orden = ord_mes(f12_mes,'mes_creacion')
        f12_mes_graf = px.bar(f12_mes.loc[f12_mes['mes_creacion'] == 'Sep'], x = 'mes_creacion', y = 'Importe Total', color='estado_agg', color_discrete_map = {'Cerrados':'rgb(51, 102, 102)', 'Abiertos':'rgb(204, 204, 51)'},category_orders = {'mes_creacion' : orden}
        , text = 'Importe Total', text_auto = '.2s', labels={'mes_creacion': 'Mes', 'Importe Total': 'Costo', 'estado_agg':'Estado agregado' })
        f12_mes_graf.update_layout(legend = dict(yanchor = 'top', y = 0.95, xanchor = 'left', x = 0.7),font =dict(size = 15), margin=dict(l=0,r=10,b=0), yaxis_categoryorder = 'total ascending' )
        return f12_mes_graf

    def save_images(self):
        print('Guardando imagenes')
        self.tabla_estado.write_image(f'{self.path}/tb_estados.png',width=1800, height=400, engine='orca')
        self.tabla_ruta.write_image(f'{self.path}/tb_ruta.png',width = 1800, height=1500, engine='orca')
        self.tabla_dgitado.write_image(f'{self.path}/tb_digitado.png',width= 1800, height=1500, engine='orca'       )
        # self.make_pie().write_image(f'{self.path}/pie.png',width=400, height=400, engine='orca')
        # self.make_bar().write_image(f'{self.path}/meses.png',width=800, height=400, engine='orca')