from pptx import Presentation
from pptx.util import Cm,Pt
from data import  var_global,var_main
class PPTPY():
    path_f3 = ''
    path_f4 = ''
    fecha_corte = ''
    f4_data = []

    def __init__(self, pf3, pf4, f4cals, fc) -> None:
        self.path_f3 = pf3
        self.path_f4 = pf4
        self.fecha_corte = fc 
        self.f4_data = f4cals

        self.seguimiento_fs = Presentation(var_main['pah_plantilla'])  # Leer presentacion 
        for i in  range(2,17):
            self.update_date(i)

    def update_date(self, n_slide): 
        slide = self.seguimiento_fs.slides[n_slide]
        tb_corte = slide.shapes.add_textbox(Cm(0),Cm(17.43),width=Cm(1), height=Cm(0.1))
        text_corte = tb_corte.text_frame.add_paragraph() 
        text_corte.text = f"Corte {self.fecha_corte}"
        text_corte.font.size = Pt(12)    

    def slide_f3_costo(self):
        f3 = self.seguimiento_fs.slides[7]
        #Producto
        f3.shapes.add_picture(f"{self.path_f3}/{self.fecha_corte}_f3_abiertos_fecha_reserva.png", Cm(0.7), Cm(1.8), height=Cm(7.5)) 
        f3.shapes.add_picture(f"{self.path_f3}/{self.fecha_corte}_f3_tendencia_Producto.png", Cm(13),Cm(1.8), height=Cm(7.5)) 
        f3.shapes.add_picture(f"{self.path_f3}/{self.fecha_corte}_f3_cerrado_producto_costo.png", Cm(23), Cm(1.8), height=Cm(7.5))
        #Marketplace
        f3.shapes.add_picture(f"{self.path_f3}/{self.fecha_corte}_f3_abierto_sede.png", Cm(0.7), Cm(10.2), height=Cm(7.5)) 
        f3.shapes.add_picture(f"{self.path_f3}/{self.fecha_corte}_f3_tendencia_mkp.png", Cm(13), Cm(10.2), height=Cm(7.5)) 
        f3.shapes.add_picture(f"{self.path_f3}/{self.fecha_corte}_f3_cerrado_mkp_costo.png", Cm(23), Cm(10.2), height=Cm(7.5))

    def slide_f4(self):
        f4 = self.seguimiento_fs.slides[8]
        f4.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_tendencia_creacion_f4_x_años.png", Cm(2.01),Cm(0.58),width = Cm(16.17), height = Cm(9.08)   )
        f4.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_grafica_f4_sem.png", Cm(19.55), Cm(0.57), width = Cm(13.29), height = Cm(9.6))
        f4.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_grafica_total_por_mes.png", Cm(13.03), Cm(10.07), width = Cm(7.62), height = Cm(7.62)   )
        f4.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_torta.png", Cm(22.84), Cm(10.23), width = Cm(10), height = Cm(7.13))
        tb_reserva = f4.shapes.add_textbox(Cm(1.21),Cm(15.28),width=Cm(1), height=Cm(0.1))
        tx_text_reserva = tb_reserva.text_frame.add_paragraph() 
        tx_text_reserva.text = f"Reservado {self.f4_data[4]}"
        tx_text_reserva.font.size= Pt(14)
        
        corchete = f4.shapes.add_textbox(Cm(5.03),Cm(14.05),width=Cm(1), height=Cm(0.1))
        tx_corchete = corchete.text_frame.add_paragraph() 
        tx_corchete.text = "{"
        tx_corchete.font.size= Pt(66)

        estados = f4.shapes.add_textbox(Cm(5.87),Cm(14.6),width=Cm(1), height=Cm(0.1))
        tx_estados = estados.text_frame.add_paragraph() 
        tx_estados.text = f"Tienda {self.f4_data[1]}\nCD {self.f4_data[0]}\nDVD {self.f4_data[2]}\nVenta empresa {self.f4_data[3]}"
        tx_estados.font.size= Pt(12)

        registrados = f4.shapes.add_textbox(Cm(1.24),Cm(8.8),width=Cm(0.1), height=Cm(0.1))
        tx_registrados = registrados.text_frame.add_paragraph() 
        tx_registrados.text = f"Estado Registrado $21M < 7 días No han pasado a contabilidad,\nya informados a responsables\nUsuarios de creación:\n    -Jhonatan Beltran Velasquez\n   -Alexis Fabian Mestizo Parra"
        tx_registrados.font.size= Pt(13)

        registrados_m = f4.shapes.add_textbox(Cm(1.24),Cm(12.08),width=Cm(0.1), height=Cm(0.1))
        tx_registrados_m = registrados_m.text_frame.add_paragraph() 
        tx_registrados_m.text = f"Estado Registrado $2M >7 días No han pasado a contabilidad,\nya informados a responsables\nUsuarios de creación:\n  Jair Armando Rocha Vargas"
        tx_registrados_m.font.size= Pt(13)       

    def f4_pos_causa(self):
        f4_pos_causa = self.seguimiento_fs.slides[9]
        f4_pos_causa.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_clasificacion_posibles_causas_22.png", Cm(1.36),Cm(0.38),width = Cm(31.91), height = Cm(17.32))
        titulo = f4_pos_causa.shapes.add_textbox(Cm(0.4),Cm(-0.79),width=Cm(0.1), height=Cm(0.1))
        tx_titulo = titulo.text_frame.add_paragraph() 
        tx_titulo.text = "F4"
        tx_titulo.font.size= Pt(36)       

    def f4_mot_sede(self):
        f4_mot_sede = self.seguimiento_fs.slides[10]
        f4_mot_sede.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_grafica_total.png", Cm(0.66),Cm(2.32),width = Cm(17.41), height = Cm(14.81))
        f4_mot_sede.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_grafica_total_por_mes.png", Cm(22.38), Cm(1.01), width = Cm(7.62), height = Cm(7.62))
        f4_mot_sede.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_grafica_total_por_local.png", Cm(18.55), Cm(8.52), width = Cm(14.18), height = Cm(8.94))

    def f4_mes_moti(self):
        f4_mes_moti = self.seguimiento_fs.slides[11]

        f4_mes_moti.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_mes_f4_motivo_compañia.png", Cm(0.34),Cm(2.88),width = Cm(16.03), height = Cm(14.02))
        f4_mes_moti.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_cd_mm.png", Cm(19.5),Cm(0.61),width = Cm(11.59), height = Cm(8.27))
        f4_mes_moti.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_tienda_mes_motivo.png", Cm(19.13),Cm(9.19),width = Cm(11.72), height = Cm(8.38))

    def f4_linea_año(self):
        f4_linea_año = self.seguimiento_fs.slides[12]
        f4_linea_año.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_torta_linea.png", Cm(1.61),Cm(2.26),width = Cm(13.18), height = Cm(15.06))
        f4_linea_año.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_grafica_linea_x_mes.png", Cm(14.79),Cm(1.89),width = Cm(17.46), height = Cm(15.27))

    def f4_linea_motivo(self):
        f4_linea_motivo = self.seguimiento_fs.slides[13]
        f4_linea_motivo.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_f4_linea_motivo.png", Cm(0.21),Cm(2.39),width = Cm(16.47), height = Cm(13.19))
        f4_linea_motivo.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_linea_local.png", Cm(15.56),Cm(1.61),width = Cm(17.66), height = Cm(15.41))

    def f4_averias(self):
        f4_linea_motivo = self.seguimiento_fs.slides[14]
        f4_linea_motivo.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_grafica_averia_x_mes_y_marca.png", Cm(0),Cm(2.4),width = Cm(16.64), height = Cm(13.82))

    def f4_calidad(self):
        f4_calidad = self.seguimiento_fs.slides[15]
        f4_calidad.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_marca_calidad.png", Cm(0),Cm(2.4),width = Cm(16.64), height = Cm(13.82))

    def f4_panatallas_rotas(self):
        f4_panatallas_rotas = self.seguimiento_fs.slides[16]
        f4_panatallas_rotas.shapes.add_picture(f"{self.path_f4}/{self.fecha_corte}_pantallas_rotas.png", Cm(0),Cm(4.1),width = Cm(19.73), height = Cm(12.33))
    
    def get_all_f4_slides(self):
        self.slide_f4()
        self.f4_pos_causa()
        self.f4_mot_sede()
        self.f4_mes_moti()
        self.f4_linea_año()
        self.f4_linea_motivo()
        self.f4_averias()
        self.f4_calidad()
        self.f4_panatallas_rotas()

    def save_ppt(self):
        self.seguimiento_fs.save(f"{var_global['path_ppts']}/{self.fecha_corte}_seguimiento_fs.pptx")