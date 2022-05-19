import pandas as pd
import plotly.express as px
from   datetime import timedelta, datetime
from calendar import monthrange
from data import var_f4
from general import  set_columns_sum, unif_colors, ord_mes, ord_num
import plotly.graph_objects as go
pd.set_option('display.max_columns', 500)


# A tener en cuenta: 
# TODO 1. Entre método y método solo un espacio de separación 
# TODO 2. cuando hay signo '=' dejar un espacio antes y después  
# TODO 3. cuando vayan ',' que queden pegadas a la palabra anterior y con un espacio después 

class F4():

    def __init__(self,f4_clasificada,fc) -> None:
        self.fecha_corte = fc
        self.f4_2022 =  f4_clasificada
        self.f4_2021 = pd.read_csv('input/f4_2021.csv',sep =';', dtype = object) # TODO leer path desde var_f3
        self.path = f'output/{fc}_corte/images/f4'
        self.f4_21_22()
        self.transform()
        self.filters()
        self.set_week_f4()
        self.make_groupby()
        self.save_grap()

    def get_path(self):
        return self.path

    def f4_21_22(self):
        self.f4_2022['año'] = '2022' # TODO leer desde var_f4
        self.f4_21_22 = pd.concat([self.f4_2021,self.f4_2022]) # Esta variable se llama igual que el método, esto puede hacer que python se confunda 
    
    def transform(self):
        self.f4_21_22[var_f4['costo']] = pd.to_numeric(self.f4_21_22[var_f4['costo']], downcast = 'integer')
        for i in var_f4['fechas']: self.f4_21_22[i] = pd.to_datetime(self.f4_21_22[i])
        meses_ing = ['Jan', 'Apr', 'Aug', 'Dec']
        meses_esp = ['Ene', 'Abr', 'Ago', 'Dic']
        i=0
        for mes in meses_ing:
                self.f4_21_22.loc[self.f4_21_22['mes'] == mes, 'mes' ] = meses_esp[i]
                i = i+1
        col_str = ['desc_local','Marca','descripcion_linea'] # TODO leer desde var_f4
        for col in col_str : self.f4_21_22[col] = self.f4_21_22[col].str.capitalize()
        self.f4_21_22.descripcion_linea = self.f4_21_22.linea.str.upper() + ' - ' + self.f4_21_22.descripcion_linea # TODO leer desde var_f4

    def filters(self):
        self.f4_2022 = self.f4_21_22.loc[self.f4_21_22[var_f4['fecha_res']] >= '2022-01-01' ].reset_index(drop=True)  # TODO leer desde var_f4 = fecha_inicial
        self.f4_2022_cd = self.f4_2022.loc[self.f4_2022.local_agg == 'CD'].reset_index() # TODO leer desde var_f4
        self.f4_2022_tienda = self.f4_2022.loc[self.f4_2022.local_agg == 'TIENDA'].reset_index() # TODO leer desde var_f4
        self.f4_2022_averia = self.f4_2022.loc[self.f4_2022['Posible Causa'] == 'Avería'] # TODO leer desde var_f4
        self.f4_2022_calidad = self.f4_2022.loc[self.f4_2022['Posible Causa'] == 'Calidad'] # TODO leer desde var_f4
        self.f4_2022_pant_rotas = self.f4_2022.loc[self.f4_2022['Posible Causa']== 'Pantallas rotas'] # TODO leer desde var_f4 # DONE 
    
    def set_week_f4(self):
        self.f4_sem = self.f4_2022.copy()
        self.f4_sem.loc[self.f4_sem.mes == 'Inventario' ,'mes'] = 'Ene' # TODO leer desde var_f4
        lista_mes = self.f4_sem.mes.unique() # TODO leer desde var_f4
        f_inicio  = datetime.strptime('2022/01/01', '%Y/%m/%d') # TODO leer desde var_f4
        f_cortes = f_inicio
        for mes in enumerate(lista_mes):
            sem = 0
            while f_cortes < self.f4_sem.loc[self.f4_sem.mes == mes[1], var_f4['fecha_res']].max(): # TODO leer desde var_f4
                sem = sem + 1
                f_cortes = f_inicio + timedelta(days = 7)
                if sem == 4:
                    dias = monthrange(2011,mes[0]+1)[1]
                    if dias == 28:
                        f_cortes = f_cortes - timedelta(days = 4)
                    elif dias == 30:
                        f_cortes = f_cortes - timedelta(days = 2) 
                    elif dias == 31:
                        f_cortes = f_cortes - timedelta(days = 1)
                self.f4_sem.loc[(self.f4_sem[var_f4['fecha_res']] >= f_inicio) & (self.f4_sem[var_f4['fecha_res']] <= f_cortes), 'Semana (fecha de reserva)'] = f"S{sem}{f_cortes.strftime('%b')}"
                f_inicio = f_cortes + timedelta(days = 1)

    def make_groupby(self):
        f4_x_semanas =  self.f4_sem.groupby(['local_agg', 'Semana (fecha de reserva)'], sort = False)[var_f4['costo']].sum().reset_index()# TODO leer desde var_f4
        f4_x_años = self.f4_21_22.groupby(['año', 'mes'],sort = False)[var_f4['costo']].sum().reset_index() # TODO leer desde var_f4
        gb_local = self.f4_2022.groupby('local_agg')[var_f4['costo']].sum().reset_index() # TODO leer desde var_f4
        gb_f4g_graf_21 = self.f4_2022.groupby(['mes', 'Posible Causa', 'local_agg']).agg({var_f4['costo']:'sum'}).reset_index() # TODO leer desde var_f4
        group_total = self.f4_2022.groupby('Posible Causa')[var_f4['costo']].sum().sort_values(ascending = False).reset_index() # TODO leer desde var_f4
        group_local = self.f4_2022.groupby(['Posible Causa','local_agg'])[var_f4['costo']].sum().sort_values(ascending = False).reset_index() # TODO leer desde var_f4
        group_local = group_local.loc[group_local.local_agg.isin(['TIENDA','CD'])].reset_index() # TODO leer desde var_f4
        group_mes = self.f4_2022.groupby(['mes','local_agg'])[var_f4['costo']].sum().sort_values(ascending = False).reset_index() # TODO leer desde var_f4
        group_mes = group_mes.loc[group_mes.local_agg.isin(['TIENDA','CD'])].reset_index() # TODO leer desde var_f4
        orden_pc = self.f4_2022_tienda.groupby('Posible Causa')[var_f4['costo']].sum().sort_values(ascending = False).head(5).keys() # TODO leer desde var_f4
        gb_f4mespc = self.f4_2022_tienda.groupby(['mes','Posible Causa'])[var_f4['costo']].sum().reset_index() # TODO leer desde var_f4
        gb_f4mespc = gb_f4mespc.loc[gb_f4mespc['Posible Causa'].isin(orden_pc)] # TODO leer desde var_f4
        orden_pc_cd = self.f4_2022_cd.groupby('Posible Causa')[var_f4['costo']].sum().sort_values(ascending = False).head(5).keys() # TODO leer desde var_f4
        gb_f4mespc_cd = self.f4_2022_cd.groupby(['mes','Posible Causa'])[var_f4['costo']].sum().reset_index() # TODO leer desde var_f4
        gb_f4mespc_cd = gb_f4mespc_cd.loc[gb_f4mespc_cd['Posible Causa'].isin(orden_pc_cd)] # TODO leer desde var_f4
        f4_linea =  self.f4_2022.groupby(var_f4['desc_linea'])[var_f4['costo']].sum().reset_index().sort_values(var_f4['costo'],ascending = False).head(10) # TODO leer desde var_f4
        orden_linea_mes = self.f4_2022.groupby([var_f4['desc_linea'],'mes'])[var_f4['costo']].sum().reset_index().sort_values(var_f4['costo'],ascending = False)[var_f4['desc_linea']].unique()[0:10] # TODO leer desde var_f4
        f4_linea_mes = self.f4_2022.groupby([var_f4['desc_linea'],'mes'])[var_f4['costo']].sum().reset_index().sort_values(var_f4['costo'],ascending = False) # TODO leer desde var_f4
        f4_linea_mes = f4_linea_mes.loc[f4_linea_mes[var_f4['desc_linea']].isin(orden_linea_mes)].reset_index(drop = False) 
        linea_motivo = self.f4_2022.groupby([var_f4['desc_linea'],'Posible Causa'])[var_f4['costo']].sum().reset_index().sort_values(var_f4['costo'], ascending = False) # TODO leer desde var_f4
        top_lineas = linea_motivo.groupby([var_f4['desc_linea']])['total_precio_costo'].sum().sort_values(ascending = False).head(9).keys() # TODO leer desde var_f4
        linea_motivo.loc[~linea_motivo[var_f4['desc_linea']].isin(top_lineas), [var_f4['desc_linea']]] = 'Otras' 
        top_pcs = linea_motivo.groupby(['Posible Causa'])['total_precio_costo'].sum().sort_values(ascending = False).head(5).keys() # TODO leer desde var_f4
        linea_motivo.loc[~linea_motivo['Posible Causa'].isin(top_pcs), 'Posible Causa'] = 'Otras causas' # TODO leer desde var_f4
        linea_local = self.f4_2022.groupby([var_f4['desc_linea'],'local_agg'])[var_f4['costo']].sum().sort_values(ascending = False).reset_index() # TODO leer desde var_f4
        list_lineas_loc = linea_local[var_f4['desc_linea']].unique()[0:10] 
        linea_local = linea_local.loc[ linea_local[var_f4['desc_linea']].isin(list_lineas_loc)].reset_index(drop = True)
        top_10_marca = self.f4_2022_averia.groupby(['Marca','mes'])[var_f4['costo']].sum().sort_values(ascending = False).reset_index() # TODO leer desde var_f4
        listado_marcas = self.f4_2022_averia.groupby(['Marca','mes'])[var_f4['costo']].sum().sort_values(ascending = False).reset_index()['Marca'].unique()[0:10] # TODO leer desde var_f4
        top_10_marca = top_10_marca.loc[top_10_marca.Marca.isin(listado_marcas)].reset_index(drop = True)
        marcas_calidad = self.f4_2022_calidad.groupby(['Marca','mes'])[var_f4['costo']].sum().sort_values(ascending = False).reset_index() # TODO leer desde var_f4
        lista_marcas = marcas_calidad.Marca.unique()[0:10] # TODO para llamar una columna usa ['col'] TODO leer desde var_f4
        marcas_calidad = marcas_calidad.loc[marcas_calidad.Marca.isin(lista_marcas)].reset_index(drop = True)  # TODO para llamar una columna usa ['col'] TODO leer desde var_f4
        f4_pant_rotas= self.f4_2022_pant_rotas.groupby(['Marca','mes'])[var_f4['costo']].sum().sort_values(ascending = False).reset_index() # TODO leer desde var_f4
        orden_pc_tot = self.f4_2022.groupby('Posible Causa')['total_precio_costo'].sum().sort_values(ascending = False).head(7).keys()  # TODO leer desde var_f4
        gb_f4mes_tot = self.f4_2022.groupby(['mes','Posible Causa'])['total_precio_costo'].sum().reset_index() # TODO leer desde var_f4
        gb_f4mes_tot = gb_f4mes_tot.loc[gb_f4mes_tot['Posible Causa'].isin(orden_pc_tot)] # TODO leer desde var_f4
        
        self.tb_averias = make_tables_top_10(top_10_marca)
        self.tb_p_rotas = make_tables_top_10(f4_pant_rotas)
        self.tb_calidad = make_tables_top_10(marcas_calidad)
        self.tb_loc_pant = make_tables_top_10(self.grap_pant_rotas, 'loc')
        self.tb_prod_pant = make_tables_top_10(self.grap_pant_rotas, 'prod')

        set_columns_sum(f4_x_semanas,'Semana (fecha de reserva)',var_f4['costo'])
        set_columns_sum(f4_x_semanas,'local_agg',var_f4['costo'])
        set_columns_sum(f4_x_años,'año',var_f4['costo'])
        set_columns_sum(gb_local,'local_agg',var_f4['costo'])
        set_columns_sum(gb_f4g_graf_21, 'Posible Causa',var_f4['costo'])
        set_columns_sum(gb_f4g_graf_21, 'local_agg',var_f4['costo'])
        set_columns_sum(group_local, 'local_agg',var_f4['costo'])
        set_columns_sum(group_mes, 'mes',var_f4['costo'])
        set_columns_sum(group_mes, 'local_agg',var_f4['costo'])
        set_columns_sum(gb_f4mespc, 'mes',var_f4['costo'])
        set_columns_sum(gb_f4mespc, 'Posible Causa',var_f4['costo'])
        set_columns_sum(gb_f4mespc_cd, 'mes',var_f4['costo'])
        set_columns_sum(gb_f4mespc_cd, 'Posible Causa',var_f4['costo'])
        set_columns_sum(f4_linea_mes, 'mes',var_f4['costo'])
        set_columns_sum(f4_linea_mes, var_f4['desc_linea'],var_f4['costo'])
        set_columns_sum(linea_motivo,'Posible Causa',var_f4['costo'])
        set_columns_sum(linea_motivo, var_f4['desc_linea'],var_f4['costo'])
        set_columns_sum(linea_local, var_f4['desc_linea'],var_f4['costo'])
        set_columns_sum(linea_local, 'local_agg',var_f4['costo'])
        set_columns_sum(top_10_marca, 'Marca',var_f4['costo'])
        set_columns_sum(top_10_marca, 'mes',var_f4['costo'])
        set_columns_sum(marcas_calidad, 'mes',var_f4['costo'])
        set_columns_sum(marcas_calidad, 'Marca',var_f4['costo'])
        set_columns_sum(f4_pant_rotas, 'Marca',var_f4['costo'])
        set_columns_sum(f4_pant_rotas, 'mes',var_f4['costo'])
        set_columns_sum(gb_f4mes_tot, 'mes',var_f4['costo'])
        set_columns_sum(gb_f4mes_tot, 'Posible Causa',var_f4['costo'])

        self.grap_bar_sem(f4_x_semanas)
        self.grap_bar(f4_x_años)
        self.grap_pie(gb_local)
        self.grap_pos_causa(gb_f4g_graf_21)
        self.grap_total(group_total)
        self.grap_f4_local(group_local)
        self.grap_f4_mes_local(group_mes)
        self.f4_mespc = f4_figs(gb_f4mespc, orden_pc, 'F4s Tienda mes/motivo')
        self.f4_mespc_cd = f4_figs(gb_f4mespc_cd, orden_pc_cd, 'F4s CD mes/motivo')
        self.f4_mespc_tot = f4_figs(gb_f4mes_tot, orden_pc_tot, 'F4s por mes y motivo total compañía')
        self.grap_pie_lineas(f4_linea)
        self.grap_f4_lina_mes(f4_linea_mes)
        self.grap_f4_linea_motivo(linea_motivo)
        self.grap_f4_linea_local(linea_local)
        self.grap_f4_top_10_marcas(top_10_marca)
        self.grap_marca_esp()
        self.grap_marca_averia(marcas_calidad)
        self.grap_pant_rotas(f4_pant_rotas)
    
    def grap_bar_sem(self,f4_x_semanas):
        colores = unif_colors(f4_x_semanas, 'local_agg') # TODO leer desde var_f4
        orden = ord_num(f4_x_semanas,'local_agg',var_f4['costo']) # TODO leer desde var_f4
        self.grafica_f4_sem = px.bar(f4_x_semanas, x = 'Semana (fecha de reserva)', y = var_f4['costo'], labels = {var_f4['costo']: 'Total costo','local_agg':'Local'}, text = var_f4['costo'], # TODO leer desde var_f4
        text_auto = '.2s', color = 'local_agg', color_discrete_map = colores, category_orders = {'local_agg' :orden}) # TODO leer desde var_f4
        self.grafica_f4_sem.update_layout(legend = dict(orientation = 'h', yanchor = 'bottom', xanchor = 'left',x = 0,y = 1), font = dict(size = 14), margin=dict(l=0,r=10,t=100), title={'text':'Creación F4 dados de baja por semana - 2022','y':0.99,'x':0.5,'yanchor': 'top'})

    def grap_bar(self, f4_x_años):
        colores = unif_colors(f4_x_años,'año') # TODO leer desde var_f4
        orden = ord_mes(f4_x_años, 'mes') # TODO leer desde var_f4
        f4_x_años[var_f4['costo']] = f4_x_años[var_f4['costo']]/1e6
        self.ten_creac_x_año = px.bar(f4_x_años,  x = 'mes', y = var_f4['costo'], color = 'año', barmode = 'group',text_auto = ',.0f',# TODO leer desde var_f4
        labels = {var_f4['costo']: 'Costo total (Millones)','mes':'Mes de reserva ', 'año':'Año'} ,title = 'Tendencia de creación F4 dados de baja según mes de reserva', # TODO leer desde var_f4
        color_discrete_map = colores, category_orders = {'mes' : orden})  
        self.ten_creac_x_año.update_layout(legend = dict(yanchor = 'top', y = 0.95, xanchor = 'left', x = 0.1),font =dict(size = 15), margin=dict(l=0,r=10,b=0) )
        
    def grap_pos_causa(self,gb_f4g_graf_21): 
        colores = unif_colors(gb_f4g_graf_21,'local_agg') # TODO leer desde var_f4
        orden = gb_f4g_graf_21.sort_values(var_f4['costo'], ascending = False)['Posible Causa'].unique() # TODO leer desde var_f4
        gb_f4g_graf_21[var_f4['costo']] = gb_f4g_graf_21[var_f4['costo']]/1e6
        self.graf_f4_pos_causa = px.bar(gb_f4g_graf_21, y = 'Posible Causa', x = var_f4['costo'] , color = 'local_agg',text = var_f4['costo'],text_auto = '.2s', # TODO leer desde var_f4
        title = f'Posibles causas de F4 2022 dados de baja por locales - Total costo $ {gb_f4g_graf_21[var_f4["costo"]].sum():,.0f} M ', 
        labels = {'Posible Causa':'Posibles causas',var_f4['costo']:'Costo total (Millones)', 'local_agg':'Local', 'mes':'Mes de reserva'}, 
        facet_col = 'mes', category_orders = {'Posible Causa':orden, 'mes':['Inventario','Ene', 'Feb', 'Mar']}, color_discrete_map = colores) # TODO leer desde var_f4
        self.graf_f4_pos_causa.update_layout(legend = dict(yanchor = 'bottom', y = 0.05, xanchor = 'right', x = 1))

    def grap_pie(self, gb_local):
        colores = unif_colors(gb_local,'local_agg') # TODO leer desde var_f4
        self.fig_torta_local = px.pie(gb_local, values = var_f4['costo'], names = 'local_agg', color = 'local_agg' ,title ='F4 acumulado por sede',color_discrete_map = colores) # TODO leer desde var_f4
        self.fig_torta_local.update_traces( textposition ='inside', textinfo = 'percent+label')
        self.fig_torta_local.update_layout(font = dict(size = 15),  margin =dict(l=0, r=0, t=40,b=0))
    
    def grap_pie_lineas(self, f4_linea):
        self.fig_torta_linea = px.pie(f4_linea, values = var_f4['costo'], names = var_f4['desc_linea'],color_discrete_sequence = px.colors.qualitative.Vivid , title='F4s Por línea en 2022')
        self.fig_torta_linea.update_traces( textposition='inside', textinfo = 'percent')
        self.fig_torta_linea.update_layout(font_size=16,legend=dict(yanchor = 'top',xanchor='right', orientation = 'h',y = 0,x = 0.8),font=dict(size=15), margin= dict(l=0,r=0) )
    
    def grap_total(self,group_total):
        total = self.f4_2022[var_f4['costo']].sum()
        total_graf = '${:,.0f} M '.format(total/1e6)
        self.fig_clasificado = px.bar(group_total, x=var_f4['costo'], y='Posible Causa',text=var_f4['costo'] ,text_auto='.2s',labels={var_f4['costo']: 'Costo total','Posible Causa':'Posible causa'})
        self.fig_clasificado.update_layout(yaxis_categoryorder = 'total ascending', title = f'F4 acumulados - Total acumulado 2022 {total_graf}')

    def grap_f4_local(self,group_local):
        orden = ord_num(group_local,'local_agg',var_f4['costo']) # TODO leer desde var_f4
        colores = unif_colors(group_local,'local_agg') # TODO leer desde var_f4
        self.fig_clasificado_local = px.bar(group_local, x = var_f4['costo'], y = 'Posible Causa',text= var_f4['costo'],color = 'local_agg',  # TODO leer desde var_f4
        text_auto = '.2s',labels={var_f4['costo']: 'Costo total','Posible Causa':'Posible causa','local_agg':'Local'}, color_discrete_map = colores, # TODO leer desde var_f4
        category_orders = {'local_agg':orden}) # TODO leer desde var_f4
        self.fig_clasificado_local.update_layout(yaxis_categoryorder = 'total ascending',title= 'F4 acumulados por local',legend = dict(yanchor = 'top', y = 0.5, xanchor = 'left', x = 0.6), font = dict(size=15), margin=dict(l=0,r=0))
    
    def grap_f4_mes_local(self,group_mes):
        colores = unif_colors(group_mes,'local_agg') # TODO leer desde var_f4
        orden = ord_mes(group_mes,'mes') # TODO leer desde var_f4
        self.fig_clas_mes_local = px.bar(group_mes, x='mes', y = var_f4['costo'], text = var_f4['costo'] ,color = 'local_agg' ,text_auto = '.2s',labels = {var_f4['costo']: 'Costo total','mes':'Mes','local_agg':'Local'}, color_discrete_map = colores, category_orders = {'mes':orden})
        self.fig_clas_mes_local.update_layout(yaxis_categoryorder = 'total ascending',title ={'text':'F4 acumulados por mes y local','y':0.99,'x':0.5,'yanchor': 'top'}, font=dict(size=15), margin= dict(l=0,r=0,t=70), legend=dict(yanchor = 'bottom',xanchor='left', orientation = 'h',y = 1,x = 0))

    def grap_f4_lina_mes(self,f4_linea_mes):
        orden = ord_mes(f4_linea_mes,'mes')
        colores = unif_colors(f4_linea_mes,'mes')
        self.fig_f4_linea_mes = px.bar(f4_linea_mes, x = var_f4['desc_linea'],y = var_f4['costo'], text = var_f4['costo'],color = 'mes', # TODO leer desde var_f4.
        text_auto ='.2s', barmode = 'group', labels = {var_f4['costo']:'Costo total',
        var_f4['desc_linea']:'Línea','mes':'Mes'}, color_discrete_map = colores, category_orders = {'mes':orden}) # TODO leer desde var_f4
        self.fig_f4_linea_mes.update_layout(xaxis_categoryorder = 'total descending', uniformtext_minsize = 6, uniformtext_mode = 'show', legend = dict(yanchor = 'bottom',xanchor = 'left', orientation = 'h',y = 1), title = {'text':'Top 10 F4s por línea y mes','y':0.99,'x':0.5,'yanchor': 'top'}, margin=dict(t=100,l=0,r=0),font=dict(size=14))
        self.fig_f4_linea_mes.update_yaxes(range = [0, f4_linea_mes[var_f4['costo']].max() + (f4_linea_mes[var_f4['costo']].max() * 0.25)], constrain = 'domain')
        self.fig_f4_linea_mes.update_traces(textangle = 90, textposition = 'outside')
    
    def grap_f4_linea_motivo(self,linea_motivo):
        linea_motivo = linea_motivo.groupby([var_f4['desc_linea'],'Posible Causa'])[var_f4['costo']].sum().reset_index().sort_values(var_f4['costo'], ascending = False) # TODO leer desde var_f4
        self.fig_f4_linea_motivo = px.bar(linea_motivo, x = var_f4['costo'], y = var_f4['desc_linea'],text = var_f4['costo'] ,color = 'Posible Causa' ,text_auto = '.2s',labels = {var_f4['costo']: 'Costo total','Posible Causa':'Causa','local_agg':'Local','descripcion_linea':'Línea'}) # TODO leer desde var_f4
        self.fig_f4_linea_motivo.update_layout(yaxis_categoryorder = 'total ascending',title = 'F4 por línea con motivo', font_size = 18,legend = dict( y = 0.3, xanchor = 'left', x = 0.3))
        self.fig_f4_linea_motivo.update_xaxes(range = [0,linea_motivo[var_f4['costo']].max() + (linea_motivo[var_f4['costo']].max() * 1.5)], constrain = 'domain')

    def grap_f4_linea_local(self,linea_local):
        color = unif_colors(linea_local,'local_agg') # TODO leer desde var_f4
        self.fig_lin_local = px.bar(linea_local, x = 'descripcion_linea', y = var_f4['costo'],text_auto = '.2s', text = var_f4['costo'] , # TODO leer desde var_f4
        barmode ='group',color = 'local_agg',title = 'F4 por línea por local', labels = {'descripcion_linea':'Línea',var_f4['costo']:'Total costo', # TODO leer desde var_f4
        'local_agg':'Local'}, color_discrete_map = color) # TODO leer desde var_f4
        self.fig_lin_local.update_layout(xaxis_categoryorder = 'total descending', uniformtext_minsize = 10,uniformtext_mode = 'show',legend = dict(yanchor = 'bottom', xanchor = 'left', orientation = 'h',y = 1))
        self.fig_lin_local.update_yaxes(range = [0, linea_local[var_f4['costo']].max() + (linea_local[var_f4['costo']].max() * 0.25)], constrain = 'domain')
        self.fig_lin_local.update_traces(textangle = 90, textposition= 'outside')

    def grap_f4_top_10_marcas(self,top_10_marca):
        color = unif_colors(top_10_marca,'mes') # TODO leer desde var_f4
        orden = ord_mes(top_10_marca,'mes') # TODO leer desde var_f4
        self.fig_f4_marca = px.bar(top_10_marca, x = 'Marca',y = var_f4['costo'],text = var_f4['costo'],color = 'mes', # TODO leer desde var_f4
        text_auto = '.2s', barmode = 'group', labels = {var_f4['costo']:'Costo total','descripcion_linea':'Linea','mes':'Mes'}, color_discrete_map = color, category_orders = {'mes':orden}) # TODO leer desde var_f4
        self.fig_f4_marca.update_layout(xaxis_categoryorder = 'total descending', uniformtext_minsize = 6,uniformtext_mode ='show',legend = dict(yanchor = 'bottom',xanchor = 'left', orientation  = 'h',y = 1),font=dict(size=15),title={'text': 'Top 10 F4s Avería por marca y mes','y':0.99,'x':0.5,'yanchor': 'top'}, margin=dict(r=0,l=0,t=100))
        self.fig_f4_marca.update_yaxes(range = [0, top_10_marca[var_f4['costo']].max() + (top_10_marca[var_f4['costo']].max() * 0.25)], constrain = 'domain')
        self.fig_f4_marca.update_traces(textangle = 90, textposition = 'outside')
    
    def grap_marca_esp(self):
        self.marc = 'Samsung'
        marca = self.f4_2022_averia.loc[self.f4_2022_averia.Marca == self.marc]
        top_5_loc = marca.groupby(['desc_local','mes'])[var_f4['costo']].sum().sort_values(ascending=False).reset_index()['desc_local'].unique()[0:5]                                                             
        grup_marca = marca.groupby(['desc_local','mes'])[var_f4['costo']].sum().sort_values(ascending=False).reset_index()
        grup_marca = grup_marca.loc[grup_marca['desc_local'].isin(top_5_loc)]
        set_columns_sum(grup_marca,'mes',var_f4['costo'])
        set_columns_sum(grup_marca,'desc_local',var_f4['costo'])
        color = unif_colors(grup_marca,'mes')
        self.fig_marca_locales = px.bar(grup_marca, x = 'desc_local',y = var_f4['costo'],text = var_f4['costo'],color = 'mes',text_auto = '.2s',labels = {var_f4['costo']:'Costo total','desc_local':'Local','mes':'Mes'}, color_discrete_map = color)
        self.fig_marca_locales.update_layout(xaxis_categoryorder = 'total descending', uniformtext_minsize = 10,uniformtext_mode ='show',legend= dict(yanchor = 'bottom',xanchor = 'left', orientation = 'h',y = 1),font=dict(size=15),title={'text':f'{self.marc} por local','y':0.99,'x':0.5,'yanchor': 'top'}, margin=dict(r=0,l=0,t=100))
        self.fig_marca_locales.update_yaxes(range = [0, grup_marca[var_f4['costo']].max() + (grup_marca[var_f4['costo']].max() * 0.25)], constrain ='domain')
        self.fig_marca_locales.update_traces(textangle = 90, textposition = 'outside')
    
    def grap_marca_averia(self, marcas_calidad):
        orden = ord_mes(marcas_calidad,'mes') # TODO leer desde var_f4
        color = unif_colors(marcas_calidad,'mes') # TODO leer desde var_f4
        self.fig_marcas_calidad = px.bar(marcas_calidad, x = 'Marca', y = var_f4['costo'], barmode = 'group',color = 'mes',text_auto = '.2s', color_discrete_map = color, category_orders = {'mes':orden}, labels = {var_f4['costo']:'Total costo','mes':'Mes'}) # TODO leer desde var_f4
        self.fig_marcas_calidad.update_layout(xaxis_categoryorder = 'total descending', uniformtext_minsize = 10,uniformtext_mode = 'show',legend = dict(yanchor = 'bottom',xanchor = 'left', orientation = 'h',y = 1),font=dict(size=15),title={'text':"Top 10 F4's marcas por calidad",'y':0.99,'x':0.5,'yanchor': 'top'}, margin=dict(r=0,l=0,t=100))
        self.fig_marcas_calidad.update_yaxes(range = [0, marcas_calidad[var_f4['costo']].max() + (marcas_calidad[var_f4['costo']].max() * 0.25)], constrain = 'domain')
        self.fig_marcas_calidad.update_traces(textangle = 90, textposition = 'outside')

    def grap_pant_rotas(self,f4_pant_rotas):
        color = unif_colors(f4_pant_rotas,'mes') # TODO leer desde var_f4
        orden = ord_mes(f4_pant_rotas,'mes') # TODO leer desde var_f4
        orden_y = ord_num(f4_pant_rotas, 'Marca',var_f4['costo'])
        self.fig_pant_rotas = px.bar(f4_pant_rotas, x = 'Marca', y = var_f4['costo'],color = 'mes',text_auto = '.2s', category_orders = {'mes' : orden, 'Marca' : orden_y}, labels = {var_f4['costo']:'Total costo','mes':'Mes'}, color_discrete_map = color) # TODO leer desde var_f4
        self.fig_pant_rotas.update_layout(legend = dict(yanchor = 'bottom',xanchor = 'left', orientation = 'h',y = 1),font=dict(size=15),title={'text':'Top 10 F4\'s marcas por calidad','y':0.99,'x':0.5,'yanchor': 'top'}, margin=dict(r=0,l=0,t=100))


    def save_grap(self):  
        self.fig_torta_local.write_image(f'{self.path}/{self.fecha_corte}_torta.png', engine = 'orca') 
        self.ten_creac_x_año.write_image(f'{self.path}/{self.fecha_corte}_tendencia_creacion_f4_x_años.png', width = 800, height = 450, engine = 'orca')
        self.grafica_f4_sem.write_image(f'{self.path}/{self.fecha_corte}_grafica_f4_sem.png', width = 700, height = 500, engine = 'orca')
        self.graf_f4_pos_causa.write_image(f'{self.path}/{self.fecha_corte}_clasificacion_posibles_causas_22.png', width = 1300, height = 700, engine = 'orca') 
        self.fig_clasificado.write_image(f'{self.path}/{self.fecha_corte}_grafica_total.png', height = 600,  width = 700, engine='orca')
        self.fig_clasificado_local.write_image(f'{self.path}/{self.fecha_corte}_grafica_total_por_local.png', height = 600,  width = 1000,engine = 'orca')
        self.fig_clas_mes_local.write_image(f'{self.path}/{self.fecha_corte}_grafica_total_por_mes.png', height = 500,  width = 500,engine = 'orca')
        self.f4_mespc.write_image(f'{self.path}/{self.fecha_corte}_tienda_mes_motivo.png', height = 500,  width = 700,engine = 'orca')
        self.f4_mespc_cd.write_image(f'{self.path}/{self.fecha_corte}_cd_mm.png', engine = 'orca')
        self.fig_torta_linea.write_image(f'{self.path}/{self.fecha_corte}_torta_linea.png', height = 800,  width = 700,engine = 'orca')
        self.fig_f4_linea_mes.write_image(f'{self.path}/{self.fecha_corte}_grafica_linea_x_mes.png', height = 700,  width = 900,engine = 'orca')
        self.fig_f4_linea_motivo.write_image(f'{self.path}/{self.fecha_corte}_f4_linea_motivo.png', height = 800,  width = 1000,engine = 'orca')
        self.fig_lin_local.write_image(f'{self.path}/{self.fecha_corte}_linea_local.png', height = 700,  width = 800, engine = 'orca')
        self.fig_f4_marca.write_image(f'{self.path}/{self.fecha_corte}_grafica_averia_x_mes_y_marca.png', height = 900,  width = 900,engine = 'orca')
        self.fig_marca_locales.write_image(f'{self.path}/{self.fecha_corte}_{self.marc}_local.png', height = 600,  width = 500, engine = 'orca')
        self.fig_marcas_calidad.write_image(f'{self.path}/{self.fecha_corte}_marca_calidad.png', height = 700,  width = 800, engine = 'orca')
        self.fig_pant_rotas.write_image(f'{self.path}/{self.fecha_corte}_pantallas_rotas.png', height = 500,  width = 800, engine = 'orca')
        self.f4_mespc_tot.write_image(f'{self.path}/{self.fecha_corte}_mes_f4_motivo_compañia.png', height = 700,  width = 800, engine = 'orca')
        self.tb_averias.write_image(f'{self.path}/{self.fecha_corte}_tabla_averias.png',height = 370,  width = 900, engine = 'orca')
        self.tb_p_rotas.write_image(f'{self.path}/{self.fecha_corte}_tabla_pantallas_rotas.png',height = 280,  width = 900, engine = 'orca')
        self.tb_calidad.write_image(f'{self.path}/{self.fecha_corte}_tabla_calidad.png',height = 370,  width = 900, engine = 'orca')
        self.tb_loc_pant.write_image(f'{self.path}/{self.fecha_corte}_tabla_loc_pant.png',height = 600,  width = 400, engine = 'orca')
        self.tb_prod_pant.write_image(f'{self.path}/{self.fecha_corte}_tabla_prod_pant.png',height = 340,  width = 600, engine = 'orca')
        
