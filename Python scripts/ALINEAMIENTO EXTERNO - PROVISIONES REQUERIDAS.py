# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 17:21:30 2023

@author: Joseph Montoya
"""

'#############################################################################'
'#################            ALINEAMIENTO EXTERNO           #################'
'#############################################################################'

import pandas as pd
import os
import pyodbc

#%% importación de archivos

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\ALINEAMIENTO EXTERNO\\2023 MAYO')

ch_anx06 = 'C:\\Users\\sanmiguel38\\Desktop\\ALINEAMIENTO EXTERNO\\2023 MAYO'
anexo06 = 'anexo06 mayo 2023 finalizado ahora sí.xlsx'

base_alineamiento = '20523941047_70369063_PE202300732_RQ_COOPAC SAN MIGUEL _Alineamiento Externo RCCMay23.xlsx'

#%% lectura

anx06 = pd.read_excel(ch_anx06 + '\\' + anexo06,
                      skiprows= 2,
                      dtype= {'Número de Documento 10/' : str,
                              'Tipo de Crédito 19/'     : str,
                              'Nro Prestamo \nFincore'  : str})

anx06.dropna(subset=['Apellidos y Nombres / Razón Social 2/', 
                     'Fecha de Nacimiento 3/',
                     'Número de Documento 10/',
                     'Domicilio 12/',
                     'Numero de Crédito 18/'], inplace=True, how='all')

#alineamiento externo agregado
alineamiento_externo = pd.read_excel(base_alineamiento,
                                     skiprows=8,
                                     dtype = {'NUMERO DE DOCUMENTO' : str},
                                     sheet_name = 'D')

#alineamiento externo desagregado por empresas en el sector financiero
detalle_entidad = pd.read_excel(base_alineamiento,
                                     skiprows=8,
                                     dtype = {'NUMERO DE DOCUMENTO' : str},
                                     sheet_name = 'E')

del ch_anx06
del anexo06
del base_alineamiento
#%% limpieza de espacios

anx06['Número de Documento 10/'] = anx06['Número de Documento 10/'].str.strip()
anx06['''Nro Prestamo 
Fincore'''] = anx06['''Nro Prestamo 
Fincore'''].str.strip()
alineamiento_externo['NUMERO DE DOCUMENTO'] = alineamiento_externo['NUMERO DE DOCUMENTO'].str.strip()
alineamiento_externo['ALINEAMIENTO EXTERNO CON SBS RCC ACTUAL'] = alineamiento_externo['ALINEAMIENTO EXTERNO CON SBS RCC ACTUAL'].str.strip()

#%%
def alineamiento_numerico(alineamiento_externo):
    if alineamiento_externo['ALINEAMIENTO EXTERNO CON SBS RCC ACTUAL'] == 'NORMAL':
        return 0
    elif alineamiento_externo['ALINEAMIENTO EXTERNO CON SBS RCC ACTUAL'] == 'CPP':
        return 1
    elif alineamiento_externo['ALINEAMIENTO EXTERNO CON SBS RCC ACTUAL'] == 'DEFICIENTE':
        return 2
    elif alineamiento_externo['ALINEAMIENTO EXTERNO CON SBS RCC ACTUAL'] == 'DUDOSO':
        return 3
    elif alineamiento_externo['ALINEAMIENTO EXTERNO CON SBS RCC ACTUAL'] == 'PERDIDA':
        return 4
    else:
        return ''

alineamiento_externo['ALINEAMIENTO EXTERNO'] = alineamiento_externo.apply(alineamiento_numerico, axis=1)
   
print('NÚMERO DE FILAS QUE NO HACEN MATCH:')
print(alineamiento_externo[alineamiento_externo['ALINEAMIENTO EXTERNO'] == ''].shape[0])
        
#%% PREPARAMOS PARA EL MERGE
'para hacer el merge, debemos igualar los carnet de extranjerías'

alineamiento_externo['TIPO DE DOCUMENTO'] = alineamiento_externo['TIPO DE DOCUMENTO'].str.strip()
def completar_documento_con_ceros(alineamiento_externo):
    if alineamiento_externo['TIPO DE DOCUMENTO'] == 'C/E':
        return '0'*(11-len(alineamiento_externo['NUMERO DE DOCUMENTO'])) + alineamiento_externo['NUMERO DE DOCUMENTO']
    else:
        return alineamiento_externo['NUMERO DE DOCUMENTO']
    
alineamiento_externo['NUMERO DE DOCUMENTO'] = alineamiento_externo.apply(completar_documento_con_ceros, axis=1)

#%%
'ahora hacemos lo mismo pero para el anexo06'

anx06['Tipo de Documento 9/'] = anx06['Tipo de Documento 9/'].astype(int)
def completar_documento_con_ceros(anx06):
    if anx06['Tipo de Documento 9/'] == 2:
        return '0'*(11-len(anx06['Número de Documento 10/'])) + anx06['Número de Documento 10/']
    else:
        return anx06['Número de Documento 10/']
    
anx06['Número de Documento 10/'] = anx06.apply(completar_documento_con_ceros, axis=1)
#%%
alineamiento_merge = alineamiento_externo[['NUMERO DE DOCUMENTO', 'ALINEAMIENTO EXTERNO', 'NUMERO DE ENTIDADES SBS REPORTADAS ']]

df_resultado = anx06.merge(alineamiento_merge, 
                           left_on=['Número de Documento 10/'],
                           right_on=['NUMERO DE DOCUMENTO']
                           ,how='left')
df_resultado.drop(['NUMERO DE DOCUMENTO'], axis=1, inplace=True)

#%%
df_resultado['ALINEAMIENTO EXTERNO'] = df_resultado['ALINEAMIENTO EXTERNO'].fillna(df_resultado['Clasificación del Deudor con Alineamiento 15/'])
df_resultado['ALINEAMIENTO EXTERNO'] = df_resultado['ALINEAMIENTO EXTERNO'].astype(int)

df_resultado['Clasificación del Deudor con Alineamiento 15/'] = df_resultado['Clasificación del Deudor con Alineamiento 15/'].astype(int)

def max_calificacion(df_resultado):
    if df_resultado['ALINEAMIENTO EXTERNO'] > df_resultado['Clasificación del Deudor con Alineamiento 15/']:
        return df_resultado['ALINEAMIENTO EXTERNO']
    else:
        return df_resultado['Clasificación del Deudor con Alineamiento 15/']

df_resultado['MAX CALIFICACION'] = df_resultado.apply(max_calificacion, axis=1)
    
#%% cálculo de tasa de provisiones

def prov_alineadas_externamente(df_resultado):
    if df_resultado['MAX CALIFICACION'] == 0:
        if df_resultado['Tipo de Crédito 19/'] in ['12','11','10', '09','08']:                                                   
            return 0.01
        elif df_resultado['Tipo de Crédito 19/'] in ['13', '07', '06']:
            return 0.007
    elif df_resultado['Saldo de Garantías Autoliquidables 35/'] > 0:
        if df_resultado['MAX CALIFICACION'] in [1,2,3,4]:
            return 0.01
    elif df_resultado['Saldos de Garantías Preferidas 34/'] > 0:
        if df_resultado['MAX CALIFICACION'] == 1:
            return 0.025
        if df_resultado['MAX CALIFICACION'] == 2:
            return 0.125
        if df_resultado['MAX CALIFICACION'] == 3:
            return 0.30
        if df_resultado['MAX CALIFICACION'] == 4:
            return 0.60
    elif (df_resultado['Saldos de Garantías Preferidas 34/'] == 0) and \
        (df_resultado['Saldo de Garantías Autoliquidables 35/'] == 0):
        if df_resultado['MAX CALIFICACION'] == 1:
            return 0.05
        if df_resultado['MAX CALIFICACION'] == 2:
            return 0.25
        if df_resultado['MAX CALIFICACION'] == 3:
            return 0.6
        if df_resultado['MAX CALIFICACION'] == 4:
            return 1.00
    else:
        return ''

df_resultado['TASA PROV. CON AL. EXTERNO'] = df_resultado.apply(prov_alineadas_externamente, axis=1)

print(df_resultado[df_resultado['TASA PROV. CON AL. EXTERNO'] == ''])

df_resultado['Provisiones Requeridas A.EXTERNO'] = df_resultado['Cartera Neta'] * \
                                                  df_resultado['TASA PROV. CON AL. EXTERNO']
                                                  
#%%
df_resultado['Provisiones Requeridas A.EXTERNO'].sum()

para_excel = df_resultado[['''Nro Prestamo 
Fincore''', 'Número de Documento 10/', 'NUMERO DE ENTIDADES SBS REPORTADAS ',
                           'ALINEAMIENTO EXTERNO',
                           'MAX CALIFICACION',
                           'TASA PROV. CON AL. EXTERNO',
                           'Provisiones Requeridas A.EXTERNO']]

#%% AHORA CHAMBEAREMOS LA PESTAÑA E
detalle_entidad['CATEGORIA DE RIESGO EN LA ENTIDAD FINANCIERA'] = detalle_entidad['CATEGORIA DE RIESGO EN LA ENTIDAD FINANCIERA'].str.strip()
def alineamiento_numerico(detalle_entidad):
    if detalle_entidad['CATEGORIA DE RIESGO EN LA ENTIDAD FINANCIERA'] == 'NORMAL':
        return 0
    elif detalle_entidad['CATEGORIA DE RIESGO EN LA ENTIDAD FINANCIERA'] == 'SCAL':
        return 0
    elif detalle_entidad['CATEGORIA DE RIESGO EN LA ENTIDAD FINANCIERA'] == 'CPP':
        return 1
    elif detalle_entidad['CATEGORIA DE RIESGO EN LA ENTIDAD FINANCIERA'] == 'DEFICIENTE':
        return 2
    elif detalle_entidad['CATEGORIA DE RIESGO EN LA ENTIDAD FINANCIERA'] == 'DUDOSO':
        return 3
    elif detalle_entidad['CATEGORIA DE RIESGO EN LA ENTIDAD FINANCIERA'] == 'PERDIDA':
        return 4
    else:
        return ''

detalle_entidad['ALINEAMIENTO EXTERNO'] = detalle_entidad.apply(alineamiento_numerico, axis=1)

print('NÚMERO DE FILAS QUE NO HACEN MATCH:')
print(detalle_entidad[detalle_entidad['CATEGORIA DE RIESGO EN LA ENTIDAD FINANCIERA'] == ''].shape[0])

#%% nos quedamos con la fila de máxima calificación

# Encontrar el índice de la fila con la calificación más alta para cada 'socio'
indices_max_calificacion = detalle_entidad.groupby('NUMERO DE DOCUMENTO')['ALINEAMIENTO EXTERNO'].idxmax()

# Filtrar el DataFrame original utilizando los índices obtenidos
df_filtrado = detalle_entidad.loc[indices_max_calificacion]

#%% ahora solo falta un merge con la primera tabla que creamos

df_filtrado = df_filtrado[['NUMERO DE DOCUMENTO', 
                           'ENTIDAD FINANCIERA', 
                           'DEUDA TOTAL EN LA ENTIDAD', 
                           'CATEGORIA DE RIESGO EN LA ENTIDAD FINANCIERA']]
df_resultado = para_excel.merge(df_filtrado, 
                                left_on=['Número de Documento 10/'],
                                right_on=['NUMERO DE DOCUMENTO']
                                ,how='left')
df_resultado.drop(['NUMERO DE DOCUMENTO'], axis=1, inplace=True)

#%%

para_excel = df_resultado.copy()
para_excel = para_excel.rename(columns={'ENTIDAD FINANCIERA': 'ENTIDAD FINANCIERA CON PEOR CALIFICACION'})

#%% AGRUPAMIENTO DE LAS PROVISIONES REQUERIDAS
prov_requeridas_agrupadas = para_excel.groupby('Número de Documento 10/')['Provisiones Requeridas A.EXTERNO'].sum().reset_index()
prov_requeridas_agrupadas = prov_requeridas_agrupadas.rename(columns={'Provisiones Requeridas A.EXTERNO': 'Provisiones Requeridas A.EXTERNO AGRUPADO'})

#merge cuando la primary key en ambos dataframes tiene el mismo nombre
resultado = pd.merge(para_excel, #dataframe1
                     prov_requeridas_agrupadas, #dataframe2
                     on='Número de Documento 10/', #llave de unión
                     how='left') #tipo de unión

#%%
para_excel = resultado.copy()
#%% 'CREACIÓN DEL EXCEL'
'CREACIÓN DEL EXCEL'
nombre = "ANX06 con alineamiento externo.xlsx"
try:
    ruta = nombre
    os.remove(ruta)
except FileNotFoundError:
    pass

para_excel.to_excel(nombre,
                      index=False)

#%%
# POR SI NO SABEMOS DÓNDE ESTÁN LOS ARCHIVOS
# Obtener la ubicación actual
ubicacion_actual = os.getcwd()

# Imprimir la ubicación actual
print("La ubicación actual es: " + ubicacion_actual)

