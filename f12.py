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
        self.NS=pd.read_csv('input\Sabana_NS.csv', sep = ';', dtype = object)
        self.NS1=self.NS[['NFOLIO', 'METODO_DE_DESPACHO']]
        self.transform()
        self.set_age_f12()
        self.make_table()
        # self.group_by()
        self.save_images()
        
    def transform(self):
        print("Transformando datos...")
        self.f12['Fecha Pactada'] = pd.to_datetime(self.f12['Fecha Pactada'], format='%d/%m/%Y')
        self.f12['Importe Total'] = pd.to_numeric(self.f12['Importe Total'])
        self.f12 = self.f12.loc[self.f12['Fecha Pactada'] >= '2022-01-01'].reset_index()
        self.f12.loc[self.f12['Fecha Pactada'].notna(), 'mes_creacion'] = self.f12.loc[self.f12['Fecha Pactada'].notna(), 'Fecha Pactada'].apply(lambda  x : x.strftime('%b'))
        self.f12=pd.merge(self.f12,self.NS1,how="left", left_on=['Nro. F12'], right_on=['NFOLIO'])
        self.f12.loc[(self.f12["Sector Reparto"]=="40") , "Metodo"] = "SITE TO STORE"
        self.f12.loc[(self.f12["Sector Reparto"]!="40") , "Metodo"] = "HOME DELIVERY"
        self.f12.loc[(self.f12["METODO_DE_DESPACHO"]=="PICK UP IN STORE") , "Metodo"] = "PICK UP IN STORE"
    
    def set_age_f12(self):
        print('Seteando edades...')
        self.f12['DIAS'] = (datetime.now() - self.f12['Fecha Pactada'])
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
        f12_digitadoHD = f12_ab.loc[(f12_ab['Estado'] == 'DIGITADO') & (f12_ab['Metodo'] == 'HOME DELIVERY')]
        f12_digitadoPS = f12_ab.loc[(f12_ab['Estado'] == 'DIGITADO') & (f12_ab['Metodo'] == 'PICK UP IN STORE')]
        f12_digitadoSS = f12_ab.loc[(f12_ab['Estado'] == 'DIGITADO') & (f12_ab['Metodo'] == 'SITE TO STORE')]
        f12_rutaHD = f12_ab.loc[(f12_ab['Estado'] == 'EN RUTA') & (f12_ab['Metodo'] == 'HOME DELIVERY')]
        f12_rutaPS = f12_ab.loc[(f12_ab['Estado'] == 'EN RUTA') & (f12_ab['Metodo'] == 'PICK UP IN STORE')]
        f12_rutaSS = f12_ab.loc[(f12_ab['Estado'] == 'EN RUTA') & (f12_ab['Metodo'] == 'SITE TO STORE')]

        self.tabla_estado = make_tables(f12_ab,'Estado', 'age', 'Importe Total', types = 'ant' )
        self.tabla_estadoER = make_tables(f12_digitado,'Metodo', 'age', 'Importe Total', types = 'ant' )
        self.tabla_estadoDG = make_tables(f12_ruta,'Metodo', 'age', 'Importe Total', types = 'ant' )

        self.tabla_digitadoHD = make_tables(f12_digitadoHD, 'Local abastecimiento', 'age', 'Importe Total', types = 'ant' )
        self.tabla_digitadoPS = make_tables(f12_digitadoPS, 'Local abastecimiento', 'age', 'Importe Total', types = 'ant' )
        self.tabla_digitadoSS = make_tables(f12_digitadoSS, 'Local abastecimiento', 'age', 'Importe Total', types = 'ant' )
        
        self.tabla_rutaHD = make_tables(f12_rutaHD, 'Local abastecimiento', 'age', 'Importe Total', types = 'ant' )
        self.tabla_rutaPS = make_tables(f12_rutaPS, 'Local abastecimiento', 'age', 'Importe Total', types = 'ant' )
        self.tabla_rutaSS = make_tables(f12_rutaSS, 'Local abastecimiento', 'age', 'Importe Total', types = 'ant' )
        

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
        self.tabla_estadoER.write_image(f'{self.path}/tb_estadosER.png',width=1800, height=400, engine='orca')
        self.tabla_estadoDG.write_image(f'{self.path}/tb_estadosDG.png',width=1800, height=400, engine='orca')

        self.tabla_rutaHD.write_image(f'{self.path}/tb_rutaHD.png',width = 1800, height=1500, engine='orca')
        self.tabla_rutaPS.write_image(f'{self.path}/tb_rutaPS.png',width = 1800, height=1500, engine='orca')
        self.tabla_rutaSS.write_image(f'{self.path}/tb_rutaSS.png',width = 1800, height=1500, engine='orca')

        self.tabla_digitadoHD.write_image(f'{self.path}/tb_digitadoHD.png',width= 1800, height=1500, engine='orca')
        self.tabla_digitadoPS.write_image(f'{self.path}/tb_digitadoPS.png',width= 1800, height=1500, engine='orca')
        self.tabla_digitadoSS.write_image(f'{self.path}/tb_digitadoSS.png',width= 1800, height=1500, engine='orca')
        # self.make_pie().write_image(f'{self.path}/pie.png',width=400, height=400, engine='orca')
        # self.make_bar().write_image(f'{self.path}/meses.png',width=800, height=400, engine='orca')