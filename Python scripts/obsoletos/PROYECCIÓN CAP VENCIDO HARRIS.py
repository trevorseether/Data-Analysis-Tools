# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 16:30:02 2023

@author: Joseph Montoya
"""


import pandas as pd
import os

#%%
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\HARRIS PROYECCIÓN')
#%%
mora_dxp =  'Mora_DxP_Junio_2023.xlsx'
mora_ld =   'Mora_LD_Junio_2023.xlsx'
mora_mype = 'Mora_MyPE_Junio_2023.xlsx'

#%%
fecha_hoy = '23/06/2023'
#%%
#leyendo DXP DE LIMA
dxp_lima = pd.read_excel(mora_dxp, 
                         sheet_name = 'DxP - Lima',
                         skiprows= 0,
                         dtype = 
                         {'''Código
Socio''' : object,  '''N°
Préstamo''' : object,   'Celular' : object,  'DNI': object})
dxp_lima = dxp_lima.rename(columns={"Segundp Aval": "Segundo Aval"})
columnas = dxp_lima.columns
columnas = columnas[:-2]
dxp_lima = dxp_lima[columnas]
dxp_lima['origen excel'] = 'dxp-lima'

#LEYENDO DXP DE PROVINCIA
dxp_provincia = pd.read_excel(mora_dxp, 
                         sheet_name = 'DxP - Proseva',
                         skiprows= 0,
                         dtype = 
                         {'''Código
Socio''' : object,  '''N°
Préstamo''' : object,   'Celular' : object,   'DNI': object})
dxp_provincia = dxp_provincia[columnas]
dxp_provincia['origen excel'] = 'dxp-provincia'

#LEYENDO DXP JUDICIAL
dxp_judicial = pd.read_excel(mora_dxp, 
                         sheet_name = 'Judicial',
                         skiprows= 0,
                         dtype = 
                         {'''Código
Socio''' : object,  '''N°
Préstamo''' : object,   'Celular' : object,   'DNI': object})
dxp_judicial = dxp_judicial[columnas]
dxp_judicial['origen excel'] = 'dxp-judicial'

#LEYENDO DXP CASTIGADOS
dxp_castigados = pd.read_excel(mora_dxp, 
                         sheet_name = 'Castigado',
                         skiprows= 0,
                         dtype = 
                         {'''Código
Socio''' : object,  '''N°
Préstamo''' : object,   'Celular' : object,   'DNI': object})
dxp_castigados = dxp_castigados[columnas]
dxp_castigados['origen excel'] = 'dxp-castigado'

#%%
#leyendo LD NORMAL
ld_normal = pd.read_excel(mora_ld, 
                         sheet_name = 'Normal',
                         skiprows= 0,
                         dtype = 
                         {'''Código
Socio''' : object,  '''N°
Préstamo''' : object,   'Celular' : object,  'DNI': object})
ld_normal = ld_normal.rename(columns={"Segundp Aval": "Segundo Aval"})
ld_normal = ld_normal[columnas]
ld_normal['origen excel'] = 'ld-normal'

#LEYENDO LD JUDICIAL
ld_judicial = pd.read_excel(mora_ld, 
                         sheet_name = 'Judicial',
                         skiprows= 0,
                         dtype = 
                         {'''Código
Socio''' : object,  '''N°
Préstamo''' : object,   'Celular' : object,   'DNI': object})
ld_judicial = ld_judicial[columnas]
ld_judicial['origen excel'] = 'ld-judicial'

#%%
#leyendo MYPE DE LIMA
mype_lima = pd.read_excel(mora_mype, 
                         sheet_name = 'Lima',
                         skiprows= 0,
                         dtype = 
                         {'''Código
Socio''' : object,  '''N°
Préstamo''' : object,   'Celular' : object,  'DNI': object})
mype_lima = mype_lima.rename(columns={"Segundp Aval": "Segundo Aval"})
mype_lima = mype_lima[columnas]
mype_lima['origen excel'] = 'mype-lima'

#LEYENDO MYPE DE PROVINCIA
mype_provincia = pd.read_excel(mora_mype, 
                         sheet_name = 'Provincia',
                         skiprows= 0,
                         dtype = 
                         {'''Código
Socio''' : object,  '''N°
Préstamo''' : object,   'Celular' : object,   'DNI': object})
mype_provincia = mype_provincia[columnas]
mype_provincia['origen excel'] = 'mype-provincia'

#LEYENDO MYPE JUDICIAL
mype_judicial = pd.read_excel(mora_mype, 
                         sheet_name = 'Judicial',
                         skiprows= 0,
                         dtype = 
                         {'''Código
Socio''' : object,  '''N°
Préstamo''' : object,   'Celular' : object,   'DNI': object})
mype_judicial = mype_judicial[columnas]
mype_judicial['origen excel'] = 'mype-judicial'

#LEYENDO MYPE CASTIGADOS
mype_castigados = pd.read_excel(mora_mype, 
                         sheet_name = 'Castigado',
                         skiprows= 0,
                         dtype = 
                         {'''Código
Socio''' : object,  '''N°
Préstamo''' : object,   'Celular' : object,   'DNI': object})
mype_castigados = mype_castigados[columnas]
mype_castigados['origen excel'] = 'mype-castigado'

#%%
# ya que verificamos que todas tienen las mismas columnas
'CONCATENAMOS LOS DATAFRAMES'

concatenado = pd.concat([dxp_lima, dxp_provincia, dxp_judicial, dxp_castigados, 
                         ld_normal, ld_judicial,
                         mype_lima, mype_provincia, mype_judicial, mype_castigados], axis=0)

#%%
'PROYECCIÓN DE LA CALIFICACIÓN'

ult_dia = columnas[20]
concatenado['Producto'] = concatenado['Producto'].str.strip()
def calificacion(concatenado):
    if (concatenado[ult_dia] >= 0) & (concatenado[ult_dia] <= 8):
        return '0'
    elif (concatenado[ult_dia] >= 9) & (concatenado[ult_dia] <= 30):
        return '1'
    elif (concatenado[ult_dia] >= 31) & (concatenado[ult_dia] <= 60):
        return '2'
    elif (concatenado[ult_dia] >= 61) & (concatenado[ult_dia] <= 120):
        return '3'
    elif (concatenado[ult_dia] >= 120):
        return '4'
    else:
        return 'investigar caso'

concatenado['calificación proyectada'] = concatenado.apply(calificacion, axis=1)
ult_dia = columnas[19]
concatenado['calificación fin de mes pasado'] = concatenado.apply(calificacion, axis=1)
ult_dia = columnas[18]
concatenado['calificación hoy'] = concatenado.apply(calificacion, axis=1)

#%%
#ELIMINAMOS LA COLUMNA DIRECCIÓN (AL PARECER HAY ALGÚN CARACTER NO PERMITIDO)
concatenado = concatenado.drop('Dirección', axis=1)

#%%
# añadimos la fecha de los datos
concatenado['DÍA ANÁLISIS'] = fecha_hoy

#%%
#CREACIÓN EXCEL

try:
    ruta = "PROYECCIÓN HARRIS.xlsx"
    os.remove(ruta)
except FileNotFoundError:
    pass

concatenado.to_excel('PROYECCIÓN HARRIS.xlsx', index=False)





