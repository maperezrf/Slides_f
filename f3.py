import pandas as pd
import plotly.express as px
from   datetime import timedelta, datetime
from calendar import monthrange
from general import generate_structure,  set_columns_sum, unif_colors, ord_mes,ord_num
import constants as const
from data import var_f3
pd.set_option('display.max_columns', 500)

class F3():

    dt_string = datetime.now().strftime('%y%m%d')
    mes_1= '2022-02-28' # calculo de 30 días atras
    def __init__(self) -> None:
       self.f3=pd.read_csv(var_f3['path_df'], sep=";", dtype=object)
       self.path = generate_structure("f3")
       self.transform()
       self.set_local_agg()
       self.filters()
       self.make_groupby()
       self.save_graf()

    def transform(self):
        self.f3[var_f3['costo']] = pd.to_numeric(self.f3[var_f3['costo']])
        fechas = [var_f3['fecha_res'], var_f3['fecha_envio'], var_f3['fecha_anulacion'],var_f3['fecha_confirmacion']]
        self.f3.loc[:, fechas] = self.f3[fechas].apply(lambda x: x.replace(["ene", "abr", "ago", "dic"], ["jan", "apr", "aug", "dec"], regex=True))
        for i in fechas:self.f3[i] = pd.to_datetime(self.f3[i], format='%d-%b-%Y')
        self.f3['mes'] = self.f3[var_f3["fecha_res"]].dt.strftime('%b-%y')
        self.f3 = self.f3.sort_values(var_f3["fecha_res"])
    
    def set_local_agg(self):
        self.f3.loc[self.f3.local.isin(const.tienda), 'local_agg'] = 'TIENDA'
        self.f3.loc[self.f3.local.isin(const.cd), 'local_agg'] = 'CD'
        self.f3.loc[self.f3.local_agg.isna(), 'local_agg'] = 'OTROS'

    def filters(self):
        self.f3_2021 = self.f3.loc[self.f3[var_f3['fecha_res']]>='2021-01-01']
        self.f3_abierto = self.f3.loc[self.f3[var_f3['estado']].isin(['enviado','reservado'])].reset_index()
        self.f3_ab_pr_mkp = self.f3_abierto.loc[self.f3_abierto[var_f3['tipo_producto']].isin(['producto','market place'])]
        self.f3_mayor_90 = self.f3_ab_pr_mkp.loc[self.f3_ab_pr_mkp[var_f3["fecha_res"]] <= self.mes_1]
        self.f3_ab_mkp = self.f3_abierto.loc[self.f3_abierto[var_f3['tipo_producto']] =='market place']
    

    def make_groupby(self):
        grupo_F3_prd_mkp = self.f3_ab_pr_mkp.groupby([var_f3["tipo_producto"],'mes'], sort =False)[var_f3['costo']].sum().reset_index()
        mkp_sede = self.f3_ab_mkp.groupby(['local_agg','mes'], sort=False)[var_f3['costo']].sum().reset_index()

        set_columns_sum(mkp_sede, 'local_agg',var_f3['costo'])
        set_columns_sum(mkp_sede, 'mes',var_f3['costo'])
        set_columns_sum(grupo_F3_prd_mkp, var_f3["tipo_producto"],var_f3['costo'])
        set_columns_sum(grupo_F3_prd_mkp, "mes",var_f3['costo'])
        self.grap_f3_ab(grupo_F3_prd_mkp)
        self.grap_mkp_x_sede(mkp_sede)
    
    def grap_f3_ab(self,grupo_F3_prd_mkp):
        f3_mkp_3m = ('{:,.0f} M '.format(self.f3_mayor_90.loc[self.f3_mayor_90[var_f3["tipo_producto"]]=='market place', var_f3['costo']].sum()/1e6))
        f3_prd_3m = ('{:,.0f} M '.format(self.f3_mayor_90.loc[self.f3_mayor_90[var_f3["tipo_producto"]]=='producto', var_f3['costo']].sum()/1e6))
        f3_total_3m = ('{:,.0f} M '.format(self.f3_mayor_90[var_f3['costo']].sum()/1e6))
        orden = ord_num(grupo_F3_prd_mkp,var_f3["tipo_producto"],var_f3['costo'])
        orden_mes = grupo_F3_prd_mkp.mes.unique()
        self.grafica_F3_prd_mkp = px.bar(grupo_F3_prd_mkp, x="mes", y=var_f3['costo'], labels={'mes':'Mes de reserva', var_f3['costo']: "Costo promedio", var_f3['tipo_producto']:'Tipo producto'}, 
        text=var_f3['costo'], text_auto='.2s', color = var_f3['tipo_producto'], color_discrete_sequence=['rgb(36, 121, 108)','rgb(204, 97, 176)'], title=f"F3 abiertos según fecha de reserva - Total costo ${round(self.f3_ab_pr_mkp[var_f3['costo']].sum()/1e6):,.0f}M",category_orders={var_f3['tipo_producto']:orden, "mes":orden_mes })
        self.grafica_F3_prd_mkp.update_layout(legend=dict(yanchor="top", y=0.98, xanchor="left", x=1))
        self.grafica_F3_prd_mkp.add_shape(type="rect",
            xref="paper", yref="paper",
            x0=0, y0=0,
            x1=0.87, y1=1,
            line=dict(
                color="red",
                width=2,
            ))
        self.grafica_F3_prd_mkp.add_annotation(x=orden_mes[0], y=0.9*1e9,
                text= f"Total > 30 días= {f3_total_3m}",
                showarrow=False,
                font = dict (color = "red",size = 15))
        self.grafica_F3_prd_mkp.add_annotation(x=orden_mes[0], y=0.7*1e9,
                text= f"Market place > 30 días= {f3_mkp_3m} <br>Producto > 30 días= {f3_prd_3m}",
                showarrow=False,
                font = dict (color = "red",size = 12))
        self.grafica_F3_prd_mkp.update_annotations(align="left")
    
    def grap_mkp_x_sede(self,mkp_sede):
        color = unif_colors(mkp_sede, "local_agg")
        total = self.f3_ab_mkp[var_f3['costo']].sum()/1e6
        self.fig_mkp_sede = px.bar(mkp_sede, x ='mes', y=var_f3['costo'], color='local_agg', title=f"F3 Marketplace abiertos por sede - Total costo ${total:,.0f}M",color_discrete_sequence=[ 'rgb(47, 138, 196)','rgb(153, 201, 69)','rgb(165, 170, 153)' ], labels={ var_f3['costo']:'Costo promedio', 'mes':'Mes de reserva', 'local_agg':'Local'}, text=var_f3['costo'],text_auto='.2s', color_discrete_map = color )  
        self.fig_mkp_sede.update_layout(legend=dict(yanchor="top", y=0.9, xanchor="left", x=0.1))
        self.fig_mkp_sede.update_yaxes(range=[0,4*1e8], constrain="domain")

    def save_graf(self):
        self.grafica_F3_prd_mkp.write_image(f'{self.path}/{self.dt_string}_f3_abiertos_fecha_reserva.svg' ,width=600, height=400)
        self.fig_mkp_sede.write_image(f'{self.path}/{self.dt_string}_f3_abierto_sede.svg',width=600, height=350) # 820 , 350 

f3 = F3()