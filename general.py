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

def generate_structure(f):
    if f"{dt_string}_corte" not in listdir(path):
        mkdir(f"{path}/{dt_string}_corte")
        mkdir(f"{path}/{dt_string}_corte/images")
        mkdir(f"{path}/{dt_string}_corte/images/f3")
        mkdir(f"{path}/{dt_string}_corte/images/f4")
        mkdir(f"{path}/{dt_string}_corte/images/f11")
        mkdir(f"{path}/{dt_string}_corte/classifier")
    else:
        pass
    if f == "f11":
        return f"{path}/{dt_string}_corte/images/f11"
    elif f == "f4":
        return f"{path}/{dt_string}_corte/images/f4"
    elif f == "f3":
        return f"{path}/{dt_string}_corte/images/f3"
    elif f == "classifier":
        return f"{path}/{dt_string}_corte/classifier"




def unif_colors(df ,column):
    unique = df[column].unique()
    dic = {}
    for i in unique:
        for local in const.p_colores:
            if local in i:
                dic[i] = const.p_colores[local]
    return dic

def ord_mes(df,column,f = "general"):
    if f == "general":
        meses = ["Inv","Ene","Feb","Mar","Abr","May","Jun","Ago","Sep","Oct","Nov","Dic"]
    elif f == "f3":
        meses =['Dic 15', 'Dic 31','Ene 17','Ene 31','Mar 01','Mar 16','Mar 28','Abr 05','Abr 12']
    col_mes = df[column].unique()
    list_mes = []
    for mes in meses:
        for i in col_mes: 
            if mes in i:
                list_mes.append(i)
    return list_mes

def ord_num(df,column,colum_num):
    return df.groupby(column)[colum_num].sum().sort_values(ascending=False).reset_index()[column].unique()
