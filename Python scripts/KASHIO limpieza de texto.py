# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 15:00:55 2023

@author: Joseph Montoya
"""

import pandas as pd
import os

#%% #LEYENDO EL DEL DÍA ACTUAL
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\KASHIO\\2023 AGOSTO\\18 agosto 2023')

kashio = pd.read_excel('DATA_CLIENTES_COOP.SANMIGUEL_20230818.xlsx',
                       dtype={'ID CLIENTE': str,
                              'TELEFONO': str,
                              'NUMERO DOCUMENTO': str})

kashio['ID CLIENTE'] = kashio['ID CLIENTE'].str.strip()
kashio['EMAIL'] = kashio['EMAIL'].str.strip()
kashio['EMAIL'] = kashio['EMAIL'].str.upper()

#%% #LEYENDO EL DEL DÍA ANTERIOR
ubi = 'C:\\Users\\sanmiguel38\\Desktop\\KASHIO\\2023 AGOSTO\\17 agosto 2023'
nombre = 'DATA_CLIENTES_COOP.SANMIGUEL_20230817.xlsx'

kashio_anterior = pd.read_excel(ubi + '\\' + nombre,
                                dtype={'ID CLIENTE': str,
                                       'TELEFONO': str,
                                       'NUMERO DOCUMENTO': str})

kashio_anterior['ID CLIENTE'] = kashio_anterior['ID CLIENTE'].str.strip()
kashio_anterior['EMAIL'] = kashio_anterior['EMAIL'].str.strip()
kashio_anterior['EMAIL'] = kashio_anterior['EMAIL'].str.upper()

kashio_anterior['EMAIL ANTERIOR'] = kashio_anterior['EMAIL']
kashio_anterior['ID ANTERIOR'] = kashio_anterior['ID CLIENTE']
kashio_anterior = kashio_anterior[['ID ANTERIOR', 'EMAIL ANTERIOR']]

#%% unimos con el del día anterior
kashio = kashio.merge(kashio_anterior, 
                      left_on=['ID CLIENTE'],
                      right_on=['ID ANTERIOR'],
                      how='left')

def limpieza(kashio): #revisar si esta vaina del pd.isna funciona
    if pd.isna(kashio['EMAIL ANTERIOR']):
        return kashio['EMAIL']
    else:
        return kashio['EMAIL ANTERIOR']
    
kashio['EMAIL ANTERIOR'] = kashio.apply(limpieza, axis=1)

kashio['EMAIL ANTERIOR'] = kashio['EMAIL ANTERIOR'].str.strip()
#%% LIMPIEZA DE DATOS:  
def correccion(row):
    palabras_a_buscar = ['GMAILCON', '\\', '/', 'FMAIL.COM', 'GAMIL.COM', 'GEMAIL.COM', 'GMAIL.COM.COM',
                         'HOTMAIL.COM/MECHIBL_2000@HOTMAIL.COM', 'GMAI.COM', 'GMIAL.COM', 'GNMAIL.COM', '@MAIL.COM',
                         'Ñ', ' ', '  ', '   ']
    
    if any(palabra in row['EMAIL ANTERIOR'] for palabra in palabras_a_buscar):
        return 'REGULARIZARCORREO@GMAIL.COM'
    else:
        return row['EMAIL ANTERIOR']
    
kashio['EMAIL ANTERIOR'] = kashio.apply(correccion, axis=1)

###############################################################################
###        PEGAR ESTO EN L2 =DERECHA(E2;(LARGO(E2)-ENCONTRAR("@";E2)))      ###
###############################################################################

kashio['EMAIL'] = kashio['EMAIL ANTERIOR']

kashio = kashio[kashio.columns[0:11]] #nos quedamos solo con las columnas necesarias

#%% CREACIÓN DEL PRIMER REPORTE CORREGIDO
'''esto habrá que comentarlo una vez que asumamos al 100% las funciones'''
nombre = "correo corregido.xlsx"
try:
    ruta = nombre
    os.remove(ruta)
except FileNotFoundError:
    pass

kashio.to_excel(nombre, index=False)

#%% ponemos los correos corregidos en el otro reporte (el más grande)

#PONEMOS EL NOMBRE DEL OTRO ARCHIVO
kashio_ampliado = pd.read_excel('DATA_RECIBOS_COOP.SANMIGUEL_20230818.xlsx',
                                dtype = {'ID CLIENTE (*)': str,
                                         'REFERENCIA': str,
                                         'ID ORDEN DE PAGO': str})

kashio_ampliado = kashio_ampliado.rename(columns={"NOMBRE": "NOMBRE_1"})
print(kashio_ampliado.shape[0])


kashio_ampliado = kashio_ampliado.merge(kashio, 
                                        left_on=['ID CLIENTE (*)'],
                                        right_on=['ID CLIENTE'],
                                        how='left')
print(kashio_ampliado.shape[0])
print('si sale diferente hay que investigar, posiblemente hay créditos duplicados')

#%% ARCHIVO FINAL PARA CONVERTIR A CSV

kashio_para_csv = kashio_ampliado[['ID CLIENTE', 'DOCUMENTO', 'NUMERO DOCUMENTO', 'NOMBRE', 'EMAIL',
                                   'TELEFONO', 'ESTADO', 'ID ORDEN DE PAGO', 'REFERENCIA', 'NOMBRE_1',
                                   'DESCRIPCION', 'MONEDA', 'MONTO', 'VENCIMIENTO', 'EXPIRACION']]

kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('Á', 'A')
kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('É', 'E')
kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('Í', 'I')
kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('Ó', 'O')
kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('Ú', 'U')

#%% EXPORTAR A CSV 

kashio_para_csv.to_csv('GeneracionData.csv', 
                       index=False, 
                       encoding='utf-8')

'''
nombre_archivo = 'datos.csv'
df = pd.read_csv(nombre_archivo, encoding='utf-8',
                 dtype = {'ID CLIENTE': str,
                          'TELEFONO': str,
                          'REFERENCIA': str})


df.to_csv('datos.csv', index=False, encoding='utf-8')
#BUSCAR LOS Ã‘ Y REEMPLAZARLOS POR Ñ
'''



