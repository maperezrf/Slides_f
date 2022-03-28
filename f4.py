import pandas as pd
import plotly.express as px
from   datetime import date, timedelta, datetime
import plotly.graph_objects as go
import numpy as np
import constants as const
from calendar import monthrange
from data import var_f4

pd.set_option('display.max_columns', 500)
dt_string = datetime.now().strftime('%y%m%d')

class F4():

    def __init__(self) -> None:
        self.f4_2022 = pd.read_csv(var_f4["path_df_clas"],sep=";" , dtype = object)
        self.f4_2021 = pd.read_csv("input/f4_2021.csv",sep=";", dtype = object)
        self.f4_21_22()
        self.transform()
        self.filters()
        self.set_week_f4()
        self.make_groupby()
        self.save_grap()

    def f4_21_22(self):
        self.f4_2022["año"] = "2022"
        self.f4_21_22 = pd.concat([self.f4_2021,self.f4_2022])
    
    def transform(self):
        self.f4_21_22[var_f4['costo']] = pd.to_numeric(self.f4_21_22[var_f4['costo']], downcast= 'integer')
        for i in var_f4["fechas"]: self.f4_21_22[i] = pd.to_datetime(self.f4_21_22[i])
        meses_ing = ["Jan", "Apr", "Aug", "Dec"]
        meses_esp = ["Ene", "Abr", "Ago", "Dic"]
        i=0
        for mes in meses_ing:
                self.f4_21_22.loc[self.f4_21_22["mes"] == mes, "mes" ] = meses_esp[i]
                i=i+1
                
    def filters(self):
        self.f4_2021 = self.f4_21_22.loc[self.f4_21_22[var_f4['fecha_res']] >= "2022-01-01" ].reset_index(drop=True)
        self.f4_2021_cd = self.f4_2021.loc[self.f4_2021.local_agg == "CD"].reset_index()
        self.f4_2021_tienda = self.f4_2021.loc[self.f4_2021.local_agg == "TIENDA"].reset_index()
    
    def set_week_f4(self):
        lista_mes = self.f4_2021.mes.unique()
        f_inicio  = datetime.strptime('2022/01/01', '%Y/%m/%d')
        f_cortes = f_inicio
        for mes in enumerate(lista_mes):
            sem = 0
            while f_cortes <= self.f4_2021.loc[self.f4_2021.mes == mes[1], var_f4['fecha_res']].max():
                sem = sem + 1
                f_cortes = f_inicio + timedelta(days = 7)
                if sem == 4:
                    dias = monthrange(2011,mes[0]+1)[1]
                    if dias == 28:
                        pass
                    elif dias == 30:
                        f_cortes = f_cortes + timedelta(days = 2)
                    elif dias == 31:
                        f_cortes = f_cortes + timedelta(days = 3)
                self.f4_2021.loc[(self.f4_2021[var_f4["fecha_res"]] >= f_inicio) & (self.f4_2021[var_f4["fecha_res"]] <= f_cortes), "Semana (fecha de reserva)"] = f"S{sem}{f_cortes.strftime('%b')}"
                f_inicio = f_cortes

    def make_groupby(self):
        f4_x_semanas = self.f4_2021.groupby(["local_agg", "Semana (fecha de reserva)"], sort =False)[var_f4['costo']].sum().reset_index()
        f4_x_años = self.f4_21_22.groupby(["año", "mes"],sort=False)[var_f4['costo']].sum().reset_index()
        f4_x_años[var_f4['costo']] = f4_x_años[var_f4['costo']]/1e6
        gb_local = self.f4_2021.groupby('local_agg')[var_f4['costo']].sum().reset_index()
        gb_f4g_graf_21 = self.f4_2021.groupby(['mes', "Posible Causa", "local_agg"]).agg({var_f4['costo']:"sum"}).reset_index()
        group_total = self.f4_2021.groupby('Posible Causa')[var_f4['costo']].sum().sort_values(ascending=False).reset_index()
        group_local = self.f4_2021.groupby(['Posible Causa',"local_agg"])[var_f4['costo']].sum().sort_values(ascending=False).reset_index()
        group_local= group_local.loc[group_local.local_agg.isin(["TIENDA","CD"])].reset_index()
        group_mes = self.f4_2021.groupby(["mes","local_agg"])[var_f4['costo']].sum().sort_values(ascending=False).reset_index()
        group_mes= group_mes.loc[group_mes.local_agg.isin(["TIENDA","CD"])].reset_index()
        orden_pc = self.f4_2021_tienda.groupby('Posible Causa')[var_f4['costo']].sum().sort_values(ascending=False).head(5).keys()
        gb_f4mespc = self.f4_2021_tienda.groupby(['mes','Posible Causa'])[var_f4['costo']].sum().reset_index()
        gb_f4mespc = gb_f4mespc.loc[gb_f4mespc['Posible Causa'].isin(orden_pc)]
        orden_pc_cd = self.f4_2021_cd.groupby('Posible Causa')[var_f4['costo']].sum().sort_values(ascending=False).head(5).keys()
        gb_f4mespc_cd = self.f4_2021_cd.groupby(['mes','Posible Causa'])[var_f4['costo']].sum().reset_index()
        gb_f4mespc_cd = gb_f4mespc_cd.loc[gb_f4mespc_cd['Posible Causa'].isin(orden_pc_cd)]
        f4_linea =  self.f4_2021.groupby(var_f4["desc_linea"])[var_f4['costo']].sum().reset_index().sort_values(var_f4['costo'],ascending=False).head(10)
        orden_linea_mes = self.f4_2021.groupby([var_f4["desc_linea"],"mes"])[var_f4['costo']].sum().reset_index().sort_values(var_f4['costo'],ascending=False).descripcion_linea.unique()[0:10]
        f4_linea_mes = self.f4_2021.groupby([var_f4["desc_linea"],"mes"])[var_f4['costo']].sum().reset_index().sort_values(var_f4['costo'],ascending=False)
        f4_linea_mes = f4_linea_mes.loc[f4_linea_mes.descripcion_linea.isin(orden_linea_mes)].reset_index(drop=False)
        orden_motivo = self.f4_2021.groupby([var_f4["desc_linea"],"Posible Causa"])[var_f4['costo']].sum().sort_values(ascending=False).reset_index()["Posible Causa"].unique()[0:5]
        orden_linea = self.f4_2021.groupby(["Posible Causa",var_f4["desc_linea"]])[var_f4['costo']].sum().sort_values(ascending=False).reset_index().descripcion_linea.unique()[0:10]
        linea_motivo = self.f4_2021.groupby(["Posible Causa",var_f4["desc_linea"]])[var_f4['costo']].sum().sort_values(ascending=False).reset_index()
        linea_motivo = linea_motivo.loc[linea_motivo["Posible Causa"].isin(orden_motivo)].reset_index(drop=True)
        linea_motivo = linea_motivo.loc[linea_motivo.descripcion_linea.isin(orden_linea)].reset_index(drop=True)

        set_columns_f4(f4_x_semanas,"Semana (fecha de reserva)")
        set_columns_f4(f4_x_años,"año",1)
        set_columns_f4(gb_local,"local_agg")
        set_columns_f4(gb_f4g_graf_21, 'Posible Causa')
        set_columns_f4(gb_f4g_graf_21, 'local_agg')
        set_columns_f4(group_local, 'local_agg')
        set_columns_f4(group_mes, 'mes')
        set_columns_f4(group_mes, 'local_agg')
        set_columns_f4(gb_f4mespc, 'mes')
        set_columns_f4(gb_f4mespc, 'Posible Causa')
        set_columns_f4(gb_f4mespc_cd, 'mes')
        set_columns_f4(gb_f4mespc_cd, 'Posible Causa')
        set_columns_f4(f4_linea_mes, 'mes')
        set_columns_f4(f4_linea_mes, 'descripcion_linea')
        set_columns_f4(linea_motivo,'Posible Causa')

        self.grap_bar_sem(f4_x_semanas)
        self.grap_bar(f4_x_años)
        self.grap_pie(gb_local)
        self.grap_pos_causa(gb_f4g_graf_21)
        self.grap_total(group_total)
        self.grap_f4_local(group_local)
        self.grap_f4_mes_local(group_mes)
        self.f4_mespc = f4_figs(gb_f4mespc, orden_pc, "F4s Tienda mes/motivo")
        self.f4_mespc_cd = f4_figs(gb_f4mespc_cd, orden_pc_cd, 'F4s CD mes/motivo')
        self.grap_pie_lineas(f4_linea)
        self.grap_f4_lina_mes(f4_linea_mes)
        self.grap_f4_linea_motivo(linea_motivo)
    
    def grap_bar_sem(self,f4_x_semanas):
        self.grafica_f4_sem=px.bar(f4_x_semanas, x="Semana (fecha de reserva)", y=var_f4['costo'], labels={var_f4['costo']: "Total costo"}, text=var_f4['costo'], 
        text_auto='.2s', color = 'local_agg', color_discrete_sequence=px.colors.qualitative.Vivid, title= "Creación F4 dados de baja por semana - 2022",color_discrete_map = const.locales)
        self.grafica_f4_sem.update_layout(legend=dict(orientation="h", yanchor="top", xanchor="right", x=1))

    def grap_bar(self, f4_x_años):
        self.ten_creac_x_año = px.bar(f4_x_años,  x="mes", y=var_f4['costo'], color='año', barmode='group',text_auto=",.0f",labels={var_f4['costo']: "Costo total (Millones)","mes":"Mes de reserva ", "categoria":"Año" } ,title="Tendencia de creación F4 dados de baja según mes de reserva")
        self.ten_creac_x_año.update_layout(legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.1))
        
    def grap_pos_causa(self,gb_f4g_graf_21):
        self.graf_f4_pos_causa = px.bar(gb_f4g_graf_21, y="Posible Causa", x=var_f4['costo'] , color = "local_agg",text=var_f4['costo'],text_auto=",.0f",
        title= f"Posibles causas de F4 2022 dados de baja por locales - Total costo $ {gb_f4g_graf_21[var_f4['costo']].sum():,.0f} M ", labels={"Posible Causa":"Posibles causas",var_f4['costo']:"Costo total (Millones)", "local_agg":"Local", 'mes':'Mes de reserva'}, facet_col='mes')#, category_orders={'Posible Causa':orden, 'mes':['Ene', 'Feb', 'Mar']})
        self.graf_f4_pos_causa.update_layout(legend=dict(yanchor="bottom", y=0.1, xanchor="right", x=0.9))

    def grap_pie(self, gb_local):
        self.fig_torta_local = px.pie(gb_local, values=var_f4['costo'], names='local_agg', title='F4 acumulado por sede',color_discrete_map = const.locales)
        self.fig_torta_local.update_traces( textposition='inside', textinfo='percent+label')
    
    def grap_pie_lineas(self, f4_linea):
        self.fig_torta_linea = px.pie(f4_linea, values=var_f4['costo'], names='descripcion_linea', title='F4s Por línea en 2022')
        self.fig_torta_linea.update_traces( textposition='inside', textinfo='percent')
    
    def grap_total(self,group_total):
        total = self.f4_2021[var_f4['costo']].sum()
        total_graf = '${:,.0f} M '.format(total/1e6)
        self.fig_clasificado = px.bar(group_total, x=var_f4['costo'], y="Posible Causa",text=var_f4['costo'] ,text_auto='.2s',labels={var_f4['costo']: "Costo total","Posible Causa":"Causa"})
        self.fig_clasificado.update_layout(yaxis_categoryorder = 'total ascending', title = f"F4 acumulados - Total acumulado 2022 {total_graf}" )
    
    def grap_f4_local(self,group_local):
        self.fig_clasificado_local = px.bar(group_local, x=var_f4['costo'], y="Posible Causa",text=var_f4['costo'] ,color="local_agg" ,text_auto='.2s',labels={var_f4['costo']: "Costo total","Posible Causa":"Causa","local_agg":"Local"}, color_discrete_map = const.locales)
        self.fig_clasificado_local.update_layout(yaxis_categoryorder = 'total ascending',title="F4 acumulados por local")
    
    def grap_f4_mes_local(self,group_mes):
        self.fig_clas_mes_local = px.bar(group_mes, x="mes", y=var_f4['costo'], text=var_f4['costo'] ,color="local_agg" ,text_auto='.2s',labels={var_f4['costo']: "Costo total","mes":"Mes","local_agg":"Local"}, color_discrete_map = const.locales)
        self.fig_clas_mes_local.update_layout(yaxis_categoryorder = 'total ascending',title="F4 acumulados por mes y local")

    def grap_f4_lina_mes(self,f4_linea_mes):
        self.fig_f4_liena_mes = px.bar(f4_linea_mes, x=var_f4["desc_linea"],y=var_f4['costo'], text=var_f4['costo'],color="mes",text_auto='.2s', barmode='group', title="Top 10 F4s por línea y mes",labels={var_f4['costo']:"Costo total",var_f4["desc_linea"]:"Línea","mes":"Mes"})
        self.fig_f4_liena_mes.update_layout(xaxis_categoryorder = 'total descending',legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.6))
    
    def grap_f4_linea_motivo(self,linea_motivo):
        self.fig_f4_linea_motivo = px.bar(linea_motivo, x=var_f4['costo'], y=var_f4["desc_linea"],text=var_f4['costo'] ,color="Posible Causa" ,text_auto='.2s',labels={var_f4['costo']: "Costo total","Posible Causa":"Causa","local_agg":"Local"})
        self.fig_f4_linea_motivo.update_layout(yaxis_categoryorder = 'total ascending',title="F4 acumulados por local")
      
    def save_grap(self):
        self.fig_torta_local.write_image(f"{self.path}/{dt_string}_f4_torta.svg", engine='orca') 
        self.ten_creac_x_año.show()#.write_image(f"images/{dt_string}_tendencia_creacion_f4_x_años.svg", width = 800, height=450, engine='orca')
        self.grafica_f4_sem.show()#.write_image(f"images/{dt_string}_grafica_f4_sem.svg", width = 700, height=500, engine='orca')
        self.graf_f4_pos_causa.show()# graf_f4_pos_causa.write_image(f"images/{dt_string}_clasificacion_posibles_causas_22.svg", width = 1300, height=700, engine='orca') 
        self.fig_clasificado.show()#fig_clasificado.write_image(f"images_f4/{dt_string}_grafica_total.svg", height = 600,  width =700)
        self.fig_clasificado_local.show()#fig_clasificado.write_image(f"images_f4/{dt_string}_grafica_total_por_local.svg", height = 500,  width = 800)
        self.fig_clas_mes_local.show()#self.fig_clas_mes_local.write_image(f"images_f4/{dt_string}_grafica_total_por_mes.svg", height = 500,  width = 500)
        self.f4_mespc.show()
        self.f4_mespc_cd.show()#self.f4_mespc_cd.write_image(f"images/{dt_string}_f4s_cd_mm.svg", engine='orca') # width = 1300, height=700,
        self.fig_torta_linea.show()
        self.fig_f4_liena_mes.show()#fig_f4_liena_mes.write_image(f"images_f4/{dt_string}_grafica_linea_x_mes.svg", height = 500,  width = 800)
        self.fig_f4_linea_motivo.show()


def f4_figs(df, pc_order, titulo):
    fig = px.bar(df, x="Posible Causa", y=var_f4['costo'], color='mes', barmode='group', title=titulo, 
                text= var_f4['costo'], text_auto=",.2s", category_orders={'mes':['Ene','Feb','Mar'], 'Posible Causa':pc_order},
                labels={'mes':'Mes',var_f4['costo']: 'Total costo' , 'Posible Causa':'Posible causa'}, color_discrete_sequence=px.colors.qualitative.Prism)
    fig.update_layout(xaxis_categoryorder = 'total descending')  # ordenar eje x de mayor a menor
    return fig

def set_columns_f4(base,var,ind=0):
    item = base[var].unique().tolist()
    if ind == 0:
        for i in item:
            base.loc[base[var] == i, var] = (base.loc[base[var] == i, var] + " " + '${:,.0f} M '.format(base.loc[base[var] == i, var_f4['costo']].sum()/1e6))
    else:
        for i in item:
            base.loc[base[var] == i, var] = (base.loc[base[var] == i, var] + " " + '${:,.0f} M '.format(base.loc[base[var] == i, var_f4['costo']].sum()))

f4 = F4()