def make_tables_top_10(df,type='top_10'):
    if type == 'top_10':
        pt_df = df.pivot_table(index='Marca', columns='mes',values='total_precio_costo',aggfunc='sum',margins_name='Total',fill_value=0,margins=True).reset_index()
        pt_df = pd.concat([pt_df.loc[pt_df.Marca!= 'Total'].sort_values('Total',ascending=False), pt_df.loc[pt_df.Marca=='Total']]) 
        pt_df = pt_df[['Marca']+ord_mes(df,'mes')+['Total']]
    elif type == 'loc':
        pt_df = aux.pivot_table(index='desc_local',values='total_precio_costo',aggfunc='sum',margins=True, margins_name='Total').reset_index()
        pt_df.rename(columns={'desc_local':'Local','total_precio_costo':'Total'},inplace=True)
        pt_df = pd.concat([pt_df.loc[pt_df['Local']!= 'Total'].sort_values('Total',ascending=False), pt_df.loc[pt_df['Local']=='Total']])
    elif type == "prod":
        pt_df = aux.pivot_table(index="descripcion_producto",values="total_precio_costo",aggfunc="sum").reset_index().sort_values("total_precio_costo",ascending=False)
        pt_df.rename(columns={"descripcion_producto":"Producto","total_precio_costo":"Total"},inplace=True)
        pt_df = pt_df.head(10)

    columns = pt_df.columns.to_list()
    listado = []
    for i in columns:
        listado.append(pt_df[i].tolist())
    font_color =  ['rgb(0,0,0)' if x == 'Total' else 'rgb(0,0,0)' for x in listado[0]]
    color_fill=  ['rgb(229,236,246)' if x == 'Total' else 'rgb(255,255,255)' for x in listado[0]]
    fig = go.Figure(data=[go.Table(header=dict(values = pt_df.columns.to_list(),font=dict(size=14,color=['rgb(0,0,0)'], family='Arial Black'),line = dict(color='rgb(50,50,50)'),fill=dict(color='rgb(229,236,246)')),
                    cells = dict(values=listado,
                    format = [None, '$.2s'],font = dict(size = 13, color = [font_color]),align='center', height = 30,fill= dict(color=[color_fill]),line = dict(color='rgb(50,50,50)')))
                        ])
    fig.update_layout( margin = dict(r=1,l=0,t=0,b=0))
    return fig
    
def f4_figs(df, pc_order, titulo):
    orden = ord_mes(df,'mes') # TODO leer desde var_f4
    colores = unif_colors(df,'mes') # TODO leer desde var_f4
    fig = px.bar(df, x='Posible Causa', y=var_f4['costo'], color='mes', barmode='group', #title=titulo,  # TODO leer desde var_f4
                text= var_f4['costo'], text_auto=',.2s', category_orders={'mes':orden, 'Posible Causa':pc_order},color_discrete_map = colores, # TODO leer desde var_f4
                labels={'mes':'Mes',var_f4['costo']: 'Total costo', 'Posible Causa':'Posible causa'}) # TODO leer desde var_f4
    fig.update_layout(xaxis_categoryorder = 'total descending', uniformtext_minsize = 10, uniformtext_mode='show', legend=dict(yanchor='bottom',xanchor='left', orientation = 'h',y=1), font=dict(size=15),title={'text': titulo,'y':0.99,'x':0.5,'yanchor': 'top'}, margin=dict(t=100))
    fig.update_yaxes(range=[0, df[var_f4['costo']].max() + (df[var_f4['costo']].max() * 0.40)], constrain='domain')
    fig.update_traces(textangle=90, textposition= 'outside')
    return fig
