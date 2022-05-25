
from f3 import F3
from f4_classifier import CLASSIFIER_F4
from f4 import F4
from datetime import datetime
from general import generate_structure
from ppt import PPTPY

# Datos a modificar antes de la ejecución del código
fecha_corte = input("Ingrese la fecha de corte, formato -> AAAA-MM-DD: ") # TODO pasar a formato de fecha 
f3_file = input('Ingrese nombre de archivo de f3 .csv: ')
f4_file = input('Ingrese nombre de archivo de f4 .csv: ')
f11_file = input('Ingrese nombre de archivo de f11 abiertos .csv: ')
# Datos a modificar antes de la ejecución del código

generate_structure(fecha_corte)

# F3
f3 = F3(fecha_corte, f3_file)
path_f3 = f3.get_path()

# F4 Clasificador
f4_classifier = CLASSIFIER_F4(fecha_corte, f4_file)
f4_clasificada = f4_classifier.get_marca() #[x] pasar a método get_f4_classified() #PRIORITARIO=23MAYO

# F4
f4 = F4(f4_clasificada,fecha_corte)
path_f4 = f4.get_path() #[x] pasar a método get_path() #PRIORITARIO=23MAYO
f4_calcs = f4_classifier.calculos() 

# Generación de ppt
ppt = PPTPY(path_f3, path_f4, f4_calcs, fecha_corte)
ppt.slide_f3_costo() 
ppt.get_all_f4_slides()
ppt.save_ppt()
