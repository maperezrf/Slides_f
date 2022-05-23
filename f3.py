import pandas as pd
import plotly.express as px
from   datetime import timedelta, datetime
from general import set_columns_sum, unif_colors, ord_mes,ord_num,set_columns_nunique
import constants as const
from data import var_f3, var_global
pd.set_option('display.max_columns', 500)

class F3():

    fecha_corte = datetime.now().strftime('%y%m%d')
    f3_ab_mkp = None
    f3_ab_pr_mkp = None
    fecha_corte = None   

    def __init__(self, fr, fc, f3_name) -> None:
       self.fecha_riesgo = fr
       self.fecha_corte = fc
       
       self.f3 = pd.read_csv(var_f3['path_df'] + f3_name + '.csv', sep = ';', dtype = object)
       self.f3_tendencia = pd.read_excel(var_f3['trend_path'], dtype = str)
       self.path = f"{var_global['path_cortes']}/{fc}_corte/images/f3"
       self.transform()
       self.set_local_agg()
       self.filters()
       self.make_groupby()
       self.save_graf()

    def get_path(self):
        return self.path

    def transform(self):
        # F3 planilla
        self.f3[var_f3['costo']] = pd.to_numeric(self.f3[var_f3['costo']])
        fechas = [var_f3['fecha_res'], var_f3['fecha_envio'], var_f3['fecha_anulacion'], var_f3['fecha_confirmacion']]
        self.f3.loc[:, fechas] = self.f3[fechas].apply(lambda x: x.replace(['ene', 'abr', 'ago', 'dic'], ['jan', 'apr', 'aug', 'dec'], regex=True))
        for i in fechas:self.f3[i] = pd.to_datetime(self.f3[i], format = '%d-%b-%Y')
        self.f3['mes_n'] = self.f3[var_f3['fecha_res']].dt.strftime('%m')
        self.f3['mes_n'] = pd.to_numeric(self.f3['mes_n'])
        self.f3['mes'] = self.f3[var_f3['fecha_res']].dt.strftime('%b')
        self.f3 = self.f3.sort_values(var_f3['fecha_res'])
        self.f3[var_f3['tipo_producto']] = self.f3[var_f3['tipo_producto']].str.capitalize()

        # F3 tendencias
        self.f3_tendencia['costo'] = pd.to_numeric(self.f3_tendencia['costo'])
        self.f3_tendencia['fecha ptt'] = pd.to_datetime(self.f3_tendencia['fecha ptt'], format='%Y-%m-%d')

    def set_local_agg(self):
        tienda = []
        cd = []
        for i in range(len(const.tienda)): tienda.append (str(const.tienda[i]))
        for i in range(len(const.cd)): cd.append (str(const.cd[i]))
        self.f3.loc[self.f3.local.isin(tienda), 'local_agg'] = 'TIENDA'
        self.f3.loc[self.f3.local.isin(cd), 'local_agg'] = 'CD'
        self.f3.loc[self.f3.local_agg.isna(), 'local_agg'] = 'OTROS'

    def filters(self):
        self.f3_2021 = self.f3.loc[self.f3[var_f3['fecha_res']] >= var_f3['fecha_inicial']].reset_index(drop = True)  # [x] leer desde var_f3 = fecha_inicial
        self.f3_abierto = self.f3.loc[self.f3[var_f3['estado']].isin(var_f3['abiertos'])].reset_index(drop = True)  # [x] leer desde var_f3 = abiertos
        f3_cerrados = self.f3.loc[self.f3[var_f3['estado']].isin(var_f3['cerrados'])].reset_index(drop = True) # [x] leer desde var_f3 = cerrados        
        self.f3_ab_pr_mkp = self.f3_abierto.loc[self.f3_abierto[var_f3['tipo_producto']].isin(var_f3['tipo_tp'])].reset_index(drop = True)  # [x] leer desde var_f3 = filtro_tp # [x] si es variable global entonces debe ir en el init o en inialización 
        self.f3_ab_mkp = self.f3_abierto.loc[self.f3_abierto[var_f3['tipo_producto']] ==var_f3['tipo_tp'][1]].reset_index(drop = True) # [x] si es variable global entonces debe ir en el init o en inialización 
        self.f3_ab_pr_mkp.loc[self.f3_ab_pr_mkp[var_f3['fecha_res']] <= self.fecha_riesgo,'mayor a 30'] = 'y'
        self.f3_ab_pr_mkp.loc[self.f3_ab_pr_mkp['mayor a 30'].isna(), 'mayor a 30'] = 'n'
        self.set_cortes(f3_cerrados)

    def set_cortes(self, f3_cerrado):
        
        #f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] >= '2021-12-15') & (f3_cerrado['fecha_confirmacion'] <= '2021-12-31') | (f3_cerrado['fecha_anulacion'] >= '2021-12-15') & (f3_cerrado['fecha_anulacion']  <= '2021-12-31'), 'Cortes_cerra'] ='Dic 15 - Dic 31'
        #f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] > '2021-12-31') & (f3_cerrado['fecha_confirmacion']  <= '2022-01-17') | (f3_cerrado['fecha_anulacion'] > '2021-12-31') & (f3_cerrado['fecha_anulacion']  <= '2022-01-17'), 'Cortes_cerra'] ='Dic 31 - Ene 17'
        #f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] > '2022-01-17') & (f3_cerrado['fecha_confirmacion']  <= '2022-01-31') | (f3_cerrado['fecha_anulacion'] > '2022-01-17') & (f3_cerrado['fecha_anulacion']  <= '2022-01-31'), 'Cortes_cerra'] ='Ene 17 - Ene 31'
        #f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] > '2022-01-31') & (f3_cerrado['fecha_confirmacion']  <= '2022-03-01') | (f3_cerrado['fecha_anulacion'] > '2022-01-31') & (f3_cerrado['fecha_anulacion']  <= '2022-03-01'), 'Cortes_cerra'] ='Ene 31 - Mar 01' 
        f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] >= '2022-03-01') & (f3_cerrado['fecha_confirmacion']  < '2022-03-08') | (f3_cerrado['fecha_anulacion'] >= '2022-03-01') & (f3_cerrado['fecha_anulacion']  < '2022-03-08'), 'Cortes_cerra'] = '01-07 Mar'
        f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] >= '2022-03-08') & (f3_cerrado['fecha_confirmacion']  < '2022-03-15') | (f3_cerrado['fecha_anulacion'] >= '2022-03-08') & (f3_cerrado['fecha_anulacion']  < '2022-03-15'), 'Cortes_cerra'] = '08-14 Mar'
        f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] >= '2022-03-15') & (f3_cerrado['fecha_confirmacion']  < '2022-03-22') | (f3_cerrado['fecha_anulacion'] >= '2022-03-15') & (f3_cerrado['fecha_anulacion']  < '2022-03-22'), 'Cortes_cerra'] = '15-21 Mar'
        f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] >= '2022-03-22') & (f3_cerrado['fecha_confirmacion']  < '2022-03-29') | (f3_cerrado['fecha_anulacion'] >= '2022-03-22') & (f3_cerrado['fecha_anulacion']  < '2022-03-29'), 'Cortes_cerra'] = '22-28 Mar'
        f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] >= '2022-03-29') & (f3_cerrado['fecha_confirmacion']  < '2022-04-05') | (f3_cerrado['fecha_anulacion'] >= '2022-03-29') & (f3_cerrado['fecha_anulacion']  < '2022-04-05'), 'Cortes_cerra'] = '29-04 Abr'
        f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] >= '2022-04-05') & (f3_cerrado['fecha_confirmacion']  < '2022-04-12') | (f3_cerrado['fecha_anulacion'] >= '2022-04-05') & (f3_cerrado['fecha_anulacion']  < '2022-04-12'), 'Cortes_cerra'] = '05-11 Abr'
        f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] >= '2022-04-12') & (f3_cerrado['fecha_confirmacion']  < '2022-04-19') | (f3_cerrado['fecha_anulacion'] >= '2022-04-12') & (f3_cerrado['fecha_anulacion']  < '2022-04-19'), 'Cortes_cerra'] = '12-18 Abr'
        f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] >= '2022-04-19') & (f3_cerrado['fecha_confirmacion']  < '2022-04-26') | (f3_cerrado['fecha_anulacion'] >= '2022-04-19') & (f3_cerrado['fecha_anulacion']  < '2022-04-26'), 'Cortes_cerra'] = '19-25 Abr'
        f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] >= '2022-04-26') & (f3_cerrado['fecha_confirmacion']  < '2022-05-03') | (f3_cerrado['fecha_anulacion'] >= '2022-04-26') & (f3_cerrado['fecha_anulacion']  < '2022-05-03'), 'Cortes_cerra'] = '26-02 May' 
        f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] >= '2022-05-03') & (f3_cerrado['fecha_confirmacion']  < '2022-05-10') | (f3_cerrado['fecha_anulacion'] >= '2022-05-03') & (f3_cerrado['fecha_anulacion']  < '2022-05-10'), 'Cortes_cerra'] = '03-09 May'         
        f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] >= '2022-05-10') & (f3_cerrado['fecha_confirmacion']  < '2022-05-17') | (f3_cerrado['fecha_anulacion'] >= '2022-05-10') & (f3_cerrado['fecha_anulacion']  < '2022-05-17'), 'Cortes_cerra'] = '10-16 May' 
        f3_cerrado.loc[(f3_cerrado['fecha_confirmacion'] >= '2022-05-17') & (f3_cerrado['fecha_confirmacion']  < '2022-05-24') | (f3_cerrado['fecha_anulacion'] >= '2022-05-17') & (f3_cerrado['fecha_anulacion']  < '2022-05-24'), 'Cortes_cerra'] = '17-23 May' 

        self.fig_prd_costo = self.calc_cierres('producto', f3_cerrado, 'costo')
        self.fig_mkp_costo = self.calc_cierres('mkp', f3_cerrado, 'costo')
        self.fig_prd_cantidad = self.calc_cierres('producto', f3_cerrado, 'cantidad')
        self.fig_mkp_cantidad =  self.calc_cierres('mkp', f3_cerrado, 'cantidad') 

    def calc_cierres(self, t_producto, f3_cerrado, tip_group): 
        # TODO pasar a un solo método
        # Validar tipo 
        if t_producto == 'producto':
            df = f3_cerrado.loc[f3_cerrado[var_f3['tipo_producto']] == 'Producto'].reset_index()
            titulo = 'F3 cerrados (Producto)'
        elif t_producto == 'mkp':
            df = f3_cerrado.loc[f3_cerrado[var_f3['tipo_producto']] == 'Market place'].reset_index()
            titulo = 'F3 cerrados (MKP)'

        # Validar value a graficar
        if tip_group == 'costo':
            grup_df = df.groupby([var_f3['estado'], 'Cortes_cerra'], sort = False)[[var_f3['costo']]].sum().reset_index()
            total = grup_df[var_f3['costo']].sum()
            total = '${:,.0f} M '.format(total/1e6)
            titulo = f"{titulo} {total}"
            etiquetas = {'Cortes_cerra':'Cortes de cierre', 'cant*costoprmd': 'Costo promedio', 'descripcion6': 'Estado'}
            set_columns_sum(grup_df, 'Cortes_cerra', var_f3['costo'])
            set_columns_sum(grup_df, var_f3['estado'], var_f3['costo'])
            return self.grap_cortes(grup_df, var_f3['costo'], titulo, etiquetas)
        elif tip_group == 'cantidad':
            grup_df = df.groupby([var_f3['estado'], 'Cortes_cerra'], sort = False)[var_f3['f3_id']].nunique().reset_index()
            total = grup_df[var_f3['f3_id']].sum()
            titulo = f"{titulo} {total}"
            etiquetas = {'Cortes_cerra':'Cortes de cierre', var_f3['f3_id']: 'Cantidad', 'descripcion6': 'Estado' }
            set_columns_nunique(grup_df, 'Cortes_cerra', var_f3['f3_id'])
            set_columns_nunique(grup_df, var_f3['estado'], var_f3['f3_id']) 
            return self.grap_cortes(grup_df, var_f3['f3_id'], titulo, etiquetas) 

    def make_groupby(self):
        grupo_F3_prd_mkp = self.f3_ab_pr_mkp.groupby([var_f3['tipo_producto'],'mes','mayor a 30'], sort = False)[var_f3['costo']].sum().reset_index()
        grupo_F3_prd_mkp_num = self.f3_ab_pr_mkp.groupby([var_f3['tipo_producto'],'mes','mayor a 30'], sort = False)[var_f3['f3_id']].nunique().reset_index()

        mkp_sede = self.f3_ab_mkp.groupby(['local_agg','mes'], sort = False )[var_f3['costo']].sum().reset_index()
        mkp_sede_num = self.f3_ab_mkp.groupby(['local_agg','mes'], sort = False )[var_f3['f3_id']].nunique().reset_index()

        set_columns_sum(mkp_sede, 'local_agg',var_f3['costo'])
        set_columns_sum(mkp_sede, 'mes',var_f3['costo'])
        set_columns_nunique(mkp_sede_num, 'local_agg', var_f3['f3_id'])
        set_columns_nunique(mkp_sede_num, 'local_agg', var_f3['f3_id'])
        
        self.graf_mkp_sede = self.grap_mkp_x_sede(mkp_sede, var_f3['costo'])
        self.graf_mkp_sede_num = self.grap_mkp_x_sede(mkp_sede_num, var_f3['f3_id'])

        self.graf_f3_prd_mkp_num = self.calc_datos_grap_f3_ab(grupo_F3_prd_mkp_num, var_f3['f3_id'])
        self.graf_f3_prd_mkp_cost = self.calc_datos_grap_f3_ab(grupo_F3_prd_mkp, var_f3['costo'])
        self.calc_tend()
        self.graf_tend_mkp = self.grap_tend('mkp')
        self.graf_tend_prod = self.grap_tend()
       
    def calc_datos_grap_f3_ab(self, df, column):
        if column ==   var_f3['costo']: # Gráfica para costo 
            f3_mkp_3m = ('{:,.0f} M '.format(df.loc[(df[var_f3['tipo_producto']] == 'Market place') & (df['mayor a 30'] == 'y'), column].sum()/1e6))
            f3_prd_3m = ('{:,.0f} M '.format(df.loc[(df[var_f3['tipo_producto']] == 'Producto') & (df['mayor a 30'] == 'y'), column].sum()/1e6))
            f3_total_3m = ('{:,.0f} M '.format(df.loc[(df['mayor a 30'] == 'y'), column].sum()/1e6))
            set_columns_sum(df, var_f3['tipo_producto'], column)
            set_columns_sum(df, 'mes',column)
            titulo = f'F3 abiertos - Total ${round(df[column].sum()/1e6):,.0f}M'
        if column ==  var_f3['f3_id']: # Gráfica para cantidad
            f3_mkp_3m = df.loc[(df[var_f3['tipo_producto']] == 'Market place') & (df['mayor a 30'] == 'y'), column].sum()
            f3_prd_3m = df.loc[(df[var_f3['tipo_producto']] == 'Producto') & (df['mayor a 30'] == 'y'), column].sum()
            f3_total_3m = df.loc[(df['mayor a 30'] == 'y'), column].sum()
            set_columns_nunique(df, var_f3['tipo_producto'], column)
            set_columns_nunique(df, 'mes',column)
            titulo = f'F3 abiertos - Total {df[column].sum()}'
        orden = ord_num(df,var_f3['tipo_producto'],column)
        return self.grap_f3_ab(df, orden, column, f3_total_3m, f3_mkp_3m, f3_prd_3m, titulo)

    def calc_tend(self):
        grupo_F3_prd_mkp = self.f3_ab_pr_mkp.groupby([var_f3['tipo_producto'], 'mes', 'mayor a 30'],  sort = False)[var_f3['costo']].sum().reset_index()
        f3_mkp_3m = pd.to_numeric('{:.0f}'.format(grupo_F3_prd_mkp.loc[(grupo_F3_prd_mkp[var_f3['tipo_producto']] == 'Market place'), var_f3['costo']].sum()/1e6))
        f3_prd_3m = pd.to_numeric('{:.0f}'.format(grupo_F3_prd_mkp.loc[(grupo_F3_prd_mkp[var_f3['tipo_producto']] == 'Producto'), var_f3['costo']].sum()/1e6))
        ult_fecha = self.f3_tendencia['fecha ptt'].max()
        ult_mkp_ten = self.f3_tendencia.loc[(self.f3_tendencia['fecha ptt'] == ult_fecha) & (self.f3_tendencia['tipo producto'] == 'mkp'), 'costo'].item()
        ult_prod_ten = self.f3_tendencia.loc[(self.f3_tendencia['fecha ptt'] == ult_fecha) & (self.f3_tendencia['tipo producto'] == 'producto'), 'costo'].item()

        if (f3_mkp_3m != ult_mkp_ten) & (f3_prd_3m != ult_prod_ten):
            datos = {
                'tipo producto' : ['producto', 'mkp'],
                'costo' : [f3_prd_3m, f3_mkp_3m], 
                'fecha ptt' : [datetime.now(), datetime.now()]
            }
            df = pd.DataFrame(datos)
            tendencias = pd.concat([self.f3_tendencia, df])
            tendencias.to_excel(var_f3['trend_path'],index=False)
            self.f3_tendencia = tendencias

    # Gráficas 
    def grap_cortes(self, df, column, titulo, etiquetas):
        orden_y = ord_mes(df, 'Cortes_cerra', "f3")
        orden_x = ord_num(df, var_f3['estado'],column)
        graf_F3_cerr_prd = px.bar(df, x='Cortes_cerra', y=column, labels = etiquetas, text = column, text_auto='.2s',  category_orders={var_f3['estado']:orden_x,
            "Cortes_cerra":orden_y}, color = 'descripcion6', color_discrete_sequence=['rgb(118, 78, 159)','rgb(218, 165, 27)'], title = titulo)
        graf_F3_cerr_prd.update_layout(legend = dict(yanchor = "bottom", xanchor = "left", orientation = "h", y = 1))
        graf_F3_cerr_prd.update_yaxes(range = [0, df[column].max() + (df[column].max() * 0.25)], constrain ='domain')
        graf_F3_cerr_prd.update_layout(font=dict(size = 14))   
        graf_F3_cerr_prd.update_layout(margin_r=20, margin_t=60)
        return graf_F3_cerr_prd

    def grap_f3_ab(self, grupo_F3_prd_mkp, orden, axes_y, f3_total_3m, f3_mkp_3m, f3_prd_3m, titulo):
        range_y = grupo_F3_prd_mkp[axes_y].max()
        orden_mes = grupo_F3_prd_mkp.mes.unique()
        fig = px.bar(grupo_F3_prd_mkp, x = 'mes', y = axes_y, labels = {'mes':'Mes de reserva', var_f3['costo']: 'Costo promedio', var_f3['tipo_producto']:'Tipo producto'}, 
            text = axes_y, text_auto = '.2s', color = var_f3['tipo_producto'], color_discrete_sequence = ['rgb(36, 121, 108)','rgb(204, 97, 176)'], title = titulo, 
            category_orders = {var_f3['tipo_producto']:orden, 'mes':orden_mes })
        fig.update_layout(legend = dict(orientation = "h", yanchor = "bottom", xanchor = "right",x = 1,y = 1))
        fig.update_layout(font=dict(size = 14))   
        fig.update_layout(margin_r=20, margin_t=60)
        fig.add_shape(type = 'rect', xref = 'paper', yref = 'paper', x0 = 0, y0 = 0, x1 = 0.82, y1 = 1, line = dict(color = 'red', width = 2))
        fig.add_annotation(x = orden_mes[0], y = (range_y * 60/100) + range_y, text = f'Total > 30 días = {f3_total_3m}', showarrow = False, font = dict (color = 'red',size = 14))
        fig.add_annotation(x = orden_mes[0], y = range_y + (range_y * 35/100), text = f'Producto > 30 días = {f3_prd_3m} <br>Market place > 30 días = {f3_mkp_3m}', 
            showarrow = False, font = dict (color = 'red',size = 14))
        fig.update_annotations(align = 'left')
        fig.update_yaxes(range = [0,grupo_F3_prd_mkp[axes_y].max() + (grupo_F3_prd_mkp[axes_y].max() * 0.7)], constrain = 'domain')
        return fig
    
    def grap_mkp_x_sede(self, mkp_sede, column):
        if column == var_f3['costo']:
            color = unif_colors(mkp_sede, 'local_agg')
            total = self.f3_ab_mkp[column].sum()/1e6
            fig = px.bar(mkp_sede, x = 'mes', y = column, color = 'local_agg', title = f'F3 Marketplace abiertos - Total costo ${total:,.0f}M', 
                labels = { column:'Costo promedio', 'mes':'Mes de reserva', 'local_agg':'Local'}, text = column,text_auto = '.2s', color_discrete_map = color )  
            fig.update_layout(legend = dict(yanchor ='top', y=0.9, xanchor = 'left', x = 0.1))
            fig.update_yaxes(range = [0,6*1e8], constrain='domain')
            fig.update_layout(margin_r=20, margin_t=60)
        elif column == var_f3['f3_id']:
            color = unif_colors(mkp_sede, 'local_agg')
            total = self.f3_ab_mkp[column].nunique()
            fig = px.bar(mkp_sede, x = 'mes', y = column, color = 'local_agg', title = f'F3 Marketplace abiertos - Total {total:,.0f}', 
                labels = { column:'Costo promedio', 'mes':'Mes de reserva', 'local_agg':'Local'}, text = column,text_auto = '.s', color_discrete_map = color )  
            fig.update_layout(legend = dict(yanchor = 'top', y = 0.9, xanchor = 'left', x=0.1))
            fig.update_yaxes(range = [0,1100], constrain = 'domain')
            fig.update_layout(margin_r=20, margin_t=60)
        fig.update_layout(font=dict(size=14))
        return fig

    def grap_tend(self, tipo_producto = 'producto'): 
        trend = self.f3_tendencia.loc[self.f3_tendencia['fecha ptt'] >= '2022-03-01']
        tend_prod = trend.loc[trend['tipo producto'] == 'producto']
        tend_mkp = trend.loc[trend['tipo producto'] == 'mkp']
        if tipo_producto == 'mkp':
            titulo = 'Tendencia F3 abierto tipo marketplace'
            df = tend_mkp
        else:
            titulo = 'Tendencia F3 abierto tipo producto'
            df = tend_prod
        
        fig = px.line(df, x='fecha ptt', y = 'costo', labels = {'fecha ptt':'Fecha de corte', 'costo': 'Costo promedio (Millones)' },
        text = 'costo', color_discrete_sequence = ['rgb(204, 97, 176)'], title = titulo )
        fig.update_layout(legend = dict(yanchor = 'top', y = 1, xanchor ='left', x = 0.45))
        fig.update_layout(font=dict(size=14))
        fig.update_traces(textposition = 'bottom center')
        fig.update_layout(margin_r=20, margin_t=60)
        fecha_max = (df['fecha ptt'].max() + timedelta (days = 5)).strftime('%d-%m-%Y')
        fecha_min = (df['fecha ptt'].min() - timedelta (5)).strftime('%d-%m-%Y')
        fig.update_xaxes(range = [fecha_min, fecha_max], constrain = 'domain')
        return fig

    # Saving graphs 
    def save_graf(self): 
        # Graphs x cost
        self.graf_f3_prd_mkp_cost.write_image(f'{self.path}/{self.fecha_corte}_f3_abiertos_fecha_reserva.png' ,width=600, height=400, engine='orca')
        self.graf_mkp_sede.write_image(f'{self.path}/{self.fecha_corte}_f3_abierto_sede.png',width=600, height=400, engine='orca')
        self.graf_tend_mkp.write_image(f'{self.path}/{self.fecha_corte}_f3_tendencia_mkp.png',width=500, height=400, engine='orca')
        self.graf_tend_prod.write_image(f'{self.path}/{self.fecha_corte}_f3_tendencia_Producto.png',width=500, height=400, engine='orca')
        self.fig_prd_costo.write_image(f'{self.path}/{self.fecha_corte}_f3_cerrado_producto_costo.png',width=500, height=400, engine='orca')
        self.fig_mkp_costo.write_image(f'{self.path}/{self.fecha_corte}_f3_cerrado_mkp_costo.png',width=500, height=400, engine='orca')

        # Graphs x cant
        self.graf_f3_prd_mkp_num.write_image(f'{self.path}/{self.fecha_corte}_f3_abiertos_fecha_reserva_cant.png' ,width=600, height=350, engine='orca')
        self.graf_mkp_sede_num.write_image(f'{self.path}/{self.fecha_corte}_f3_abierto_sede_cant.png',width=600, height=350, engine='orca')
        self.fig_prd_cantidad.write_image(f'{self.path}/{self.fecha_corte}_f3_cerrado_prodcuto_cantidad.png',width=500, height=350, engine='orca')
        self.fig_mkp_cantidad.write_image(f'{self.path}/{self.fecha_corte}_f3_cerrado_mkp_cantidad.png',width=500, height=350, engine='orca')
        print('Se guardaron las imgs!')