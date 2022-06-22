# Libraries
import pandas as pd
import plotly.express as px
from   datetime import datetime
from data import var_f11, var_global
from general import set_columns_nunique, set_columns_sum, make_tables
import plotly.graph_objects as go

class F11():
    
    # Constants
    dt_string = datetime.now().strftime('%y%m%d')
    mes = ['Jan-21','Feb-21','Mar-21','Apr-21','May-21','Jun-21','Jul-21','Aug-21','Sep-21','Oct-21','Nov-21','Dec-21', 'Jan-22', 'Feb-22', 'Mar-22'] # Editar esta lista cada vez 
    rango_fechas = []
    f11_tcosto  = None
    f11_tm90_costo  = None
    f11_tcant = None
    f11_tm90_cant = None 

    def __init__(self, frango, fcorte, f11_name) -> None:
        self.rango_fechas = frango
        self.f11 = pd.read_csv(var_f11['path_df'] + f11_name + '.csv', dtype='object', sep=';')
        self.path = f"{var_global['path_cortes']}/{fcorte}_corte/images/f11"
        self.transform()
        self.f11 = self.f11.sort_values(var_f11['fech_creacion'])
        self.set_antiguedad()
        self.f11_rf = self.f11_filters() # F11 con todos los filtros iniciales
        self.f11_m90 = self.fltr_riesgo(self.f11_rf) # F11 empresa abiertos mayores a 90 días de creados
        self.print_numbers()

    def get_max_trend_date(self):
        self.load_trend_files()
        return pd.to_datetime(self.f11_tcosto[var_f11['fecha_corte']], format='%Y-%m-%d').max()

    def get_f11(self):
        return self.f11_rf

    def get_f11_m90(self):
        return self.f11_m90

    ## ------ Trasform 
    def transform(self):
        # Dates 
        self.f11[var_f11['fech_creacion']] = pd.to_datetime(self.f11[var_f11['fech_creacion']], format='%Y-%m-%d')
        self.f11[var_f11['mes']] = self.f11[var_f11['fech_creacion']].dt.strftime('%b-%y')
        # Numbers 
        self.f11[var_f11['costo']] = pd.to_numeric(self.f11[var_f11['costo']])
        self.f11[var_f11['dias']]= pd.to_numeric(self.f11[var_f11['dias']])
        # Text

    ## ------ Filters
    def f11_filters(self):
        f11_initial = fltr_fecha_desde(self.f11)
        f11_empresa = fltr_empresa(f11_initial)
        f11_st_rf12 = fltr_tipo_f11(f11_empresa)
        f11_emp_abiertos = fltr_abiertos(f11_st_rf12)
        return f11_emp_abiertos

    def set_antiguedad(self):
        self.f11.loc[self.f11['DIAS'] <30, 'age'] = 'Menor a 30' 
        self.f11.loc[(self.f11['DIAS']>=30)&(self.f11['DIAS']<=60), 'age'] ='30 a 60'
        self.f11.loc[(self.f11['DIAS']>=60)&(self.f11['DIAS']<=90), 'age'] ='61 a 90'
        self.f11.loc[(self.f11['DIAS']>=90)&(self.f11['DIAS']<=120), 'age'] ='91 a 120'
        self.f11.loc[(self.f11['DIAS']>=120)&(self.f11['DIAS']<=180), 'age'] ='121 a 180'
        self.f11.loc[(self.f11['DIAS']>=181), 'age'] = 'Mayor a 181'

    def fltr_riesgo(self, df):
        return df.loc[df[var_f11['mes']].isin(self.mes)].reset_index(drop=True) # TODO mejorar estructura

    def load_trend_files(self):
        self.f11_tcosto = pd.read_excel(var_f11['trend_path'], sheet_name='f11_abiertos_costo')
        self.f11_tm90_costo = pd.read_excel(var_f11['trend_path'], sheet_name='f11_abiertos_m90_costo')
        self.f11_tcant = pd.read_excel(var_f11['trend_path'], sheet_name='f11_abiertos_cant')
        self.f11_tm90_cant = pd.read_excel(var_f11['trend_path'], sheet_name='f11_abiertos_m90_cant')

    def get_f11_cutoff(self):
        print('Generando agrupaciones ... ')
        gb_f11_gm = self.f11_rf.groupby([var_f11['grupo'], var_f11['mes']], sort=False)[var_f11['costo']].sum().reset_index()
        gb_f11_gm_m90 = self.f11_m90.groupby([var_f11['grupo'], var_f11['mes']])[var_f11['costo']].sum().reset_index()
        gb_f11_gm_cant = self.f11_rf.groupby([var_f11['grupo'], var_f11['mes']], sort=False)[var_f11['f11_id']].nunique().reset_index()
        gb_f11_gm_m90_cant = self.f11_m90.groupby([var_f11['grupo'], var_f11['mes']])[var_f11['f11_id']].nunique().reset_index()

        print('Estableciendo nueva fecha de corte ... ')
        gb_f11_gm = set_fecha_corte(gb_f11_gm)
        gb_f11_gm_m90 = set_fecha_corte(gb_f11_gm_m90)
        gb_f11_gm_cant = set_fecha_corte(gb_f11_gm_cant)
        gb_f11_gm_m90_cant = set_fecha_corte(gb_f11_gm_m90_cant)

        print('Concatenando corte a histórico ...')
        self.f11_tcosto = pd.concat([self.f11_tcosto, gb_f11_gm], axis=0)
        self.f11_tm90_costo = pd.concat([self.f11_tm90_costo, gb_f11_gm_m90], axis=0)
        self.f11_tcant = pd.concat([self.f11_tcant, gb_f11_gm_cant], axis=0)
        self.f11_tm90_cant = pd.concat([self.f11_tm90_cant, gb_f11_gm_m90_cant], axis=0)

        print('Transformando datos ... ')
        # Transform 
        self.f11_tcosto = transform_df_trend(self.f11_tcosto, var_f11['costo'])
        self.f11_tm90_costo = transform_df_trend(self.f11_tm90_costo, var_f11['costo'])
        self.f11_tcant = transform_df_trend(self.f11_tcant, var_f11['f11_id'])
        self.f11_tm90_cant = transform_df_trend(self.f11_tm90_cant, var_f11['f11_id'])

        print('Guardando análisis del corte!')
        writer = pd.ExcelWriter(var_f11['trend_path'], engine='xlsxwriter')
        self.f11_tcosto.to_excel(writer, sheet_name='f11_abiertos_costo', index=False)
        self.f11_tm90_costo.to_excel(writer, sheet_name='f11_abiertos_m90_costo', index=False)
        self.f11_tcant.to_excel(writer, sheet_name='f11_abiertos_cant', index=False)
        self.f11_tm90_cant.to_excel(writer, sheet_name='f11_abiertos_m90_cant', index=False)
        writer.save()
        print('Hecho!')

    def tendencias(self):
        self.load_trend_files()
        self.get_tendencias_costo()
        self.get_tendencias_cantidad()

    def print_numbers(self):
        
        print(f'Propietario de f11: {self.f11_rf[var_f11["propietario"]].unique()}')
        print(f'Tipos de F11 encontrados: {self.f11_rf[var_f11["servicio"]].unique()}')
        print(f'Estados de F11 encontrados: {self.f11_rf[var_f11["estado"]].unique()}')
        print(self.f11_rf.groupby([var_f11['grupo']], sort=False)[var_f11['costo']].sum().sort_values(ascending=False))

    def f11_resfil(self):
        # Gráfica para costo
        gb_f11_gm = self.f11_rf.groupby([var_f11['grupo'], var_f11['mes']], sort=False)[var_f11['costo']].sum().reset_index() # TODO repetido 
        gb_f11_gm = set_columns_sum(gb_f11_gm, var_f11['mes'],var_f11['costo'])
        gb_f11_gm = set_columns_sum(gb_f11_gm, var_f11['grupo'],var_f11['costo'])
        orden_grupo = gb_f11_gm.groupby([var_f11['grupo']], sort=False)[var_f11['costo']].sum().sort_values(ascending=False).reset_index()[var_f11['grupo']].to_list()
        orden_mes = gb_f11_gm[var_f11['mes']].unique().tolist()
        total_abierto = gb_f11_gm[var_f11['costo']].sum()
        gb_f11_3m_grupo = self.f11_m90.groupby(var_f11['grupo'])[var_f11['costo']].sum().reset_index().set_index(var_f11['grupo']) # Calcula los totales de costo por grupo 
        self.fig_f11_costo(gb_f11_gm, gb_f11_3m_grupo, orden_grupo, orden_mes, total_abierto)

        # Gráfica por cantidad 
        gb_f11_gm_cant = self.f11_rf.groupby([var_f11['grupo'], var_f11['mes']], sort=False)[var_f11['f11_id']].nunique().reset_index() # TODO repetido
        gb_f11_gm_cant = set_columns_nunique(gb_f11_gm_cant, var_f11['mes'],var_f11['f11_id'])
        gb_f11_gm_cant = set_columns_nunique(gb_f11_gm_cant, var_f11['grupo'],var_f11['f11_id'])
        orden_grupo_cant = gb_f11_gm_cant.groupby([var_f11['grupo']], sort=False)[var_f11['f11_id']].sum().sort_values(ascending=False).reset_index()[var_f11['grupo']].to_list()
        orden_mes_cant = gb_f11_gm_cant[var_f11['mes']].unique().tolist()
        total_abierto_cant = gb_f11_gm_cant[var_f11['f11_id']].sum()
        gb_f11_3m_cant_grupo = self.f11_m90.groupby(var_f11['grupo'])[var_f11['f11_id']].nunique().reset_index().set_index(var_f11['grupo']) # Calcula los totales de costo por grupo 
        self.fig_f11_cantidad(gb_f11_gm_cant, gb_f11_3m_cant_grupo, orden_grupo_cant, orden_mes_cant, total_abierto_cant)
        
        #Generación tablas 
        f11_initial = fltr_fecha_desde(self.f11)
        f11_abiertos = fltr_abiertos(f11_initial)
        f11_empresa = fltr_empresa(f11_abiertos)
        f11_cliente = fltr_cliente(f11_abiertos)
        f11_emp_cd = f11_empresa.loc[f11_empresa[var_f11['grupo']] == 'CD']
        f11_emp_no_cd = f11_empresa.loc[~f11_empresa[var_f11['grupo']].isin(['CD', 'BODEGA PRODUCTO EN PROCESO'])]
        f11_cl_cd = f11_cliente.loc[f11_cliente[var_f11['grupo']] == 'CD']
        f11_cl_no_cd = f11_cliente.loc[~f11_cliente[var_f11['grupo']].isin(['CD', 'BODEGA PRODUCTO EN PROCESO'])]
        self.generate_tables(f11_empresa,f11_cliente,f11_emp_cd,f11_emp_no_cd,f11_cl_no_cd,f11_cl_cd)

    def fig_f11_costo(self, df, gb_annotations, orden_grupo, orden_mes, ta):
        f11_empresa_sede = px.bar(df, x=var_f11['mes'], y=var_f11['costo'], color=var_f11['grupo'], text=var_f11['costo'], text_auto='.2s', category_orders={var_f11['grupo']:orden_grupo, var_f11['mes']:orden_mes})
        f11_empresa_sede.update_layout(barmode='stack',title_text=f"F11s empresa abiertos por sede - Total abierto {ta/1e6:,.0f}M") #,uniformtext=dict(mode="hide", minsize=10),legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.1))
        f11_empresa_sede.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="right", x=0.5))
        f11_empresa_sede.update_layout(font=dict(size=14))

        f11_empresa_sede.add_shape(type="rect",xref="paper", yref="paper",x0=0, y0=0,x1=0.83, y1=0.8,line=dict(color="red", width=2,))
        mes_ref = orden_mes[0] 
        f11_empresa_sede.add_annotation(x=mes_ref, y=0.9*1e9, text= f"Total > 90 días = {gb_annotations.sum()[0]/1e6:,.0f}M", showarrow=False, font = dict (color = "red",size = 17), xanchor='left') # TODO Estas líneas pueden agrupar, en un solo add_annotation, utilizando <br>, y se alinea mejor utilizando fig.update_annotations(align="left") 
        f11_empresa_sede.add_annotation(x=mes_ref, y=0.8*1e9, text= f"CD = {gb_annotations.loc['CD'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 14), xanchor='left')
        f11_empresa_sede.add_annotation(x=mes_ref, y=0.7*1e9, text= f"TIENDAS = {gb_annotations.loc['TIENDAS'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 14), xanchor='left')
        f11_empresa_sede.add_annotation(x=mes_ref, y=0.6*1e9, text= f"BODEGA PRODUCTO EN PROCESO = {gb_annotations.loc['BODEGA PRODUCTO EN PROCESO'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 14), xanchor='left')
        f11_empresa_sede.add_annotation(x=mes_ref, y=0.5*1e9, text= f"DVD ADMINISTRATIVO = {gb_annotations.loc['DVD ADMINISTRATIVO'][0]/1e6:,.0f}M",showarrow=False,font = dict (color = "red",size = 14), xanchor='left')

        f11_empresa_sede.layout.yaxis.title.text='Total costo promedio'
        f11_empresa_sede.layout.xaxis.title.text='Mes de creación'
        f11_empresa_sede.write_image(f"{self.path}/{self.dt_string}_f11_empresa_abiertos_sede_monto.svg",scale=1, height=800,width=850, engine='orca')
        
    def fig_f11_cantidad(self, df, gb_annotations, orden_grupo, orden_mes, ta):
        f11_es_cantidad = px.bar(df, x=var_f11['mes'], y=var_f11['f11_id'], color=var_f11['grupo'], text=var_f11['f11_id'], text_auto='.0f', category_orders={var_f11['grupo']:orden_grupo, var_f11['mes']:orden_mes})
        f11_es_cantidad.update_layout(barmode='stack',title_text=f"F11s empresa abiertos por sede - Total abierto {ta:,.0f} folios de F11" ) #,uniformtext=dict(mode="hide", minsize=10),legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.1))
        f11_es_cantidad.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="right", x=0.5))
        f11_es_cantidad.update_layout(font=dict(size=14))

        f11_es_cantidad.add_shape(type="rect",xref="paper", yref="paper",x0=0, y0=0,x1=0.83, y1=0.8,line=dict(color="red", width=2,))
        mes_ref = orden_mes[0]
        f11_es_cantidad.add_annotation(x=mes_ref, y=1200, text= f"Total > 90 días = {gb_annotations.sum()[0]:,.0f} folios", showarrow=False, font = dict (color = "red",size = 17), xanchor='left') # TODO igual que en la lina 88
        f11_es_cantidad.add_annotation(x=mes_ref, y=1000,text= f"CD = {gb_annotations.loc['CD'][0]:,.0f} folios",showarrow=False,font = dict (color = "red",size = 14), xanchor='left')
        f11_es_cantidad.add_annotation(x=mes_ref, y=900,text= f"TIENDAS = {gb_annotations.loc['TIENDAS'][0]:,.0f} folios",showarrow=False,font = dict (color = "red",size = 14), xanchor='left')
        f11_es_cantidad.add_annotation(x=mes_ref, y=800,text= f"BODEGA PRODUCTO EN PROCESO = {gb_annotations.loc['BODEGA PRODUCTO EN PROCESO'][0]:,.0f} folios",showarrow=False,font = dict (color = "red",size = 14), xanchor='left')
        f11_es_cantidad.add_annotation(x=mes_ref, y=700,text= f"DVD ADMINISTRATIVO = {gb_annotations.loc['DVD ADMINISTRATIVO'][0]:,.0f} folios",showarrow=False,font = dict (color = "red",size = 14), xanchor='left')

        f11_es_cantidad.layout.yaxis.title.text='Cantidad de folios de F11'
        f11_es_cantidad.layout.xaxis.title.text='Mes de creación'
        f11_es_cantidad.write_image(F"{self.path}/{self.dt_string}_f11_empresa_abiertos_sede_cantidad.svg",scale=1, height=800,width=850, engine='orca')

    def generate_tables(self,f11_empresa,f11_cliente,f11_emp_cd,f11_emp_no_cd,f11_cl_no_cd,f11_cl_cd):
        tb_emp_gen = make_tables(f11_empresa,'SERVICIO','GRUPO','TOTAL_COSTO')
        tb_cl_gen = make_tables(f11_cliente,'SERVICIO','GRUPO','TOTAL_COSTO')
        tb_emp_gen_ant = make_tables(f11_empresa,'SERVICIO','age','TOTAL_COSTO','ant')
        tb_cl_gen_ant = make_tables(f11_cliente,'SERVICIO','age','TOTAL_COSTO','ant')
        tb_emp_cd = make_tables(f11_emp_cd,'SERVICIO','age','TOTAL_COSTO','ant')
        tb_emp_no_cd = make_tables(f11_emp_no_cd.sort_values('DIAS',ascending=True),'SERVICIO','age','TOTAL_COSTO','ant')
        tb_cl_no_cd = make_tables(f11_cl_no_cd.sort_values('DIAS',ascending=True),'SERVICIO','age','TOTAL_COSTO','ant')
        tb_cl_cd = make_tables(f11_cl_cd.sort_values('DIAS',ascending=True),'SERVICIO','age','TOTAL_COSTO','ant')

        tb_emp_gen.write_image(f'{self.path}/{self.dt_string}tb_emp_gral.png',height = 265, width = 1100, engine='orca')
        tb_cl_gen.write_image(f'{self.path}/{self.dt_string}tb_cl_gral.png',height = 265, width = 1100, engine='orca')
        tb_emp_cd.write_image(f'{self.path}/{self.dt_string}tb_emp_cd.png',height = 265, width = 1000, engine='orca')
        tb_emp_no_cd.write_image(f'{self.path}/{self.dt_string}tb_emp_no_cd.png',height = 265, width = 1000, engine='orca')
        tb_cl_no_cd.write_image(f'{self.path}/{self.dt_string}tb_cl_no_cd.png',height = 265, width = 1000, engine='orca')
        tb_cl_cd.write_image(f'{self.path}/{self.dt_string}tb_cl_cd.png',height = 265, width = 1000, engine='orca')
        tb_emp_gen_ant.write_image(f'{self.path}/{self.dt_string}tb_emp_ant.png',height = 265, width = 1000, engine='orca')
        tb_cl_gen_ant.write_image(f'{self.path}/{self.dt_string}tb_cl_ant.png',height = 265, width = 1000, engine='orca')

    # ---------------- Trend methods 
    def get_tendencias_costo(self):
        # Total flujo 
        tcd = self.f11_tcosto.loc[self.f11_tcosto[var_f11['grupo']]=='CD']
        ttienda = self.f11_tcosto.loc[(self.f11_tcosto[var_f11['grupo']]=='TIENDAS')|(self.f11_tcosto[var_f11['grupo']]=='DVD ADMINISTRATIVO')]

        gb_tcd = tcd.groupby([var_f11['fecha_corte']])[var_f11['costo']].sum().reset_index()
        gb_ttienda = ttienda.groupby([var_f11['fecha_corte']])[var_f11['costo']].sum().reset_index()

        self.fig_f11_trend_costo(gb_tcd, 'CD', ['rgb(204, 97, 176)'])
        self.fig_f11_trend_costo(gb_ttienda, 'Tiendas & DVD', ['rgb(36, 121, 108)'])

        # Mayores a 90 días 
        tm90_cd = self.f11_tm90_costo.loc[self.f11_tm90_costo[var_f11['grupo']]=='CD']
        tm90_tienda = self.f11_tm90_costo.loc[(self.f11_tm90_costo[var_f11['grupo']]=='TIENDAS')|(self.f11_tm90_costo[var_f11['grupo']]=='DVD ADMINISTRATIVO')]

        gb_tm90_cd = tm90_cd.groupby([var_f11['fecha_corte']])[var_f11['costo']].sum().reset_index()
        gb_tm90_tienda = tm90_tienda.groupby([var_f11['fecha_corte']])[var_f11['costo']].sum().reset_index()

        self.fig_f11_trend_costo(gb_tm90_cd, 'CD mayores a 90 días', ['rgb(204, 97, 176)'])
        self.fig_f11_trend_costo(gb_tm90_tienda, 'Tiendas & DVD mayores a 90 días', ['rgb(36, 121, 108)'])

    def fig_f11_trend_costo(self, df, local, color):
        df[var_f11['costo']] = round(df[var_f11['costo']]/1e6)
        fig_f11_cd_trend = px.line(df, x=var_f11['fecha_corte'], y=var_f11['costo'], labels={var_f11['fecha_corte']:'Fecha de corte', 
        var_f11['costo']: "Costo total (Millones)" }, text=var_f11['costo'], color_discrete_sequence=color, 
        title=f"F11 abiertos {local}" )
        fig_f11_cd_trend.update_layout(legend=dict(yanchor="top", y=1, xanchor="left", x=0.45))
        fig_f11_cd_trend.update_traces(textposition="bottom right")
        fig_f11_cd_trend.update_xaxes(range=self.rango_fechas, constrain="domain")
        fig_f11_cd_trend.update_layout(font=dict(size=14))
        # nuevos 
        fig_f11_cd_trend.update_layout(margin_r=20, margin_t=60)
        fig_f11_cd_trend.write_image(f"{self.path}/{self.dt_string}_f11_trend_{local}.svg",width=550, height=400, engine='orca')

    def get_tendencias_cantidad(self):
        # Cantidad 
        self.f11_tcant = transform_df_trend(self.f11_tcant, var_f11['f11_id'])
        
        tcd = self.f11_tcant.loc[self.f11_tcant[var_f11['grupo']]=='CD']
        ttienda = self.f11_tcant.loc[(self.f11_tcant[var_f11['grupo']]=='TIENDAS')|(self.f11_tcant[var_f11['grupo']]=='DVD ADMINISTRATIVO')]

        gb_tcd = tcd.groupby([var_f11['fecha_corte']])[var_f11['f11_id']].sum().reset_index()
        gb_ttienda = ttienda.groupby([var_f11['fecha_corte']])[var_f11['f11_id']].sum().reset_index()

        self.fig_f11_trend_cantidad(gb_tcd, 'CD', ['rgb(204, 97, 176)'])
        self.fig_f11_trend_cantidad(gb_ttienda, 'Tiendas & DVD', ['rgb(36, 121, 108)'])

        # Cantidad 90 días 
        self.f11_tm90_cant = transform_df_trend(self.f11_tm90_cant, var_f11['f11_id'])

        tm90_cd = self.f11_tm90_cant.loc[self.f11_tm90_cant[var_f11['grupo']]=='CD']
        tm90_tienda = self.f11_tm90_cant.loc[(self.f11_tm90_cant[var_f11['grupo']]=='TIENDAS')|(self.f11_tm90_cant[var_f11['grupo']]=='DVD ADMINISTRATIVO')]

        gb_tm90_cd = tm90_cd.groupby([var_f11['fecha_corte']])[var_f11['f11_id']].sum().reset_index()
        gb_tm90_tienda = tm90_tienda.groupby([var_f11['fecha_corte']])[var_f11['f11_id']].sum().reset_index()

        self.fig_f11_trend_cantidad(gb_tm90_cd, 'CD mayores a 90 días', ['rgb(204, 97, 176)'])
        self.fig_f11_trend_cantidad(gb_tm90_tienda, 'Tiendas & DVD mayores a 90 días', ['rgb(36, 121, 108)'])

    def fig_f11_trend_cantidad(self, df, local, color):
        fig_f11_cd_trend = px.line(df, x=var_f11['fecha_corte'], y=var_f11['f11_id'], labels={var_f11['fecha_corte']:'Fecha de corte', 
        var_f11['f11_id']: "Cantidad de folios F11" }, text=var_f11['f11_id'], color_discrete_sequence=color, 
        title=f"F11 abiertos {local}" )
        fig_f11_cd_trend.update_layout(legend=dict(yanchor="top", y=1, xanchor="left", x=0.45))
        fig_f11_cd_trend.update_traces(textposition="bottom right")
        fig_f11_cd_trend.update_xaxes(range=self.rango_fechas, constrain="domain")
        fig_f11_cd_trend.update_layout(margin_r=20, margin_t=60)
        fig_f11_cd_trend.update_layout(font=dict(size=14))
        fig_f11_cd_trend.write_image(f"{self.path}/{self.dt_string}_f11_tcant_{local}.svg",width=550, height=400, engine='orca')

# General methods 

def fltr_tipo_f11(df):
    return df.loc[df[var_f11['servicio']].isin(var_f11['tipo_f11_x_grafica'])]

def fltr_empresa(df):
    return df.loc[df[var_f11['propietario']] == var_f11['prop_empresa']].reset_index(drop=True)

def fltr_cliente(df):
    return df.loc[df[var_f11['propietario']] == var_f11['prop_cliente']].reset_index(drop=True)

def fltr_abiertos(df):
    return df.loc[df[var_f11['estado']].isin(var_f11['estados_abiertos'])].reset_index(drop=True)
    
def fltr_fecha_desde(df):
    return df.loc[df[var_f11['fech_creacion']] >= var_f11['fecha_inicial']].reset_index(drop=True)

def transform_df_trend(df, value):
    df[value] = pd.to_numeric(df[value])
    df[var_f11['fecha_corte']] = pd.to_datetime(df[var_f11['fecha_corte']], format='%Y-%m-%d')
    return df 

def set_fecha_corte(df, fecha_corte=datetime.now().strftime("%Y-%m-%d")):
    df['FECHA_CORTE']= fecha_corte
    return df