from os import mkdir,listdir 
import constants as const
import pandas as pd 
import plotly.graph_objects as go
from data import var_global
path = var_global["path_cortes"]


def set_columns_sum(base, var, column):    
    lista = base.loc[base[var].notna()][var].unique()
    gb_var = base.groupby(var)[column].sum().reset_index()
    gb_var.set_index(var, inplace=True)
    for item in lista:
        base.loc[base[var]==item, var] = f'{item} ${round(gb_var.loc[item, column]/1e6):,.0f}M'
    return base 

def set_columns_nunique(base, var, column):    
    lista = base.loc[base[var].notna()][var].unique()
    gb_var = base.groupby(var)[column].sum().reset_index()
    gb_var.set_index(var, inplace=True)
    for item in lista:
        base.loc[base[var]==item, var] = f'{item} {round(gb_var.loc[item, column]):,.0f}'
    return base 

def generate_structure(dt_string):
    if f"{dt_string}_corte" not in listdir(var_global['path_cortes']):
        mkdir(f"{var_global['path_cortes']}/{dt_string}_corte")
        mkdir(f"{var_global['path_cortes']}/{dt_string}_corte/images")
        mkdir(f"{var_global['path_cortes']}/{dt_string}_corte/images/f3")
        mkdir(f"{var_global['path_cortes']}/{dt_string}_corte/images/f4")
        mkdir(f"{var_global['path_cortes']}/{dt_string}_corte/images/f11")
        mkdir(f"{var_global['path_cortes']}/{dt_string}_corte/classifier")
        mkdir(f"{var_global['path_cortes']}/{dt_string}_corte/images/f5")
        mkdir(f"{var_global['path_cortes']}/{dt_string}_corte/images/f12")
    else:
        pass
    
def unif_colors(df ,column):
    unique = df[column].unique()
    dic = {}
    for i in unique:
        for local in const.p_colores:
            if local in i:
                dic[i] = const.p_colores[local]
    return dic

def ord_mes(df,column,f = "general", orden = None):
    if f == "general":
        meses = ["Inv","Ene","Jan","Feb","Mar","Abr","Apr","May","Jun","Jul","Ago","Aug","Sep","Oct","Nov","Dic","Dec"]
    elif f == "f3":
        meses = orden
    elif f == "ant":
        meses = ['Menor a 30', '31 a 60', '61 a 90','91 a 120', '121 a 180','Mayor a 121', 'Mayor a 181','Total'] 
    col_mes = df[column].unique()
    list_mes = []
    for mes in meses:
        for i in col_mes: 
            if mes in i:
                list_mes.append(i)
    return list_mes
    
def ord_num(df,column,colum_num):
    return df.groupby(column)[colum_num].sum().sort_values(ascending=False).reset_index()[column].unique()

