import pandas as pd
import plotly.express as px
from   datetime import date, timedelta, datetime
import plotly.graph_objects as go
import numpy as np
import constants as const
from calendar import monthrange
from data import var_f4
from general import GENERAL
pd.set_option('display.max_columns', 500)

class F4():
    dt_string = datetime.now().strftime('%y%m%d')
    general = GENERAL()

    def __init__(self) -> None:
        self.f4_2022 = pd.read_csv(var_f4["path_df_clas"],sep=";" , dtype = object)
        self.f4_2021 = pd.read_csv("input/f4_2021.csv",sep=";", dtype = object)
        self.path = self.general.generate_structure()
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
        col_str = ["desc_local","Marca","descripcion_linea"]
        for col in col_str : self.f4_21_22[col] = self.f4_21_22[col].str.capitalize()
                
    def filters(self):
        self.f4_2021 = self.f4_21_22.loc[self.f4_21_22[var_f4['fecha_res']] >= "2022-01-01" ].reset_index(drop=True)
        self.f4_2021_cd = self.f4_2021.loc[self.f4_2021.local_agg == "CD"].reset_index()
        self.f4_2021_tienda = self.f4_2021.loc[self.f4_2021.local_agg == "TIENDA"].reset_index()
        self.f4_2022_averia = self.f4_2021.loc[self.f4_2021["Posible Causa"] == "Avería"]
        self.f4_2022_calidad = self.f4_2021.loc[self.f4_2021["Posible Causa"] == "Calidad"]
        self.f4_2022_pant_rotas = self.f4_2021.loc[self.f4_2021["Posible Causa"]== "Pantallas rotas"]
    
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
        orden_linea_mes = self.f4_2021.groupby([var_f4["desc_linea"],"mes"])[var_f4['costo']].sum().reset_index().sort_values(var_f4['costo'],ascending=False)[var_f4['desc_linea']].unique()[0:10]
        f4_linea_mes = self.f4_2021.groupby([var_f4["desc_linea"],"mes"])[var_f4['costo']].sum().reset_index().sort_values(var_f4['costo'],ascending=False)
        f4_linea_mes = f4_linea_mes.loc[f4_linea_mes[var_f4['desc_linea']].isin(orden_linea_mes)].reset_index(drop=False)
        orden_motivo = self.f4_2021.groupby([var_f4["desc_linea"],"Posible Causa"])[var_f4['costo']].sum().sort_values(ascending=False).reset_index()["Posible Causa"].unique()[0:5]
        orden_linea = self.f4_2021.groupby(["Posible Causa",var_f4["desc_linea"]])[var_f4['costo']].sum().sort_values(ascending=False).reset_index()[var_f4['desc_linea']].unique()[0:10]
        linea_motivo = self.f4_2021.groupby(["Posible Causa",var_f4["desc_linea"]])[var_f4['costo']].sum().sort_values(ascending=False).reset_index()
        linea_motivo = linea_motivo.loc[linea_motivo["Posible Causa"].isin(orden_motivo)].reset_index(drop=True)
        linea_motivo = linea_motivo.loc[linea_motivo[var_f4['desc_linea']].isin(orden_linea)].reset_index(drop=True)
        linea_local = self.f4_2021.groupby([var_f4['desc_linea'],"local_agg"])["total_precio_costo"].sum().sort_values(ascending=False).reset_index()
        list_lineas_loc = linea_local[var_f4['desc_linea']].unique()[0:10] 
        linea_local = linea_local.loc[ linea_local[var_f4['desc_linea']].isin(list_lineas_loc)].reset_index(drop=True)
        top_10_marca = self.f4_2022_averia.groupby(["Marca","mes"])[var_f4["costo"]].sum().sort_values(ascending=False).reset_index()
        listado_marcas =self.f4_2022_averia.groupby(["Marca","mes"])[var_f4["costo"]].sum().sort_values(ascending=False).reset_index()["Marca"].unique()[0:10]
        top_10_marca = top_10_marca.loc[top_10_marca.Marca.isin(listado_marcas)].reset_index(drop=True)
        marcas_calidad = self.f4_2022_calidad.groupby(["Marca","mes"])[var_f4['costo']].sum().sort_values(ascending=False).reset_index()
        lista_marcas = marcas_calidad.Marca.unique()[0:10]
        marcas_calidad = marcas_calidad.loc[marcas_calidad.Marca.isin(lista_marcas)].reset_index(drop=True)
        f4_pant_rotas= self.f4_2022_pant_rotas.groupby(["Marca","mes"])["total_precio_costo"].sum().sort_values(ascending=False).reset_index()
        list_pant = f4_pant_rotas.Marca.unique()[0:5]
        f4_pant_rotas.loc[f4_pant_rotas.Marca.isin(list_pant)]

        # top_10_marca.to_excel(f"{self.path}_tabla_top_10_marca.xlsx")
        # marcas_calidad.to_excel(f"{self.path}_tabla_marca_calidad.xlsx")
        # f4_pant_rotas.to_excel(f"{self.path}_pantallas_rotas.xlsx")
        # self.f4_2022_pant_rotas.to_excel(f"{self.path}_tabla_pantallas_rotas.xlsx")


        self.general.set_columns_sum(f4_x_semanas,"Semana (fecha de reserva)",var_f4['costo'])
        self.general.set_columns_sum(f4_x_semanas,"local_agg",var_f4['costo'])
        self.general.set_columns_sum(f4_x_años,"año",var_f4['costo'])
        self.general.set_columns_sum(gb_local,"local_agg",var_f4['costo'])
        self.general.set_columns_sum(gb_f4g_graf_21, 'Posible Causa',var_f4['costo'])
        self.general.set_columns_sum(gb_f4g_graf_21, 'local_agg',var_f4['costo'])
        self.general.set_columns_sum(group_local, 'local_agg',var_f4['costo'])
        self.general.set_columns_sum(group_mes, 'mes',var_f4['costo'])
        self.general.set_columns_sum(group_mes, 'local_agg',var_f4['costo'])
        self.general.set_columns_sum(gb_f4mespc, 'mes',var_f4['costo'])
        self.general.set_columns_sum(gb_f4mespc, 'Posible Causa',var_f4['costo'])
        self.general.set_columns_sum(gb_f4mespc_cd, 'mes',var_f4['costo'])
        self.general.set_columns_sum(gb_f4mespc_cd, 'Posible Causa',var_f4['costo'])
        self.general.set_columns_sum(f4_linea_mes, 'mes',var_f4['costo'])
        self.general.set_columns_sum(f4_linea_mes, var_f4['desc_linea'],var_f4['costo'])
        self.general.set_columns_sum(linea_motivo,'Posible Causa',var_f4['costo'])
        self.general.set_columns_sum(linea_motivo, var_f4['desc_linea'],var_f4['costo'])
        self.general.set_columns_sum(linea_local, var_f4['desc_linea'],var_f4['costo'])
        self.general.set_columns_sum(linea_local, 'local_agg',var_f4['costo'])
        self.general.set_columns_sum(top_10_marca, 'Marca',var_f4['costo'])
        self.general.set_columns_sum(top_10_marca, 'mes',var_f4['costo'])
        self.general.set_columns_sum(marcas_calidad, 'mes',var_f4['costo'])
        self.general.set_columns_sum(marcas_calidad, 'Marca',var_f4['costo'])
        self.general.set_columns_sum(f4_pant_rotas, 'Marca',var_f4['costo'])
        self.general.set_columns_sum(f4_pant_rotas, 'mes',var_f4['costo'])

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
        self.grap_f4_linea_local(linea_local)
        self.grap_f4_top_10_marcas(top_10_marca)
        self.grap_marca_esp()
        self.grap_marca_averia(marcas_calidad)
        self.grap_pant_rotas(f4_pant_rotas)
    
    def grap_bar_sem(self,f4_x_semanas):
        colores = self.general.unif_colors(f4_x_semanas, "local_agg")
        self.grafica_f4_sem=px.bar(f4_x_semanas, x="Semana (fecha de reserva)", y=var_f4['costo'], labels={var_f4['costo']: "Total costo","local_agg":"Local"}, text=var_f4['costo'], 
        text_auto='.2s', color = 'local_agg', title= "Creación F4 dados de baja por semana - 2022",color_discrete_map = colores)
        self.grafica_f4_sem.update_layout(legend=dict(orientation="h", yanchor="bottom", xanchor="right",x=1,y=1))

    def grap_bar(self, f4_x_años):
        colores = self.general.unif_colors(f4_x_años,"año")
        f4_x_años[var_f4['costo']] = f4_x_años[var_f4['costo']]/1e6
        self.ten_creac_x_año = px.bar(f4_x_años,  x="mes", y=var_f4['costo'], color='año', barmode='group',text_auto=",.0f",labels={var_f4['costo']: "Costo total (Millones)","mes":"Mes de reserva ", "categoria":"Año" } ,title="Tendencia de creación F4 dados de baja según mes de reserva", color_discrete_map = colores)  
        self.ten_creac_x_año.update_layout(legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.1))
        
    def grap_pos_causa(self,gb_f4g_graf_21):
        colores = self.general.unif_colors(gb_f4g_graf_21,"local_agg")
        orden = gb_f4g_graf_21.sort_values("total_precio_costo", ascending=False)["Posible Causa"].unique()
        gb_f4g_graf_21["total_precio_costo"] = gb_f4g_graf_21["total_precio_costo"]/1e6
        self.graf_f4_pos_causa = px.bar(gb_f4g_graf_21, y="Posible Causa", x=var_f4['costo'] , color = "local_agg",text=var_f4['costo'],text_auto='.2s',
        title= f"Posibles causas de F4 2022 dados de baja por locales - Total costo $ {gb_f4g_graf_21[var_f4['costo']].sum():,.0f} M ", labels={"Posible Causa":"Posibles causas",var_f4['costo']:"Costo total (Millones)", "local_agg":"Local", 'mes':'Mes de reserva'}, facet_col='mes', category_orders={'Posible Causa':orden, 'mes':['Ene', 'Feb', 'Mar']}, color_discrete_map = colores)
        self.graf_f4_pos_causa.update_layout(legend=dict(yanchor="bottom", y=0.05, xanchor="right", x=1))

    def grap_pie(self, gb_local):
        colores = self.general.unif_colors(gb_local,"local_agg")
        self.fig_torta_local = px.pie(gb_local, values=var_f4['costo'], names='local_agg', color="local_agg" ,title='F4 acumulado por sede',color_discrete_map = colores)
        self.fig_torta_local.update_traces( textposition='inside', textinfo='percent+label')
        self.fig_torta_local.update_layout(font_size=16)
    
    def grap_pie_lineas(self, f4_linea):
        self.fig_torta_linea = px.pie(f4_linea, values=var_f4['costo'], names=var_f4['desc_linea'], title='F4s Por línea en 2022')
        self.fig_torta_linea.update_traces( textposition='inside', textinfo='percent')
    
    def grap_total(self,group_total):
        total = self.f4_2021[var_f4['costo']].sum()
        total_graf = '${:,.0f} M '.format(total/1e6)
        self.fig_clasificado = px.bar(group_total, x=var_f4['costo'], y="Posible Causa",text=var_f4['costo'] ,text_auto='.2s',labels={var_f4['costo']: "Costo total","Posible Causa":"Posible causa"})
        self.fig_clasificado.update_layout(yaxis_categoryorder = 'total ascending', title = f"F4 acumulados - Total acumulado 2022 {total_graf}")

    
    def grap_f4_local(self,group_local):
        colores = self.general.unif_colors(group_local,"local_agg")
        self.fig_clasificado_local = px.bar(group_local, x=var_f4['costo'], y="Posible Causa",text=var_f4['costo'],color="local_agg" ,text_auto='.2s',labels={var_f4['costo']: "Costo total","Posible Causa":"Posible causa","local_agg":"Local"}, color_discrete_map = colores)
        self.fig_clasificado_local.update_layout(yaxis_categoryorder = 'total ascending',title="F4 acumulados por local",legend=dict(yanchor="top", y=0.5, xanchor="left", x=0.6), font_size=15)
    
    def grap_f4_mes_local(self,group_mes):
        colores = self.general.unif_colors(group_mes,"local_agg")
        orden = self.general.ord_mes(group_mes,"mes")
        self.fig_clas_mes_local = px.bar(group_mes, x="mes", y=var_f4['costo'], text=var_f4['costo'] ,color="local_agg" ,text_auto='.2s',labels={var_f4['costo']: "Costo total","mes":"Mes","local_agg":"Local"}, color_discrete_map = colores, category_orders= {"mes":orden})
        self.fig_clas_mes_local.update_layout(yaxis_categoryorder = 'total ascending',title="F4 acumulados por mes y local", font_size = 15)

    def grap_f4_lina_mes(self,f4_linea_mes):
        orden = self.general.ord_mes(f4_linea_mes,"mes")
        colores = self.general.unif_colors(f4_linea_mes,"mes")
        self.fig_f4_linea_mes = px.bar(f4_linea_mes, x=var_f4["desc_linea"],y=var_f4['costo'], text=var_f4['costo'],color="mes",text_auto='.2s', barmode='group', title="Top 10 F4s por línea y mes",labels={var_f4['costo']:"Costo total",var_f4["desc_linea"]:"Línea","mes":"Mes"},color_discrete_map = colores, category_orders={'mes':orden})
        self.fig_f4_linea_mes.update_layout(legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.6))
    
    def grap_f4_linea_motivo(self,linea_motivo):
        self.fig_f4_linea_motivo = px.bar(linea_motivo, x=var_f4['costo'], y=var_f4["desc_linea"],text=var_f4['costo'] ,color="Posible Causa" ,text_auto='.2s',labels={var_f4['costo']: "Costo total","Posible Causa":"Causa","local_agg":"Local","descripcion_linea":"Linea"})
        self.fig_f4_linea_motivo.update_layout(yaxis_categoryorder = 'total ascending',title="F4 por linea con motivo")

    def grap_f4_linea_local(self,linea_local):
        color = self.general.unif_colors(linea_local,"local_agg")
        self.fig_lin_local = px.bar(linea_local, x="descripcion_linea", y="total_precio_costo",barmode='group',color= "local_agg",title="F4 por línea por local", labels={"descripcion_linea":"Linea","total_precio_costo":"Total costo","local_agg":"Local"}, color_discrete_map = color)
        self.fig_lin_local.update_layout(legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.5))

    def grap_f4_top_10_marcas(self,top_10_marca):
        color = self.general.unif_colors(top_10_marca,"mes")
        orden = self.general.ord_mes(top_10_marca,"mes")
        self.fig_f4_marca = px.bar(top_10_marca, x="Marca",y="total_precio_costo",text="total_precio_costo",color="mes",text_auto='.2s', barmode='group', title="Top 10 F4s Avería por marca y mes",labels={"total_precio_costo":"Costo total","descripcion_linea":"Linea","mes":"Mes"}, color_discrete_map=color, category_orders={"mes":orden})
        self.fig_f4_marca.update_layout(xaxis_categoryorder = 'total descending',legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.85))
        
    
    def grap_marca_esp(self):
        self.marc = "barbie"
        marca = self.f4_2022_averia.loc[self.f4_2022_averia.Marca == self.marc]
        grup_marca = marca.groupby(["desc_local","mes"])["total_precio_costo"].sum().sort_values(ascending=False).reset_index()
        self.general.set_columns_sum(grup_marca,"mes",var_f4['costo'])
        self.general.set_columns_sum(grup_marca,"desc_local",var_f4['costo'])
        color = self.general.unif_colors(grup_marca,"mes")
        self.fig_marca_locales = px.bar(grup_marca, x="desc_local",y="total_precio_costo",text="total_precio_costo",color="mes",text_auto='.2s', title=f"{self.marc} por local",labels={"total_precio_costo":"Costo total","desc_local":"Local","mes":"Mes"}, color_discrete_map = color)
        self.fig_marca_locales.update_layout(xaxis_categoryorder = 'total descending')
    
    def grap_marca_averia(self, marcas_calidad):
        orden = self.general.ord_mes(marcas_calidad,"mes")
        color = self.general.unif_colors(marcas_calidad,"mes")
        self.fig_marcas_calidad = px.bar(marcas_calidad, x="Marca", y= "total_precio_costo", barmode='group',color="mes",text_auto='.2s', color_discrete_map= color, category_orders={"mes":orden}, labels={"total_precio_costo":"Total costo","mes":"Mes"})

    def grap_pant_rotas(self,f4_pant_rotas):
        color= self.general.unif_colors(f4_pant_rotas,"mes")
        orden = self.general.ord_mes(f4_pant_rotas,"mes")
        self.fig_pant_rotas = px.bar(f4_pant_rotas, x="Marca", y= "total_precio_costo",color="mes",text_auto='.2s', category_orders={"mes":orden}, labels={"total_precio_costo":"Total costo","mes":"Mes"}, color_discrete_map = color)

    def save_grap(self):
        # self.fig_torta_local.write_image(f"{self.path}/images/{self.dt_string}_f4_torta.svg", engine='orca') 
        # self.ten_creac_x_año.write_image(f"{self.path}/images/{self.dt_string}_tendencia_creacion_f4_x_años.svg", width = 800, height=450, engine='orca')
        # self.grafica_f4_sem.write_image(f"{self.path}/images/{self.dt_string}_grafica_f4_sem.svg", width = 700, height=500, engine='orca')
        # self.graf_f4_pos_causa.write_image(f"{self.path}/images/{self.dt_string}_clasificacion_posibles_causas_22.svg", width = 1300, height=700, engine='orca') 
        # self.fig_clasificado.write_image(f"{self.path}/images/{self.dt_string}_grafica_total.svg", height = 600,  width =700)
        self.fig_clasificado_local.write_image(f"{self.path}/images/{self.dt_string}_grafica_total_por_local.svg", height = 500,  width = 800,engine='orca')
        # self.fig_clas_mes_local.write_image(f"{self.path}/images/{self.dt_string}_grafica_total_por_mes.svg", height = 500,  width = 500,engine='orca')
        # self.f4_mespc.write_image(f"{self.path}/images/{self.dt_string}_tienda_mes_motivo.svg", height = 500,  width = 700,engine='orca')
        # self.f4_mespc_cd.write_image(f"{self.path}/images/{self.dt_string}_f4s_cd_mm.svg", engine='orca')
        # self.fig_torta_linea.write_image(f"{self.path}/images/{self.dt_string}_torta_linea.svg", height = 500,  width = 700,engine='orca')
        # self.fig_f4_linea_mes.write_image(f"{self.path}/images/{self.dt_string}_grafica_linea_x_mes.svg", height = 500,  width = 800,engine='orca')
        # self.fig_f4_linea_motivo.write_image(f"{self.path}/images/{self.dt_string}_linea_motivo.svg", height =600,  width = 1000,engine='orca')
        # self.fig_lin_local.write_image(f"{self.path}/images/{self.dt_string}_linea_local.svg", height =500,  width = 800, engine='orca')
        # self.fig_f4_marca.write_image(f"{self.path}/images/{self.dt_string}_grafica_averia_x_mes_y_marca.svg", height = 500,  width = 900,engine='orca')
        # self.fig_marca_locales.write_image(f"{self.path}/images/{self.dt_string}_{self.marc}_local.svg", height =500,  width = 800, engine='orca')
        # self.fig_marcas_calidad.write_image(f"{self.path}/images/{self.dt_string}_marca_calidad.svg", height =500,  width = 800, engine='orca')
        # self.fig_pant_rotas.write_image(f"{self.path}/images/{self.dt_string}_pantallas_rotas.svg", height =500,  width = 800, engine='orca')


def f4_figs(df, pc_order, titulo):
    general = GENERAL()
    colores = general.unif_colors(df,"mes")
    fig = px.bar(df, x="Posible Causa", y=var_f4['costo'], color='mes', barmode='group', title=titulo, 
                text= var_f4['costo'], text_auto=",.2s", category_orders={'mes':['Ene','Feb','Mar'], 'Posible Causa':pc_order},color_discrete_map = colores,
                labels={'mes':'Mes',var_f4['costo']: 'Total costo' , 'Posible Causa':'Posible causa'}, )
    fig.update_layout(xaxis_categoryorder = 'total descending')  # ordenar eje x de mayor a menor
    return fig

f4 = F4()