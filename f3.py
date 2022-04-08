import pandas as pd
import plotly.express as px
from   datetime import timedelta, datetime
from calendar import monthrange
from general import generate_structure,  set_columns_sum, unif_colors, ord_mes,ord_num,set_columns_nunique
import constants as const
from data import var_f3
pd.set_option('display.max_columns', 500)

class F3():

    dt_string = datetime.now().strftime('%y%m%d')
    mes_1= '2022-02-28' # calculo de 30 días atras
    def __init__(self) -> None:
       self.f3=pd.read_csv(var_f3['path_df'], sep=';', dtype=object)
       self.f3_tendencia = pd.read_excel('input/tendencias_f3.xlsx', dtype=str, sheet_name='f3')
       self.path = generate_structure('f3')
       self.transform()
       self.set_local_agg()
       self.filters()
       self.make_groupby()
    #    self.save_graf()

    def transform(self):
        self.f3[var_f3['costo']] = pd.to_numeric(self.f3[var_f3['costo']])
        self.f3[var_f3['local']] = pd.to_numeric(self.f3[var_f3['local']])
        fechas = [var_f3['fecha_res'], var_f3['fecha_envio'], var_f3['fecha_anulacion'],var_f3['fecha_confirmacion']]
        self.f3.loc[:, fechas] = self.f3[fechas].apply(lambda x: x.replace(['ene', 'abr', 'ago', 'dic'], ['jan', 'apr', 'aug', 'dec'], regex=True))
        for i in fechas:self.f3[i] = pd.to_datetime(self.f3[i], format='%d-%b-%Y')
        self.f3['mes'] = self.f3[var_f3['fecha_res']].dt.strftime('%b-%y')
        self.f3 = self.f3.sort_values(var_f3['fecha_res'])
        self.f3[var_f3['tipo_producto']] = self.f3[var_f3['tipo_producto']].str.capitalize()
        self.f3_tendencia['costo'] = pd.to_numeric(self.f3_tendencia['costo'])
        self.f3_tendencia['fecha ptt'] = pd.to_datetime(self.f3_tendencia['fecha ptt'], format='%Y-%m-%d')
        self.f3_tendencia["costo"] = self.f3_tendencia["costo"].apply(lambda x : f'{round(x/1e6):.0f}') 
        self.f3_tendencia['costo'] = pd.to_numeric(self.f3_tendencia['costo'])
        
    def set_local_agg(self):
        self.f3.loc[self.f3.local.isin(const.tienda), 'local_agg'] = 'TIENDA'
        self.f3.loc[self.f3.local.isin(const.cd), 'local_agg'] = 'CD'
        self.f3.loc[self.f3.local_agg.isna(), 'local_agg'] = 'OTROS'

    def filters(self):
        self.f3_2021 = self.f3.loc[self.f3[var_f3['fecha_res']]>='2021-01-01'].reset_index(drop = True)
        self.f3_abierto = self.f3.loc[self.f3[var_f3['estado']].isin(['enviado','reservado'])].reset_index(drop = True)
        self.f3_ab_pr_mkp = self.f3_abierto.loc[self.f3_abierto[var_f3['tipo_producto']].isin(['Producto','Market place'])].reset_index(drop = True)
        self.f3_mayor_30 = self.f3_ab_pr_mkp.loc[self.f3_ab_pr_mkp[var_f3['fecha_res']] <= self.mes_1].reset_index(drop = True)
        self.f3_ab_mkp = self.f3_abierto.loc[self.f3_abierto[var_f3['tipo_producto']] =='Market place'].reset_index(drop = True)
        self.f3_ab_pr_mkp.loc[self.f3_ab_pr_mkp[var_f3['fecha_res']] <= self.mes_1,'mayor a 30'] = 'y'
        self.f3_ab_pr_mkp.loc[self.f3_ab_pr_mkp['mayor a 30'].isna(),'mayor a 30'] = 'n'
        self.tend_prod = self.f3_tendencia.loc[self.f3_tendencia["tipo producto"] == "producto"]
        self.tend_mkp = self.f3_tendencia.loc[self.f3_tendencia["tipo producto"] == "mkp"]
    
    def make_groupby(self):
        grupo_F3_prd_mkp = self.f3_ab_pr_mkp.groupby([var_f3['tipo_producto'],'mes','mayor a 30'], sort =False)[var_f3['costo']].sum().reset_index()
        grupo_F3_prd_mkp_num = self.f3_ab_pr_mkp.groupby([var_f3['tipo_producto'],'mes','mayor a 30'], sort =False)[var_f3['f3_id']].nunique().reset_index()

        mkp_sede = self.f3_ab_mkp.groupby(['local_agg','mes'], sort = False )[var_f3['costo']].sum().reset_index()
        mkp_sede_num = self.f3_ab_mkp.groupby(['local_agg','mes'], sort = False )[var_f3['f3_id']].nunique().reset_index()

        set_columns_sum(mkp_sede, 'local_agg',var_f3['costo'])
        set_columns_sum(mkp_sede, 'mes',var_f3['costo'])
        set_columns_nunique(mkp_sede_num, 'local_agg', var_f3['f3_id'])
        set_columns_nunique(mkp_sede_num, 'local_agg', var_f3['f3_id'])
        
        self.graf_mkp_sede = self.grap_mkp_x_sede(mkp_sede,var_f3['costo'])
        self.graf_mkp_sede_num = self.grap_mkp_x_sede(mkp_sede_num,var_f3['f3_id'])

        self.graf_f3_prd_mkp_num =self.calc_datos_grap_f3_ab(grupo_F3_prd_mkp_num,var_f3['f3_id'])
        self.graf_f3_prd_mkp_cost = self.calc_datos_grap_f3_ab(grupo_F3_prd_mkp,var_f3['costo'])
        self.calc_tend()
        self.graf_tend_mkp = self.grap_tend("mkp")
        self.graf_tend_prod = self.grap_tend()
       

    def calc_datos_grap_f3_ab(self,df,column):
        if column ==   var_f3['costo']:
            f3_mkp_3m = ('{:,.0f} M '.format(df.loc[(df[var_f3['tipo_producto']]=='Market place') & (df['mayor a 30']=='y'), column].sum()/1e6))
            f3_prd_3m = ('{:,.0f} M '.format(df.loc[(df[var_f3['tipo_producto']]=='Producto') & (df['mayor a 30']=='y'), column].sum()/1e6))
            f3_total_3m = ('{:,.0f} M '.format(df.loc[(df['mayor a 30']=='y'),column].sum()/1e6))
            set_columns_sum(df, var_f3['tipo_producto'],column)
            set_columns_sum(df, 'mes',column)
            titulo = f'F3 abiertos según fecha de reserva - Total ${round(df[column].sum()/1e6):,.0f}M'
            
        if column ==  var_f3['f3_id']:
            f3_mkp_3m =df.loc[(df[var_f3['tipo_producto']]=='Market place') & (df['mayor a 30']=='y'), column].sum()
            f3_prd_3m = df.loc[(df[var_f3['tipo_producto']]=='Producto') & (df['mayor a 30']=='y'), column].sum()
            f3_total_3m = df.loc[(df['mayor a 30']=='y'),column].sum()
            set_columns_nunique(df, var_f3['tipo_producto'],column)
            set_columns_nunique(df, 'mes',column)
            titulo = f'F3 abiertos según fecha de reserva - Total {df[column].sum()}'

        orden = ord_num(df,var_f3['tipo_producto'],column)
        
        return self.grap_f3_ab(df,orden,column,f3_total_3m,f3_mkp_3m,f3_prd_3m,titulo)

    def grap_f3_ab(self,grupo_F3_prd_mkp,orden,axes_y,f3_total_3m,f3_mkp_3m,f3_prd_3m, titulo):
        range_y = grupo_F3_prd_mkp[axes_y].max()
        orden_mes = grupo_F3_prd_mkp.mes.unique()
        fig = px.bar(grupo_F3_prd_mkp, x='mes', y=axes_y, labels={'mes':'Mes de reserva', var_f3['costo']: 'Costo promedio', var_f3['tipo_producto']:'Tipo producto'}, 
        text=axes_y, text_auto='.2s', color = var_f3['tipo_producto'], color_discrete_sequence=['rgb(36, 121, 108)','rgb(204, 97, 176)'], title = titulo, category_orders={var_f3['tipo_producto']:orden, 'mes':orden_mes })
        fig.update_layout(legend=dict(yanchor='top', y=0.98, xanchor='left', x=1))
        fig.add_shape(type='rect',
            xref='paper', yref='paper',
            x0=0, y0=0,
            x1=0.87, y1=1,
            line=dict(
                color='red',
                width=2,
            ))
        fig.add_annotation(x=orden_mes[0], y= (range_y * 15/100) + range_y,
                text= f'Total > 30 días = {f3_total_3m}',
                showarrow=False,
                font = dict (color = 'red',size = 15))
        fig.add_annotation(x=orden_mes[0], y= range_y,
                text= f'Market place > 30 días = {f3_mkp_3m} <br>Producto > 30 días = {f3_prd_3m}',
                showarrow=False,
                font = dict (color = 'red',size = 12))
        fig.update_annotations(align='left')
        return fig
    
    def grap_mkp_x_sede(self,mkp_sede,column):
        if column == var_f3['costo']:
            color = unif_colors(mkp_sede, 'local_agg')
            total = self.f3_ab_mkp[column].sum()/1e6
            fig = px.bar(mkp_sede, x ='mes', y=column, color='local_agg', title=f'F3 Marketplace abiertos por sede - Total costo ${total:,.0f}M', labels={ column:'Costo promedio', 'mes':'Mes de reserva', 'local_agg':'Local'}, text=column,text_auto='.2s', color_discrete_map = color )  
            fig.update_layout(legend=dict(yanchor='top', y=0.9, xanchor='left', x=0.1))
            fig.update_yaxes(range=[0,4*1e8], constrain='domain')
        elif column == var_f3['f3_id']:
            color = unif_colors(mkp_sede, 'local_agg')
            total = self.f3_ab_mkp[column].nunique()
            fig = px.bar(mkp_sede, x ='mes', y=column, color='local_agg', title=f'F3 Marketplace abiertos por sede - Total {total:,.0f}', labels={ column:'Costo promedio', 'mes':'Mes de reserva', 'local_agg':'Local'}, text=column,text_auto='.s', color_discrete_map = color )  
            fig.update_layout(legend=dict(yanchor='top', y=0.9, xanchor='left', x=0.1))
            fig.update_yaxes(range=[0,1100], constrain='domain')
        return fig


    def calc_tend(self):
        grupo_F3_prd_mkp = self.f3_ab_pr_mkp.groupby([var_f3['tipo_producto'],'mes','mayor a 30'], sort =False)[var_f3['costo']].sum().reset_index()
        f3_mkp_3m = pd.to_numeric('{:.0f}'.format(grupo_F3_prd_mkp.loc[(grupo_F3_prd_mkp[var_f3['tipo_producto']]=='Market place'), var_f3["costo"]].sum()/1e6))
        f3_prd_3m = pd.to_numeric('{:.0f}'.format(grupo_F3_prd_mkp.loc[(grupo_F3_prd_mkp[var_f3['tipo_producto']]=='Producto'), var_f3["costo"]].sum()/1e6))
        ult_fecha = self.f3_tendencia["fecha ptt"].max().strftime('%d-%m-%Y')
        ult_mkp_ten = self.f3_tendencia.loc[(self.f3_tendencia["fecha ptt"] == ult_fecha) & (self.f3_tendencia["tipo producto"] == "mkp"),"costo"].item()
        ult_prod_ten = self.f3_tendencia.loc[(self.f3_tendencia["fecha ptt"] == ult_fecha) & (self.f3_tendencia["tipo producto"] == "producto"),"costo"].item()

        if (f3_mkp_3m != ult_mkp_ten) & (f3_prd_3m != ult_prod_ten):
            datos ={
                "tipo producto" : ["producto","mkp"],
                "costo" : [f3_prd_3m,f3_mkp_3m],
                "fecha ptt" : [datetime.now(), datetime.now()]
            }
            df = pd.DataFrame(datos)
            tendencias = pd.concat([self.f3_tendencia,df])
            tendencias.to_excel("input/tendencias_f3.xlsx",index=False)
            self.f3_tendencia = tendencias


    def grap_tend(self,tipo_producto = "producto"): 
        if tipo_producto == "mkp":
            titulo = "Tendencia F3 abierto tipo marketplace según fecha de corte"
            df = self.tend_mkp
        else:
            titulo = "Tendencia F3 abierto tipo producto según fecha de corte"
            df = self.tend_prod
        self.fig = px.line(df, x="fecha ptt", y="costo", labels={'fecha ptt':'Fecha de corte', "costo": "costo promedio (Millones)" },
        text='costo', color_discrete_sequence=['rgb(204, 97, 176)'], title=titulo )
        self.fig.update_layout(legend=dict(yanchor="top", y=1, xanchor="left", x=0.45))
        self.fig.update_traces(textposition="bottom center")
        fecha_max = (df["fecha ptt"].max() + timedelta (days = 5)).strftime('%d-%m-%Y')
        fecha_min = (df["fecha ptt"].min() - timedelta (5)).strftime('%d-%m-%Y')
        self.fig.update_xaxes(range=[fecha_min, fecha_max], constrain="domain")
        return self.fig

    def save_graf(self):
        self.graf_f3_prd_mkp_cost.show()#write_image(f'{self.path}/{self.dt_string}_f3_abiertos_fecha_reserva.svg' ,width=600, height=400)
        self.graf_f3_prd_mkp_num.show()#write_image(f'{self.path}/{self.dt_string}_f3_abiertos_fecha_reserva.svg' ,width=600, height=400)
        self.graf_mkp_sede.show()#write_image(f'{self.path}/{self.dt_string}_f3_abierto_sede.svg',width=600, height=350)
        self.graf_mkp_sede_num.show()#write_image(f'{self.path}/{self.dt_string}_f3_abierto_sede.svg',width=600, height=350)
        self.graf_tend_mkp.show()#grafica_tendencia_f3.write_image(f"images_f3/{dt_string}_f3_tendencia_Producto.svg",width=650, height=400)
        self.graf_tend_prod.show()#grafica_tendencia_f3.write_image(f"images_f3/{dt_string}_f3_tendencia_mkp.svg",width=650, height=400)

f3 = F3()