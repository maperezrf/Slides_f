
from pprint import pp
from f3 import F3
from f4_classifier import CLASSIFIER_F4
from f4 import F4
from f11 import F11
from datetime import datetime, timedelta
from general import generate_structure
from ppt import PPTPY

# Datos a modificar antes de la ejecución del código
fecha_corte = input("Ingrese la fecha de corte, formato -> AAAA-MM-DD: ") # TODO pasar a formato de fecha 

# Datos a modificar antes de la ejecución del código
fecha_riesgo_f3 = "2022-04-30" 

generate_structure(fecha_corte)

def menu_f11(f11_df):
    print('# -------------------------')
    print('# Menú F11')
    print('  Seleccione una opción: ')
    print(f'   1. Generar corte de F11 (último corte = {f11_df.get_max_trend_date()})')
    print('   2. Gráficar f11 y tendencias')
    print('   0. Salir')

def f3():
    f3_file = input('Ingrese nombre de archivo de f3 .csv (n, de lo contrario): ')
    if f3_file != 'n':
        f3 = F3(fecha_corte, f3_file)
        return f3.get_path()
    else:
        return ''

def f4():
    f4_file = input('Ingrese nombre de archivo de f4 .csv (n, de lo contrario): ')
    if f4_file != 'n':
        # F4 Clasificador
        f4_classifier = CLASSIFIER_F4(fecha_corte, f4_file)
        f4_clasificada = f4_classifier.get_marca()

        # F4
        f4 = F4(f4_clasificada,fecha_corte)
        path_f4 = f4.get_path()
        f4_calcs = f4_classifier.calculos() 
        return path_f4, f4_calcs
    else:
        return '', []

def f11():
    f11_file = input('Ingrese nombre de archivo de f11 abiertos .csv (n, de lo contrario): ')
    if f11_file != 'n':
        corte = input('Ingrese fecha corte (AAMMDD): ')
        frizq = datetime.strptime('2022-02-20', '%Y-%m-%d')
        frder = datetime.strptime(corte, '%y%m%d') + timedelta(days=10)
        rango_de_fechas = [frizq, frder]
        f11 = F11(rango_de_fechas, corte, f11_file)
        
        selection = None
        while selection != '0': 
            menu_f11(f11)
            selection = input('Rta: ')
            if selection == '1':
                f11.get_f11_cutoff()
            elif selection =='2': 
                f11.f11_resfil()
                f11.tendencias()
        return 'path'
    else:
        return ''

def ppt(fc):
    
    path_f3 = f3()
    path_f4, f4_calcs = f4()
    path_f11 = f11()

    # Generación de ppt
    ppt = PPTPY(path_f3, path_f4, f4_calcs, fc)

    sel = input('Desea generar slides de F3: (y/n)')
    if sel=='y': ppt.slide_f3_costo() 

    sel = input('Desea generar slides de F4: (y/n)')
    if sel=='y': ppt.get_all_f4_slides()
    
    # Guardar ppt
    print('Guardando cambios...')
    ppt_path = ppt.save_ppt()
    print(f'PPT guardada en {ppt_path}')

ppt(fecha_corte)
