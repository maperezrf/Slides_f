from os import mkdir,listdir 
from datetime import datetime
import constants as const


dt_string = datetime.now().strftime('%y%m%d')
path = "output"

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

def generate_structure():
    if f"{dt_string}_corte" in listdir(path):
        if "images" not in listdir(f"{path}/{dt_string}_corte"):
            mkdir(f"{path}/{dt_string}_corte/images")
        else:
            pass
    if f"{dt_string}_corte" not in listdir(path):
        print("por que aca")
        mkdir(f"{path}/{dt_string}_corte")
        mkdir(f"{path}/{dt_string}_corte/images")
    else:
        pass
    return f"{path}/{dt_string}_corte"

def unif_colors(df ,column):
    unique = df[column].unique()
    dic = {}
    for i in unique:
        for local in const.p_colores:
            if local in i:
                dic[i] = const.p_colores[local]
    return dic

def ord_mes(df,column):
    meses = ["Ene","Feb","Mar","Abr","May","Jun","Ago","Sep","Oct","Nov","Dic"]
    col_mes = df[column].unique()
    list_mes = []
    for mes in meses:
        for i in col_mes: 
            if mes in i:
                list_mes.append(i)
    return list_mes