def make_tables(df,rows,column,sum, f = None ,types = None):
    pt_df = df.pivot_table(index = rows, columns = column, values = sum, aggfunc = "sum", margins = True,  margins_name = 'Total General', fill_value = 0).reset_index()
    if types == None:
        pt_df = pd.concat([pt_df.loc[pt_df[rows] != 'Total General'].sort_values('Total General',ascending = False), pt_df.loc[pt_df[rows] == 'Total General']]) 
    if types == "meses":
        pt_df = pd.concat([pt_df.loc[pt_df[rows] != 'Total General'].sort_values('Total General',ascending = False), pt_df.loc[pt_df[rows] == 'Total General']]) 
        pt_df = pt_df[[rows] + ord_mes(df,column) + ['Total General'] ]
    elif types == "loc":
        pt_df.rename(columns={rows:'Local',sum:'Total General'},inplace=True)
        pt_df = pd.concat([pt_df.loc[pt_df['Local']!= 'Total General'].sort_values('Total General',ascending=False), pt_df.loc[pt_df['Local']=='Total General']])
    elif types == "prod":
        pt_df.rename(columns={rows:"Producto",sum:"Total"},inplace=True)
        pt_df.sort_values('Total',ascending=False, inplace = True)
        pt_df = pt_df.iloc[1:11]
    elif types == "ant":
        ord_antiguedad = ord_mes(df, 'age', 'ant')
        ord_antiguedad.insert(0, rows)
        ord_antiguedad.append('Total General')
        pt_df = pt_df[ord_antiguedad]
        set_col_riesgo(pt_df, f, rows)
        ord_antiguedad = ord_mes(df, 'age', 'ant')
        ord_antiguedad.insert(0, rows)
        ord_antiguedad.extend(['Total Riesgo', 'Total General'])
        pt_df = pt_df[ord_antiguedad]
    elif types == "local":
        pt_df.rename(columns={rows:"Local"},inplace=True)
        pt_df = pd.concat([pt_df.loc[pt_df["Local"] != 'Total General'].sort_values('Total General',ascending = False), pt_df.loc[pt_df["Local"] == 'Total General']])
        meses = ["Inv","Ene","Jan","Feb","Mar","Abr","Apr","May","Jun","Jul","Ago","Aug","Sep","Oct","Nov","Dic","Dec"]
        list_mes = []
        for mes in meses:
            for i in pt_df.columns: 
                    if mes in i:
                        list_mes.append(i)
        pt_df= pt_df[["Local"]+ list_mes +['Total General']]

    columns = pt_df.columns.to_list()
    listado = []
    for i in columns:
        listado.append(pt_df[i].tolist())
    for val in  listado[1:]:
        for i in enumerate(val):
           val[i[0]] =(i[1]/1e6)
    font_color =  ['rgb(0,0,0)' if x == 'Total' else 'rgb(0,0,0)' for x in listado[0]]
    color_fill=  ['rgb(229,236,246)' if x == 'Total' else 'rgb(255,255,255)' for x in listado[0]]
    fig = go.Figure(data=[go.Table(header=dict(values = pt_df.columns.to_list(),font=dict(size=14,color=['rgb(0,0,0)'], family='Arial Black'),line = dict(color='rgb(50,50,50)'),fill=dict(color='rgb(229,236,246)')),
                    cells = dict(values=listado,
                    format =  [None,'$,.0f'],font = dict(size = 13, color = [font_color]),align='center', height = 23,fill= dict(color=[color_fill]),line = dict(color='rgb(50,50,50)')))
                        ])
    fig.update_layout( margin = dict(r=1,l=1,t=0,b=0))
    return fig

def set_antiguedad(df, fecha_column, tipo):
    if tipo == 'f11':
        df = set_age(df,'DIAS','age')
    elif tipo == 'f3':
        for i in fecha_column:
            df[f'DIAS_{i}'] = df[i].max() - df[i]
            df[f'DIAS_{i}'] = df[f'DIAS_{i}'].apply(lambda x :x.days )
            df = set_age(df,f'DIAS_{i}', f'age_{i}')
        df.loc[df['descripcion6'] == 'enviado', 'age'] = df.loc[df['descripcion6'] == 'enviado', 'age_fecha_envio' ] 
        df.loc[df['age'].isna() , 'age'] = df.loc[df['age'].isna(), 'age_fecha_reserva']    
    if 'Mayor a 181' not in df[f'age'].unique():
        df[f'age'].replace('121 a 180' , 'Mayor a 121', inplace=True)
    return df

def set_age(df, column, age):
    df.loc[df[column] <30, age] = 'Menor a 30' 
    df.loc[(df[column] >= 30) & (df[column]<=60), age] ='31 a 60'
    df.loc[(df[column] > 60) & (df[column]<=90), age] ='61 a 90'
    df.loc[(df[column] > 90) & (df[column]<=120), age] ='91 a 120'
    df.loc[(df[column] > 120)&(df[column]<=180), age]='121 a 180'
    df.loc[(df[column] > 180), age] ='Mayor a 181'
    return df

def set_col_riesgo(df,f,rows):
    if f == 'f11':
        col = 4
    else:
        col = 2
    lista_col = df.loc[df[rows]!= 'Total'].iloc[:,col:-1].columns
    df['Total Riesgo'] = 0
    for i in range(len(lista_col)):
        df['Total Riesgo'] = df['Total Riesgo'] + df[lista_col[i]]