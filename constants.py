tienda = [101, 108, 93, 6, 183, 25, 38, 53, 13, 43, 82,
          138, 72, 35, 60, 123, 98, 36, 19, 18, 50, 45,
          85, 56, 96, 322, 131, 139, 141, 143, 5, 142, 37,30]

cd = [9951, 9921, 3000, 9903, 2000, 2001,
      2002, 9970, 9901, 3002, 9905, 9961]

p_colores = {'TIENDA': 'rgb(22, 88, 134)', 
            'CD': 'rgb(117, 18, 138)', 
            'VENTA EMPRESA': 'rgb(184, 204, 21)',
            'DVD ADMINISTRATIVO': 'rgb(209, 128, 22)', 
            '2021': 'rgb(165, 170, 153)', 
            '2022': 'rgb(237, 173, 8)',
            'Inv' : 'rgb(99, 99, 99)',
            'Ene': 'rgb(84, 43, 114)',
            'Feb':  'rgb(78, 146, 49)',
            'Mar': 'rgb(170, 167, 57)',
            'Abr': 'rgb(229, 122, 70)',
            'Producto':'rgb(51, 102, 102)',
            'Market place':'rgb(204, 204, 51)',
            'Producto, sin soporte':'rgb(204, 103, 51)',
            'Fabricacion':'rgb(101, 51, 153)'}


fechas_inv =  {
  5: '2021-12-14',
  6: '2022-01-12',
  11: '2022-01-03',
  13: '2022-01-06',
  18: '2022-01-06',
  19: '2022-01-07',
  25: '2022-01-07',
  35: '2022-01-05',
  36: '2022-01-07',
  37: '2021-12-14',
  38: '2022-01-06',
  43: '2022-01-05',
  45: '2022-01-06',
  50: '2022-01-14',
  53: '2022-01-07',
  56: '2022-01-13',
  60: '2022-01-14',
  72: '2022-01-05',
  82: '2022-01-05',
  85: '2022-01-13',
  93: '2022-01-14',
  96: '2022-01-12',
  98: '2022-01-06',
  99: '2022-01-04',
  101: '2022-01-13',
  108: '2022-01-13',
  123: '2022-01-11',
  131: '2022-01-11',
  138: '2022-01-12',
  141: '2021-12-29',
  142: '2021-12-29',
  143: '2021-12-29',
  183: '2022-01-11',
  322: '2021-08-31',
  2000: '2022-01-13',
  2001: '2022-01-13',
  2002: '2022-01-13',
  3000: '2022-01-13',
  3001: '2022-01-03',
  3009: '2021-12-28',
  9901: '2022-01-13',
  9903: '2022-01-13',
  9905: '2022-01-06',
  9910: '2021-12-26',
  9921: '2022-01-13',
  9951: '2022-01-13',
  9961: '2022-01-09',
  9970: '2022-01-13'}



f4_merma =  ['46755223', '46670175', '46755285', '46765536', '46765512', '46765772', '46765765', '46765741', '46765734', '46765727', '46765710', '46765703', '46760067', '46760043', '46759962', '46755100', '46755094', '46755032', '46759924', '46759931', '46759948', '46756091', '46756077', '46756060', '46756015', '46755988', '46755971', '46755964', '46755957', '46755001', '46755926', '46755902', '46755896', '46755889', '46754998', '46755841', '46755834', '46755766', '46754967', '46755551', '46755483', '46755476', '46754943', '46755452', '46755438', '46755407', '46755391', '46755377', '46754936', '46755346', '46755322', '46754929', '46755315', '46754912', '46754882', '46754851', '46754844', '46739254', '46739247', '46739230', '46739209', '46739186', '46739179', '46739162', '46739148', '46739858', '46739834', '46739810', '46739803', '46739780', '46739087', '46739063', '46739049', '46739742', '46739735', '46739711', '46739704', '46739667', '46739650', '46739643', '46739636', '46739629', '46739582', '46739568', '46739551', '46739698', '46739605', '46738974', '46739384', '46739353', '46739322', '46733467', '46733450', '46733436', '46733429', '46733412', '46733382', '46733375', '46733269', '46733252', '46733153', '46721358', '46720894', '46720870', '46720856', '46669858', '46669872', '46720849', '46720832', '46720825', '46720818', '46720801', '46720764', '46720740', '46720733', '46720726', '46720467', '46720382', '46720375', '46720351', '46720344', '46720337', '46720320', '46720313', '46721303', '46720276', '46720252', '46720245', '46720238', '46721297', '46720207', '46720191', '46717207', '46717146', '46717139', '46717122', '46697103', '46697097', '46697073', '46670113'] 

f4_dup = ['46712042', '46712059', '46712066', '46712073', '46712080', '46712097', '46712103', '46712110', '46712127', '46712134', '46712141', '46712158', '46712165', '46712172', '46712189', '46712196', '46712202', '46712219', '46712226', '46712240', '46712264', '46712271', '46712288', '46712295', '46712301', '46712318', '46712325', '46712332', '46712349']

centro_costo_calidad = ['23114','23214','23314','23414','23514','23614','24214','24314','24514','24714','24814','24914','25014','25114','25414','25514','25614','25714','26114','26214','28014','29014','40050','40120','29814','35220','35320','39330','39340','39360','39370','39400','39430','39440','39450','39500','2340','24404']

centro_costo_tester = ['32220','32320','32420','32520','32620','32820','32920','33020','33120','33220','33320','33420','33520','33620','33820','33920','34020','34120','34420','40080']

centro_costo_recupero = ['27124','27514','27614','29214','29314']