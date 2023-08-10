# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 15:00:55 2023

@author: Joseph Montoya
"""

import pandas as pd
import os

#%% #LEYENDO EL DEL DÍA ACTUAL
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\KASHIO\\2023 AGOSTO\\10 agosto 2023')

kashio = pd.read_excel('DATA_CLIENTES_COOP.SANMIGUEL_20230810.xlsx',
                       dtype={'ID CLIENTE': str,
                              'TELEFONO': str,
                              'NUMERO DOCUMENTO': str})

kashio['ID CLIENTE'] = kashio['ID CLIENTE'].str.strip()
kashio['EMAIL'] = kashio['EMAIL'].str.strip()
kashio['EMAIL'] = kashio['EMAIL'].str.upper()

#%% #LEYENDO EL DEL DÍA ANTERIOR
ubi = 'C:\\Users\\sanmiguel38\\Desktop\\KASHIO\\2023 AGOSTO\\09 agosto 2023'
nombre = 'DATA_CLIENTES_COOP.SANMIGUEL_20230809.xlsx'

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

#%% LIMPIEZA DE DATOS:  
def correccion(row):
    palabras_a_buscar = ['GMAILCON', '\\', '/', 'FMAIL.COM', 'GAMIL.COM', 'GEMAIL.COM', 'GMAIL.COM.COM',
                         'HOTMAIL.COM/MECHIBL_2000@HOTMAIL.COM', 'GMAI.COM', 'GMIAL.COM', 'GNMAIL.COM', '@MAIL.COM']
    
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

#%%
try:
    ruta = "correo corregido.xlsx"
    os.remove(ruta)
except FileNotFoundError:
    pass

kashio.to_excel("correo corregido.xlsx", index=False)   

