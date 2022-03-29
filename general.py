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