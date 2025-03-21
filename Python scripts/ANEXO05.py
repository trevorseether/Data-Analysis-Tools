# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 17:13:05 2023

@author: Joseph Montoya
"""
# =============================================================================
#                               ANEXO 05 PARA SBS
# =============================================================================
import pandas as pd
import os
import numpy as np
#from decimal import Decimal

#%% AVISO
'ANTES DE EMPEZAR'
'REDONDEAR diferidos, devengados y en suspenso'
'también PROVISIONES CONSTITUIDAS'
'Y RECIÉN REDONDEADO LE PASAMOS EL ANEXO A RIESGOS Y CONTABILIDAD'

#%% FECHA CORTE
##############################################
fecha_corte = 'FEBRERO 2025'
##############################################
#%% UBI
# ubicación ###################################################################
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2025\\febrero\\parte 2')
###############################################################################
#%% ANX06
# ANEXO 06 ####################################################################
anx_06 = "Rpt_DeudoresSBS Anexo06 - Febrero 2025 - campos ampliados 04.xlsx"
###############################################################################

# filas ignoradas ###########
filas_skip = 2              #
#############################

#%% LECTURA DEL ANEXO 06

df1 = pd.read_excel(anx_06,
                 dtype = {'Código Socio 7/'           : object, 
                          'Número de Documento 10/'   : object,
                          'Numero de Crédito 18/'     : object, 
                          'Nro Prestamo \nFincore'    : object,
                          'Moneda del crédito 17/'    : object, 
                          'Tipo de Crédito 19/'       : str,
                          'Clasificación del Deudor con Alineamiento 15/' : object,
                          'Fecha de Nacimiento 3/'    : object,
                          },
                 skiprows = filas_skip)

# eliminación de filas vacías
df1.dropna(subset = ['Apellidos y Nombres / Razón Social 2/', 
                     'Fecha de Nacimiento 3/',
                     'Número de Documento 10/',
                     'Domicilio 12/',
                     'Numero de Crédito 18/'], inplace = True, how = 'all')

# esta limpieza existe porque existe la posibilidad de que algunas columnas sean números en lugar de texto
df1['Tipo de Crédito 19/'] = df1['Tipo de Crédito 19/'].astype(str)
# df1['Tipo de Crédito 19/'].unique()
df1['Tipo de Crédito 19/'] = df1['Tipo de Crédito 19/'].str.strip()

tipos_nulos = df1[pd.isna(df1['Tipo de Crédito 19/'])].shape[0]
if tipos_nulos > 0:
    print('revisar, hay Tipo de Crédito 19/ con valores nulos')
else:
    print('todo bien')
del tipos_nulos

#%% limpieza
#ELIMINA ESPACIOS VACÍOS
df1['Código Socio 7/'] = df1['Código Socio 7/'].str.strip()

#%% REDONDEO DE LAS COLUMNAS
df1['Ingresos Diferidos 42/']     = df1['Ingresos Diferidos 42/'].round(2)
df1['Rendimiento\nDevengado 40/'] = df1['Rendimiento\nDevengado 40/'].round(2)
df1['Intereses en Suspenso 41/']  = df1['Intereses en Suspenso 41/'].round(2)

#%% copia
#hacemos una copia, porque sí
anexo06 = df1.copy()
x = anexo06.columns
#%% CREACIÓN DE COLUMNAS NECESARIAS
anexo06['24 - 42'] = anexo06['Saldo de colocaciones (créditos directos) 24/'] - anexo06['Ingresos Diferidos 42/']
anexo06['24 - 42'] = anexo06['24 - 42'].round(2)
anexo06['37 - 36'] = anexo06['Provisiones Constituidas 37/'] - anexo06['Provisiones Requeridas 36/']
anexo06['37 - 36'] = anexo06['37 - 36'].round(2)

#%%
'TABLA A'
pivot_A_A = anexo06.pivot_table(columns = 'Clasificación del Deudor con Alineamiento 15/',
                                      values  = ['24 - 42'], 
                                      index   = ['Tipo de Crédito 19/'],
                                      margins = True, margins_name = 'Total', #para sacar las sumatorias totales                                      
                                      aggfunc = 'sum'
                                      )
pivot_A_A = pivot_A_A.reset_index()
pivot_A_A.fillna(0, inplace = True)

#%%
# Aquí hay algo bien raro, en el mes de junio(trimestral) debió ser el saldo de cartera
# y en julio nos está podiendo que vaya '24 - 42' (cartera neta)
# que raro (ಠ_ಠ)
###################  'Saldo de colocaciones (créditos directos) 24/'    #######
'TABLA A'

pivot_A = anexo06.pivot_table(columns = 'Clasificación del Deudor con Alineamiento 15/',
                                      values  = ['24 - 42'], #'24 - 42'
                                      index   = ['Tipo de Crédito 19/'],
                                      margins = True, margins_name = 'Total', #para sacar las sumatorias totales                                      
                                      aggfunc = 'sum'
                                      )
pivot_A = pivot_A.reset_index()
pivot_A.fillna(0, inplace = True)

#%%
'TABLA B'
# eliminamos castigados
conteo_socios = anexo06[(anexo06['Saldos de Créditos Castigados 38/'] == 0)]
# Aqui va el nro de créditos y el nro de socios

# ESTA TABLA NO INCLUYE A LOS SOCIOS CASTIGADOS:
pivot_B = conteo_socios.pivot_table(columns   = 'Clasificación del Deudor con Alineamiento 15/',
                                      values  = ['Numero de Crédito 18/'], 
                                      index   = ['Tipo de Crédito 19/'],
                                      margins = True, 
                                      margins_name='Total', #para sacar las sumatorias totales
                                      aggfunc ='count'
                                      )
pivot_B = pivot_B.reset_index()
pivot_B.fillna(0, inplace = True)

conteo_socios.loc[:, 'Código Socio 7/'] = conteo_socios['Código Socio 7/'].str.strip()
# conteo_socios['Código Socio 7/']      = conteo_socios['Código Socio 7/'].str.strip()

# CALCULAMOS EL NRO DE SOCIOS

socios_0 =  conteo_socios[( conteo_socios['Clasificación del Deudor con Alineamiento 15/'] == 0)]['Código Socio 7/'].nunique()
socios_1 =  conteo_socios[( conteo_socios['Clasificación del Deudor con Alineamiento 15/'] == 1)]['Código Socio 7/'].nunique()
socios_2 =  conteo_socios[( conteo_socios['Clasificación del Deudor con Alineamiento 15/'] == 2)]['Código Socio 7/'].nunique()
socios_3 =  conteo_socios[( conteo_socios['Clasificación del Deudor con Alineamiento 15/'] == 3)]['Código Socio 7/'].nunique()
socios_4 =  conteo_socios[( conteo_socios['Clasificación del Deudor con Alineamiento 15/'] == 4)]['Código Socio 7/'].nunique()

suma_socios = int(conteo_socios['Código Socio 7/'].nunique())  #cuando implementamos este código, nos rechazó la SBS
# si aplicamos esta metodología, hay que cambiar los subtotales de cada columna manualmente

# código desactivado que podría servir algún día
# suma_socios = socios_0 + socios_1 + socios_2 + socios_3 + socios_4

#%%
'TABLA C Y C' #PUROS CEROS

#%%
'TABLA D'
pivot_D = anexo06.pivot_table(columns='Clasificación del Deudor con Alineamiento 15/',
                                      values=['Saldo de Garantías Autoliquidables 35/'], 
                                      index=['Tipo de Crédito 19/'], 
                                      margins=True, margins_name='Total', #para sacar las sumatorias totales                                      
                                      aggfunc='sum'
                                      )
pivot_D = pivot_D.reset_index()
pivot_D.fillna(0, inplace=True)
#%%
'TABLA E' #PUROS CEROS
#%%
'TABLA F'
pivot_F = anexo06.pivot_table(columns='Clasificación del Deudor con Alineamiento 15/',
                                      values=['Saldos de Garantías Preferidas 34/'], 
                                      index=['Tipo de Crédito 19/'], 
                                      margins=True, margins_name='Total', #para sacar las sumatorias totales                                      
                                      aggfunc='sum'
                                      )
pivot_F = pivot_F.reset_index()
pivot_F.fillna(0, inplace=True)
#%%
'TABLA G' #PUROS CEROS
#%%
'TABLA H'
pivot_H = anexo06.pivot_table(columns='Clasificación del Deudor con Alineamiento 15/',
                                      values=['Saldo de Créditos que no cuentan con cobertura 51/'], 
                                      index=['Tipo de Crédito 19/'], 
                                      margins=True, margins_name='Total', #para sacar las sumatorias totales                                      
                                      aggfunc='sum'
                                      )
pivot_H = pivot_H.reset_index()
pivot_H.fillna(0, inplace=True)
#%%
'TABLA I'
pivot_I = anexo06.pivot_table(columns='Clasificación del Deudor con Alineamiento 15/',
                                      values=['Provisiones Constituidas 37/'], 
                                      index=['Tipo de Crédito 19/'], 
                                      margins=True, margins_name='Total', #para sacar las sumatorias totales                                      
                                      aggfunc='sum'
                                      )
pivot_I = pivot_I.reset_index()
pivot_I.fillna(0, inplace=True)
#%%
'TABLA J'
pivot_J = anexo06.pivot_table(columns='Clasificación del Deudor con Alineamiento 15/',
                                      values=['Provisiones Requeridas 36/'], 
                                      index=['Tipo de Crédito 19/'], 
                                      margins=True, margins_name='Total', #para sacar las sumatorias totales                                      
                                      aggfunc='sum'
                                      )
pivot_J = pivot_J.reset_index()
pivot_J.fillna(0, inplace=True)
#%%
'TABLA K'
pivot_K = anexo06.pivot_table(columns='Clasificación del Deudor con Alineamiento 15/',
                                      values=['37 - 36'], 
                                      index=['Tipo de Crédito 19/'], 
                                      margins=True, margins_name='Total', #para sacar las sumatorias totales                                      
                                      aggfunc='sum'
                                      )
pivot_K = pivot_K.reset_index()
pivot_K.fillna(0, inplace=True)

#%%
'MOMENTO DE ELABORAR EL ANEXO 05'
'crear dataframe'
anexo05 = pd.DataFrame(columns=["A", "B", "C", "D", "E", "F", "G"])

#%%
#codigo que podría servir algún día :v
#c = pivot_A_A.loc[pivot_A_A['Tipo de Crédito 19/'] == '07']


nueva_fila = pd.DataFrame([['100', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['200', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['300', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)


nueva_fila = pd.DataFrame([['400', 
                            pivot_A_A.iloc[0,1],
                            pivot_A_A.iloc[0,2], 
                            pivot_A_A.iloc[0,3], 
                            pivot_A_A.iloc[0,4], 
                            pivot_A_A.iloc[0,5],
                            pivot_A_A.iloc[0,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['500', 
                            pivot_A_A.iloc[1,1],
                            pivot_A_A.iloc[1,2], 
                            pivot_A_A.iloc[1,3], 
                            pivot_A_A.iloc[1,4], 
                            pivot_A_A.iloc[1,5],
                            pivot_A_A.iloc[1,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['600', 
                            pivot_A_A.iloc[2,1],
                            pivot_A_A.iloc[2,2], 
                            pivot_A_A.iloc[2,3], 
                            pivot_A_A.iloc[2,4], 
                            pivot_A_A.iloc[2,5],
                            pivot_A_A.iloc[2,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['700', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['800', 
                            pivot_A_A.iloc[3,1],
                            pivot_A_A.iloc[3,2], 
                            pivot_A_A.iloc[3,3], 
                            pivot_A_A.iloc[3,4], 
                            pivot_A_A.iloc[3,5],
                            pivot_A_A.iloc[3,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['900', 
                            pivot_A_A.iloc[4,1],
                            pivot_A_A.iloc[4,2], 
                            pivot_A_A.iloc[4,3], 
                            pivot_A_A.iloc[4,4], 
                            pivot_A_A.iloc[4,5],
                            pivot_A_A.iloc[4,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#primera suma
nueva_fila = pd.DataFrame([['1000', 
                            pivot_A_A.iloc[5,1],
                            pivot_A_A.iloc[5,2], 
                            pivot_A_A.iloc[5,3], 
                            pivot_A_A.iloc[5,4], 
                            pivot_A_A.iloc[5,5],
                            pivot_A_A.iloc[5,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#%%
nueva_fila = pd.DataFrame([['1100', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['1200', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['1300', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['1400', 
                            pivot_A.iloc[0,1],
                            pivot_A.iloc[0,2], 
                            pivot_A.iloc[0,3], 
                            pivot_A.iloc[0,4], 
                            pivot_A.iloc[0,5],
                            pivot_A.iloc[0,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['1500', 
                            pivot_A.iloc[1,1],
                            pivot_A.iloc[1,2], 
                            pivot_A.iloc[1,3], 
                            pivot_A.iloc[1,4], 
                            pivot_A.iloc[1,5],
                            pivot_A.iloc[1,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['1600', 
                            pivot_A.iloc[2,1],
                            pivot_A.iloc[2,2], 
                            pivot_A.iloc[2,3], 
                            pivot_A.iloc[2,4], 
                            pivot_A.iloc[2,5],
                            pivot_A.iloc[2,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['1700', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['1800', 
                            pivot_A.iloc[3,1],
                            pivot_A.iloc[3,2], 
                            pivot_A.iloc[3,3], 
                            pivot_A.iloc[3,4], 
                            pivot_A.iloc[3,5],
                            pivot_A.iloc[3,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['1900', 
                            pivot_A.iloc[4,1],
                            pivot_A.iloc[4,2], 
                            pivot_A.iloc[4,3], 
                            pivot_A.iloc[4,4], 
                            pivot_A.iloc[4,5],
                            pivot_A.iloc[4,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#segunda suma
nueva_fila = pd.DataFrame([['2000', 
                            pivot_A.iloc[5,1],
                            pivot_A.iloc[5,2], 
                            pivot_A.iloc[5,3], 
                            pivot_A.iloc[5,4], 
                            pivot_A.iloc[5,5],
                            pivot_A.iloc[5,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#%%

nueva_fila = pd.DataFrame([['2100', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['2200', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['2300', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['2400', 
                            pivot_B.iloc[0,1],
                            pivot_B.iloc[0,2], 
                            pivot_B.iloc[0,3], 
                            pivot_B.iloc[0,4], 
                            pivot_B.iloc[0,5],
                            pivot_B.iloc[0,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['2500', 
                            pivot_B.iloc[1,1],
                            pivot_B.iloc[1,2], 
                            pivot_B.iloc[1,3], 
                            pivot_B.iloc[1,4], 
                            pivot_B.iloc[1,5],
                            pivot_B.iloc[1,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['2600', 
                            pivot_B.iloc[2,1],
                            pivot_B.iloc[2,2], 
                            pivot_B.iloc[2,3], 
                            pivot_B.iloc[2,4], 
                            pivot_B.iloc[2,5],
                            pivot_B.iloc[2,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['2700', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['2800', 
                            pivot_B.iloc[3,1],
                            pivot_B.iloc[3,2], 
                            pivot_B.iloc[3,3], 
                            pivot_B.iloc[3,4], 
                            pivot_B.iloc[3,5],
                            pivot_B.iloc[3,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['2900', 
                            pivot_B.iloc[4,1],
                            pivot_B.iloc[4,2], 
                            pivot_B.iloc[4,3], 
                            pivot_B.iloc[4,4], 
                            pivot_B.iloc[4,5],
                            pivot_B.iloc[4,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#tercera suma, que no es suma
nueva_fila = pd.DataFrame([['3000', 
                            socios_0,
                            socios_1, 
                            socios_2, 
                            socios_3, 
                            socios_4,
                            suma_socios]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#%%
#PURO CERO
nueva_fila = pd.DataFrame([['3100', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['3200', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['3300', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['3400', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['3500', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['3600', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['3700', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['3800', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['3900', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#tercera suma, que no es suma
nueva_fila = pd.DataFrame([['4000', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#%%
#PURO CERO 2
nueva_fila = pd.DataFrame([['4100', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['4200', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['4250', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['4300', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['4400', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['4500', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['4600', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['4700', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['4900', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#tercera suma, que no es suma
nueva_fila = pd.DataFrame([['5000', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['5100', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#%%
nueva_fila = pd.DataFrame([['5200', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['5300', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['5400', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['5500', 
                            pivot_D.iloc[0,1],
                            pivot_D.iloc[0,2], 
                            pivot_D.iloc[0,3], 
                            pivot_D.iloc[0,4], 
                            pivot_D.iloc[0,5],
                            pivot_D.iloc[0,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['5600', 
                            pivot_D.iloc[1,1],
                            pivot_D.iloc[1,2], 
                            pivot_D.iloc[1,3], 
                            pivot_D.iloc[1,4], 
                            pivot_D.iloc[1,5],
                            pivot_D.iloc[1,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['5700', 
                            pivot_D.iloc[2,1],
                            pivot_D.iloc[2,2], 
                            pivot_D.iloc[2,3], 
                            pivot_D.iloc[2,4], 
                            pivot_D.iloc[2,5],
                            pivot_D.iloc[2,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['5800', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['5900', 
                            pivot_D.iloc[3,1],
                            pivot_D.iloc[3,2], 
                            pivot_D.iloc[3,3], 
                            pivot_D.iloc[3,4], 
                            pivot_D.iloc[3,5],
                            pivot_D.iloc[3,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['6000', 
                            pivot_D.iloc[4,1],
                            pivot_D.iloc[4,2], 
                            pivot_D.iloc[4,3], 
                            pivot_D.iloc[4,4], 
                            pivot_D.iloc[4,5],
                            pivot_D.iloc[4,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#segunda suma
nueva_fila = pd.DataFrame([['6100', 
                            pivot_D.iloc[5,1],
                            pivot_D.iloc[5,2], 
                            pivot_D.iloc[5,3], 
                            pivot_D.iloc[5,4], 
                            pivot_D.iloc[5,5],
                            pivot_D.iloc[5,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#%%
nueva_fila = pd.DataFrame([['6400', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['6500', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['6600', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['6700', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['6800', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['6900', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['7000', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['7100', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#%%
nueva_fila = pd.DataFrame([['7200', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['7300', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['7400', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['7500', 
                            pivot_F.iloc[0,1],
                            pivot_F.iloc[0,2], 
                            pivot_F.iloc[0,3], 
                            pivot_F.iloc[0,4], 
                            pivot_F.iloc[0,5],
                            pivot_F.iloc[0,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['7600', 
                            pivot_F.iloc[1,1],
                            pivot_F.iloc[1,2], 
                            pivot_F.iloc[1,3], 
                            pivot_F.iloc[1,4], 
                            pivot_F.iloc[1,5],
                            pivot_F.iloc[1,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['7700', 
                            pivot_F.iloc[2,1],
                            pivot_F.iloc[2,2], 
                            pivot_F.iloc[2,3], 
                            pivot_F.iloc[2,4], 
                            pivot_F.iloc[2,5],
                            pivot_F.iloc[2,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['8000', 
                            pivot_F.iloc[4,1],
                            pivot_F.iloc[4,2], 
                            pivot_F.iloc[4,3], 
                            pivot_F.iloc[4,4], 
                            pivot_F.iloc[4,5],
                            pivot_F.iloc[4,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['8100', 
                            pivot_F.iloc[5,1],
                            pivot_F.iloc[5,2], 
                            pivot_F.iloc[5,3], 
                            pivot_F.iloc[5,4], 
                            pivot_F.iloc[5,5],
                            pivot_F.iloc[5,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#%%
nueva_fila = pd.DataFrame([['8200', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['8300', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['8400', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#%%

nueva_fila = pd.DataFrame([['8500', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['8600', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['8700', 
                            pivot_H.iloc[0,1],
                            pivot_H.iloc[0,2], 
                            pivot_H.iloc[0,3], 
                            pivot_H.iloc[0,4], 
                            pivot_H.iloc[0,5],
                            pivot_H.iloc[0,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['8800', 
                            pivot_H.iloc[1,1],
                            pivot_H.iloc[1,2], 
                            pivot_H.iloc[1,3], 
                            pivot_H.iloc[1,4], 
                            pivot_H.iloc[1,5],
                            pivot_H.iloc[1,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['8900', 
                            pivot_H.iloc[2,1],
                            pivot_H.iloc[2,2], 
                            pivot_H.iloc[2,3], 
                            pivot_H.iloc[2,4], 
                            pivot_H.iloc[2,5],
                            pivot_H.iloc[2,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['9000', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['9100', 
                            pivot_H.iloc[3,1],
                            pivot_H.iloc[3,2], 
                            pivot_H.iloc[3,3], 
                            pivot_H.iloc[3,4], 
                            pivot_H.iloc[3,5],
                            pivot_H.iloc[3,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['9200', 
                            pivot_H.iloc[4,1],
                            pivot_H.iloc[4,2], 
                            pivot_H.iloc[4,3], 
                            pivot_H.iloc[4,4], 
                            pivot_H.iloc[4,5],
                            pivot_H.iloc[4,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['9300', 
                            pivot_H.iloc[5,1],
                            pivot_H.iloc[5,2], 
                            pivot_H.iloc[5,3], 
                            pivot_H.iloc[5,4], 
                            pivot_H.iloc[5,5],
                            pivot_H.iloc[5,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#%%
nueva_fila = pd.DataFrame([['9400', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['9500', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['9600', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['9700', 
                            pivot_I.iloc[0,1],
                            pivot_I.iloc[0,2], 
                            pivot_I.iloc[0,3], 
                            pivot_I.iloc[0,4], 
                            pivot_I.iloc[0,5],
                            pivot_I.iloc[0,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['9800', 
                            pivot_I.iloc[1,1],
                            pivot_I.iloc[1,2], 
                            pivot_I.iloc[1,3], 
                            pivot_I.iloc[1,4], 
                            pivot_I.iloc[1,5],
                            pivot_I.iloc[1,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['9900', 
                            pivot_I.iloc[2,1],
                            pivot_I.iloc[2,2], 
                            pivot_I.iloc[2,3], 
                            pivot_I.iloc[2,4], 
                            pivot_I.iloc[2,5],
                            pivot_I.iloc[2,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['10000', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['10100', 
                            pivot_I.iloc[3,1],
                            pivot_I.iloc[3,2], 
                            pivot_I.iloc[3,3], 
                            pivot_I.iloc[3,4], 
                            pivot_I.iloc[3,5],
                            pivot_I.iloc[3,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['10200', 
                            pivot_I.iloc[4,1],
                            pivot_I.iloc[4,2], 
                            pivot_I.iloc[4,3], 
                            pivot_I.iloc[4,4], 
                            pivot_I.iloc[4,5],
                            pivot_I.iloc[4,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['10300', 
                            pivot_I.iloc[5,1],
                            pivot_I.iloc[5,2], 
                            pivot_I.iloc[5,3], 
                            pivot_I.iloc[5,4], 
                            pivot_I.iloc[5,5],
                            pivot_I.iloc[5,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#%%
nueva_fila = pd.DataFrame([['10400', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['10500', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila1 = pd.DataFrame([['10600', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['10700', 
                            pivot_J.iloc[0,1],
                            pivot_J.iloc[0,2], 
                            pivot_J.iloc[0,3], 
                            pivot_J.iloc[0,4], 
                            pivot_J.iloc[0,5],
                            pivot_J.iloc[0,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['10800', 
                            pivot_J.iloc[1,1],
                            pivot_J.iloc[1,2], 
                            pivot_J.iloc[1,3], 
                            pivot_J.iloc[1,4], 
                            pivot_J.iloc[1,5],
                            pivot_J.iloc[1,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['10900', 
                            pivot_J.iloc[2,1],
                            pivot_J.iloc[2,2], 
                            pivot_J.iloc[2,3], 
                            pivot_J.iloc[2,4], 
                            pivot_J.iloc[2,5],
                            pivot_J.iloc[2,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['11000', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['11100', 
                            pivot_J.iloc[3,1],
                            pivot_J.iloc[3,2], 
                            pivot_J.iloc[3,3], 
                            pivot_J.iloc[3,4], 
                            pivot_J.iloc[3,5],
                            pivot_J.iloc[3,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['11200', 
                            pivot_J.iloc[4,1],
                            pivot_J.iloc[4,2], 
                            pivot_J.iloc[4,3], 
                            pivot_J.iloc[4,4], 
                            pivot_J.iloc[4,5],
                            pivot_J.iloc[4,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['11300', 
                            pivot_J.iloc[5,1],
                            pivot_J.iloc[5,2], 
                            pivot_J.iloc[5,3], 
                            pivot_J.iloc[5,4], 
                            pivot_J.iloc[5,5],
                            pivot_J.iloc[5,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#%%
nueva_fila = pd.DataFrame([['11400', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['11500', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['11600', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['11700', 
                            pivot_K.iloc[0,1],
                            pivot_K.iloc[0,2], 
                            pivot_K.iloc[0,3], 
                            pivot_K.iloc[0,4], 
                            pivot_K.iloc[0,5],
                            pivot_K.iloc[0,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['11800', 
                            pivot_K.iloc[1,1],
                            pivot_K.iloc[1,2], 
                            pivot_K.iloc[1,3], 
                            pivot_K.iloc[1,4], 
                            pivot_K.iloc[1,5],
                            pivot_K.iloc[1,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['11900', 
                            pivot_K.iloc[2,1],
                            pivot_K.iloc[2,2], 
                            pivot_K.iloc[2,3], 
                            pivot_K.iloc[2,4], 
                            pivot_K.iloc[2,5],
                            pivot_K.iloc[2,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['12000', 0, 0, 0, 0, 0, 0]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['12100', 
                            pivot_K.iloc[3,1],
                            pivot_K.iloc[3,2], 
                            pivot_K.iloc[3,3], 
                            pivot_K.iloc[3,4], 
                            pivot_K.iloc[3,5],
                            pivot_K.iloc[3,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['12200', 
                            pivot_K.iloc[4,1],
                            pivot_K.iloc[4,2], 
                            pivot_K.iloc[4,3], 
                            pivot_K.iloc[4,4], 
                            pivot_K.iloc[4,5],
                            pivot_K.iloc[4,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['12300', 
                            pivot_K.iloc[5,1],
                            pivot_K.iloc[5,2], 
                            pivot_K.iloc[5,3], 
                            pivot_K.iloc[5,4], 
                            pivot_K.iloc[5,5],
                            pivot_K.iloc[5,6]]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#%%

'CUADRE DEL ANEXO Nº 5 CON LAS CIFRAS DEL BALANCE'

nueva_fila = pd.DataFrame([[np.nan, 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['CIFRAS DEL BALANCE', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['CREDITOS DIRECTOS', 
                            pivot_A_A.iloc[5,6],
                            pivot_A_A.iloc[5,6], 
                            pivot_I.iloc[5,1], 
                            pivot_I.iloc[5,6] - pivot_I.iloc[5,1], 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['creditos directos', 
                            pivot_A_A.iloc[5,6],
                            pivot_A_A.iloc[5,6], 
                            pivot_I.iloc[5,1], 
                            pivot_I.iloc[5,6] - pivot_I.iloc[5,1], 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['CREDITOS INDIRECTOS', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['a)', 
                            0,
                            0, 
                            0, 
                            0, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['b)', 
                            0,
                            0, 
                            0, 
                            0, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['c)', 
                            0,
                            0, 
                            0, 
                            0, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['TOTAL', 
                            pivot_A_A.iloc[5,6],
                            pivot_A_A.iloc[5,6], 
                            pivot_I.iloc[5,1], 
                            pivot_I.iloc[5,6] - pivot_I.iloc[5,1], 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['W - ANEXO 5', 
                            np.nan,
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['Créditos directos e indirectos afectos a provisiones', 
                            pivot_A_A.iloc[5,6],
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['Provisiones Genéricas constituidas', 
                            pivot_I.iloc[5,1],
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

nueva_fila = pd.DataFrame([['Provisiones específicas constituidas', 
                            pivot_I.iloc[5,6] - pivot_I.iloc[5,1], # Provisiones específicas constituídas = Provisiones Constituídas(total) - Provisiones Constituídas (solo clasificación cero [también llamadas provisiones genéricas])
                            np.nan, 
                            np.nan, 
                            np.nan, 
                            np.nan,
                            np.nan]], columns=["A", "B", "C", "D", "E", "F", "G"])
anexo05 = pd.concat([anexo05,nueva_fila], ignore_index = True)

#%% Exportación a excel

'CREACIÓN DEL EXCEL'
nombre = "Anexo 05 (para macros) - " + fecha_corte + ".xlsx"
try:
    ruta = nombre
    os.remove(ruta)
except FileNotFoundError:
    pass

anexo05.to_excel(nombre,
                 index = False,
                 sheet_name = fecha_corte)

#%% ubicación actual
ubicacion_actual = os.getcwd()

# Imprimir la ubicación actual
print("La ubicación actual es: " + ubicacion_actual)

