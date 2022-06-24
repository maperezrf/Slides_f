from config.user_path import  path_ea, path_ea

var_global ={'path_cortes':f'{path_ea}/SEGUIMIENTO-FS/cortes',
'path_ppts':f'{path_ea}/SEGUIMIENTO-FS/presentaciones/'}

var_main = {'pah_plantilla': f'{path_ea}/SEGUIMIENTO-FS/repositorio_fs/plantilla_seg_fs.pptx'}

var_f11 = {
    'path_df': f'{path_ea}/DATA/F11/',
    'trend_path': f'{path_ea}/SEGUIMIENTO-FS/repositorio_fs/tendencias_f11.xlsx', 
    'f11_id':'NRO_F11',
    'propietario':'PROPIETARIO',
    'estado':'ESTADO',
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
    'tipo_f11_x_grafica':['RETIRO F12','S.TECNICO' ], 
    'dias':'DIAS', 
    'graf_monto' : ['_f11_empresa_abiertos_sede_monto.png','_f11_trend_CD.png','_f11_trend_CD mayores a 90 días.png','_f11_trend_Tiendas & DVD.png','_f11_trend_Tiendas & DVD mayores a 90 días.png'],
    'graf_cant' : ['_f11_empresa_abiertos_sede_cantidad.png','_f11_tcant_CD.png','_f11_tcant_CD mayores a 90 días.png','_f11_tcant_Tiendas & DVD.png','_f11_tcant_Tiendas & DVD mayores a 90 días.png'],
    'tab_emp' : ['tb_emp_gral.png','tb_emp_ant.png'],
    'tab_emp_loc' : ['tb_emp_cd.png','tb_emp_no_cd.png'],
    'tab_cl' : ['tb_cl_gral.png','tb_cl_ant.png'],
    'tab_cl_loc' :  ['tb_cl_cd.png','tb_cl_no_cd.png'],
    }

var_f4 = {
    'path_df':f"{path_ea}/DATA/F4/",
    'path_f4_2021':f'{path_ea}/SEGUIMIENTO-FS/repositorio_fs/f4_2021.csv',
    'path_df_clas':'output/220406_corte/classifier/220406_f4_clasificado.csv',
    'f4_id':'nro_red_inventario',
    'marcas_df':f'{path_ea}/SEGUIMIENTO-FS/repositorio_fs/Marcas.xlsx',
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
    'path_df':f'{path_ea}/DATA/F3/',
    'trend_path':f'{path_ea}/SEGUIMIENTO-FS/repositorio_fs/tendencias_f3.xlsx' ,
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
    'abiertos': ['enviado'],
    'cerrados' : ['anulado', 'confirmado'],
    'tipo_tp' : ['Producto','Market place']
}
