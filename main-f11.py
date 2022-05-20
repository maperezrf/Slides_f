
from time import time
from traceback import print_tb
from f11 import F11
from general import generate_structure
from datetime import datetime, timedelta

df_name = input('Ingrese nombre de archivo de f11 abiertos .csv: ')
corte = input('Ingrese fecha corte (AAMMDD): ')

frizq = datetime.strptime('2022-02-20', '%Y-%m-%d')
frder = datetime.strptime(corte, '%Y-%m-%d') + timedelta(days=10)
rango_de_fechas = [frizq, frder]

generate_structure(corte)

f11 = F11(rango_de_fechas, corte, df_name)

def menu_f11():
    print('# -------------------------')
    print('# Menú F11')
    print('  Seleccione una opción: ')
    print(f'   1. Generar corte de F11 (último corte = {f11.get_max_trend_date()})')
    print('   2. Gráficar f11 y tendencias')
    print('   0. Salir')


selection = None
while selection != '0': 
    menu_f11()
    selection = input('Rta: ')

    if selection == '1':
        f11.get_f11_cutoff()
    elif selection =='2': 
        f11.f11_resfil()
        f11.tendencias()