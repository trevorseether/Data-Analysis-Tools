# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 15:00:55 2023

@author: Joseph Montoya
"""

###############################################################################
###        PEGAR ESTO EN L2 =DERECHA(E2;(LARGO(E2)-ENCONTRAR("@";E2)))      ###
###############################################################################
# también hay que reemplazar las Ã‘ por Ñ


import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')
import calendar
import datetime

#%% UBICACIÓN DE LOS ARCHIVOS #################################################
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\KASHIO\\pruebita')
###############################################################################

#%% NOMBRE ARCHIVO PRINCIPAL
'NOMBRE DEL ARCHIVO DE HOY' ##########################################
ARCHIVO_HOY = 'DATA_CLIENTES_COOP.SANMIGUEL_20231026.xlsx'
######################################################################

#%%% lectura del archivo
kashio = pd.read_excel(ARCHIVO_HOY,
                       dtype = {'ID CLIENTE'       : str,
                                'TELEFONO'         : str,
                                'NUMERO DOCUMENTO' : str}
                       )

kashio['ID CLIENTE'] = kashio['ID CLIENTE'].str.strip()
kashio['EMAIL'] = kashio['EMAIL'].str.strip()
kashio['EMAIL'] = kashio['EMAIL'].str.upper()

columnas = list(kashio.columns)

#%%  lectura y merge con el del día anterior (obsoleto)
'''
#LEYENDO EL DEL DÍA ANTERIOR
ubi = 'C:\\Users\\sanmiguel38\\Desktop\\KASHIO\\2023 AGOSTO\\21 agosto 2023'
nombre = 'DATA_CLIENTES_COOP.SANMIGUEL_20230821.xlsx'

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

def limpieza(kashio): #si no hay 'email del día anterior' se coloca el del día actual
    if pd.isna(kashio['EMAIL ANTERIOR']):
        return kashio['EMAIL']
    else:
        return kashio['EMAIL ANTERIOR']
    
kashio['EMAIL ANTERIOR'] = kashio.apply(limpieza, axis=1)

kashio['EMAIL ANTERIOR'] = kashio['EMAIL ANTERIOR'].str.strip()
'''
#%% LIMPIEZA DE DATOS:
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM.PE'  , '@GMAIL.COM')    
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COM.COM' , '@GMAIL.COM')    
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAILCON'      , '@GMAIL.COM')    
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAI.COM'      , '@GMAIL.COM')    
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GGMIAL.COM'    , '@GMAIL.COM')    
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GNMAIL.COM'    , '@GMAIL.COM')    
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMAIL.COMN'    , '@GMAIL.COM')    
kashio['EMAIL'] = kashio['EMAIL'].str.replace('@GMNAIL.COM'    , '@GMAIL.COM')    
    
kashio['EMAIL ANTERIOR'] = kashio['EMAIL'] #si reactivamos las celdas anteriores, esto habría que eliminarlo

def correccion(row):
    palabras_a_buscar = ['GMAILCON', '\\', '/', 'FMAIL.COM', 
                         'GAMIL.COM', 'GEMAIL.COM', 'GMAIL.COM.COM',
                         'HOTMAIL.COM/MECHIBL_2000@HOTMAIL.COM', 
                         'GMAI.COM', 'GMIAL.COM', 'GNMAIL.COM', 
                         '@MAIL.COM', 'Ñ', ' ', '  ', '   ', 
                         'GMAIL.COMN', 'GMNAIL.COM', 'Á', 'É', 'Í', 'Ó', 'Ú']
    
    if any(palabra in row['EMAIL ANTERIOR'] for palabra in palabras_a_buscar):
        return 'REGULARIZARCORREO@GMAIL.COM'
    else:
        return row['EMAIL ANTERIOR']
    
kashio['EMAIL ANTERIOR'] = kashio.apply(correccion, axis=1)

###############################################################################
###        PEGAR ESTO EN L2 =DERECHA(E2;(LARGO(E2)-ENCONTRAR("@";E2)))      ###
###############################################################################
# también hay que reemplazar las Ã‘ por Ñ

kashio['EMAIL'] = kashio['EMAIL ANTERIOR']

kashio = kashio[columnas] #nos quedamos solo con las columnas necesarias

#%% REPORTE DE CLIENTES CORREGIDO PARA CHEQUEAR LOS CORREOS

nombre = "Correo corregido " + str(ARCHIVO_HOY[29:37]) + ".xlsx"
try:
    ruta = nombre
    os.remove(ruta)
except FileNotFoundError:
    pass

kashio.to_excel(nombre, index=False)

#%% ponemos los correos corregidos en el otro reporte (el más grande)

# AUTOMATICAMENTE LEERÁ EL SEGUNDO ARCHIVO
kashio_ampliado = pd.read_excel('DATA_RECIBOS_COOP.SANMIGUEL_' + str(ARCHIVO_HOY[29:37]) + '.xlsx',
                                dtype = {'ID CLIENTE (*)'   : str,
                                         'REFERENCIA'       : str,
                                         'ID ORDEN DE PAGO' : str}
                                )

kashio_ampliado = kashio_ampliado.rename(columns = {"NOMBRE" : "NOMBRE_1"})

valor1 = kashio_ampliado.shape[0]
print(kashio_ampliado.shape[0])

kashio_ampliado = kashio_ampliado.merge(kashio, 
                                        left_on=['ID CLIENTE (*)'],
                                        right_on=['ID CLIENTE'],
                                        how='left')
valor2 = kashio_ampliado.shape[0]
print(kashio_ampliado.shape[0])
if valor1 != valor2:
    print('si sale diferente hay que investigar, posiblemente hay créditos duplicados')
else:
    print('todo bien, no hay créditos duplicados')

#%% ARCHIVO FINAL PARA CONVERTIR A CSV

kashio_para_csv = kashio_ampliado[['ID CLIENTE', 'DOCUMENTO', 'NUMERO DOCUMENTO', 'NOMBRE', 'EMAIL',
                                   'TELEFONO', 'ESTADO', 'ID ORDEN DE PAGO', 'REFERENCIA', 'NOMBRE_1',
                                   'DESCRIPCION', 'MONEDA', 'MONTO', 'VENCIMIENTO', 'EXPIRACION']]

kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('Á', 'A')
kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('É', 'E')
kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('Í', 'I')
kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('Ó', 'O')
kashio_para_csv['NOMBRE'] = kashio_para_csv['NOMBRE'].str.replace('Ú', 'U')

kashio_para_csv['DOCUMENTO'] = 'OTHER'

kashio_para_csv['MONTO'] = kashio_para_csv['MONTO'].round(2)

kashio_para_csv['EXPIRACION'] = '31/12/2050'  #fecha arbitrariamente lejana (actualmente se está poniendo un str)
                                #pd.Timestamp('2050-12-31') si es que necesitaramos que esté en formato DateTime

#%% VERIFICADOR DE FECHAS DE VENCIMIENTO
# Por lo menos debemos tener hasta fechas del fin de mes actual
kashio_para_csv['VENCIMIENTO parseado'] = pd.to_datetime(kashio_para_csv['VENCIMIENTO'])

# Obtén la fecha actual
fecha_actual = datetime.date.today()

# Obtiene el último día del mes
ultimo_dia_del_mes = datetime.date(fecha_actual.year, 
                                   fecha_actual.month, 
                                   calendar.monthrange(fecha_actual.year, 
                                                       fecha_actual.month)[1])

# Verifica si estás en diciembre
if fecha_actual.month == 12:
    # Si es diciembre, configura el mes al próximo año y el día al último día de enero
    ultimo_dia_del_siguiente_mes = datetime.date(fecha_actual.year + 1, 1, 31)
else:
    # Si no es diciembre, calcula el último día del mes siguiente
    ultimo_dia_del_siguiente_mes = datetime.date(fecha_actual.year, 
                                                 fecha_actual.month + 1, 
                                                 calendar.monthrange(fecha_actual.year, 
                                                                     fecha_actual.month + 1)[1])

if pd.Timestamp(ultimo_dia_del_mes).day - pd.Timestamp(fecha_actual).day > 4:
    if pd.Timestamp(ultimo_dia_del_mes) in list(kashio_para_csv['VENCIMIENTO parseado']):
        print('fechas bien puestas')
    elif pd.Timestamp(ultimo_dia_del_siguiente_mes) in list(kashio_para_csv['VENCIMIENTO parseado']):
        print('fechas bien puestas')
    else:
        print('las fechas están mal, debes cambiar la segunda en el fincore al último día del mes')
else:
    print('las fechas están mal, debes cambiar la segunda en el fincore al último día del mes')
kashio_para_csv.drop('VENCIMIENTO parseado', 
                     axis = 1, 
                     inplace = True)

#%% EXPORTAR A CSV 

kashio_para_csv.to_csv('GeneracionData ' + str(ARCHIVO_HOY[29:37]) + '.csv', 
                       index    = False, 
                       encoding = 'utf-8')

'''
#BUSCAR LOS Ã‘ Y REEMPLAZARLOS POR Ñ
'''

#%% EXPORTAR A EXCEL SI ES QUE ES NECESARIO CREAR EL REPORTE MENSUAL

'''
kashio_para_csv.to_excel('insumo cobranzas en caso de necesitar el reporte ' + str(ARCHIVO_HOY[29:37]) + '.xlsx',
                         index = False)
'''
