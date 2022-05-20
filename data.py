from config.user_path import  user 

var_global ={
    'path_cortes':f'{user}/General/SEGUIMIENTO-FS/cortes'
}

var_main = {
    'pat_plantilla':f'{user}/General/SEGUIMIENTO-FS/repositorio_fs/plantilla_seg_fs.pptx'
    }


var_f11 = {
    'path_df': f'{user}/General/DATA/F11/',
    'trend_path': f'{user}/General/SEGUIMIENTO-FS/repositorio_fs/tendencias_f11.xlsx', 
    'f11_id':'NRO_F11',
    'propietario':'PROPIETARIO',
    'estado':'ESTADO',
    'dias':'DIAS',
    'prop_empresa':'EMPRESA',
    'prop_cliente':'CLIENTE',
    'fech_creacion':'FECHA_CREACION',
    'estados_abiertos':['Despachado','Espera Retiro Clte.','Ingresado','Entrega parcial'],
    'fecha_inicial':'2021-01-01', 
    'mes':'MES', 
    'costo':'TOTAL_COSTO',
    'grupo':'GRUPO',
    'fecha_corte':'FECHA_CORTE', 
    'servicio':'SERVICIO',
    'tipo_f11_x_grafica':['RETIRO F12','S.TECNICO' ]}

var_f4 = {
    'path_df':f"{user}/General/DATA/F4/",
    'path_df_clas':'output/220406_corte/classifier/220406_f4_clasificado.csv',
    'f4_id':'nro_red_inventario',
    'marcas_df':f'{user}/General/SEGUIMIENTO-FS/repositorio_fs/Marcas.xlsx',
    'fechas' : ['fecha_creacion', 'fecha_reserva'],
    'fecha_res' : 'fecha_reserva',
    'tipo_redinv' : 'tipo_redinv',
    'estado' : 'estado',
    'destino' : 'destino',
    'desccentro_e_costo' : 'desccentro_e_costo',
    'local' : 'local',
    'costo' : 'total_precio_costo',
    'desc_linea': 'descripcion_linea'
}

var_f3 = { 
    'path_df':f'{user}/General/DATA/F3/',
    'trend_path':f'{user}/General/SEGUIMIENTO-FS/repositorio_fs/tendencias_f3.xlsx' ,
    'fecha_res':'fecha_reserva',
    'fecha_envio':'fecha_envio',
    'fecha_anulacion':'fecha_anulacion',
    'fecha_confirmacion':'fecha_confirmacion',
    'estado':'descripcion6',
    'tipo_producto':'tipo_producto',
    'costo':'cant*costoprmd',
    'f3_id':'nro_devolucion',
    'local': 'local',
    'fecha_inicial':'2021-01-01',
    'abiertos': ['enviado', 'reservado'],
    'cerrados' : ['anulado', 'confirmado'],
    'tipo_tp' : ['Producto','Market place']
}
