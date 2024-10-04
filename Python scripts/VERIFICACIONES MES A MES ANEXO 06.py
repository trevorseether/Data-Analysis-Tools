# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 12:24:36 2023

@author: Joseph Montoya
"""

###########################################################
############# VERIFICACIONES DEL ANEXO06 ##################
###########################################################

#%% importación de módulos
import pandas as pd
import os
import pyodbc
# import numpy as np

#%%
FECHA_SQL = '20240831' #se pone la del mes anterior al mes que estamos procesando

os.chdir('C:\\Users\\sanmiguel38\\Desktop\\REPORTE DE REPROGRAMADOS (primer paso del anexo06)\\2024\\2024 setiembre\\productos')

anx06_final = 'Rpt_DeudoresSBS Anexo06 - Setiembre 2024 - campos ampliados procesado 01.xlsx'

#%% IMPORTACIÓN ANX06 DEL MES PASADO


QUERY = f'''
                            
declare @fecha as datetime
set @fecha = '{FECHA_SQL}'

select 
    Nro_Fincore, 
    ApellidosyNombresRazonSocial2, 
    FechadeNacimiento3,
    NumerodeDocumento10, 
    DiasdeMora33, 
    ClasificaciondelDeudorconAlineamiento15,
    NumerodeCredito18
from 
    anexos_riesgos2..Anx06_preliminar
where 
    FechaCorte1 = @fecha
order by 
    ApellidosyNombresRazonSocial2

'''

conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

df_mes_pasado = pd.read_sql_query(QUERY, conn)

del conn

if df_mes_pasado.shape[0] == 0:
    print('el anexo06 del mes pasado está vacío, posiblemente fecha mal puesta')
else:
    pass

df_mes_pasado['ApellidosyNombresRazonSocial2'] = df_mes_pasado['ApellidosyNombresRazonSocial2'].str.strip()
df_mes_pasado['NumerodeDocumento10'] = df_mes_pasado['NumerodeDocumento10'].str.strip()
df_mes_pasado['NumerodeCredito18'] = df_mes_pasado['NumerodeCredito18'].str.strip()

df_mes_pasado = df_mes_pasado.rename(columns={'ApellidosyNombresRazonSocial2': 'nombres y apellidos mes pasado'})
df_mes_pasado = df_mes_pasado.rename(columns={'FechadeNacimiento3'           : 'FechaNacimiento mes pasado'})
df_mes_pasado = df_mes_pasado.rename(columns={'NumerodeDocumento10'          : 'Documento mes pasado'})
df_mes_pasado = df_mes_pasado.rename(columns={'DiasdeMora33'                 : 'DíasMora mes pasado'})
df_mes_pasado = df_mes_pasado.rename(columns={'ClasificaciondelDeudorconAlineamiento15': 'Clasificación Alineamiento mes pasado'})
df_mes_pasado = df_mes_pasado.rename(columns={'NumerodeCredito18'            : 'Crédito 18 mes pasado'})

#%% ANEXO AMPLIADO MES ACTUAL
#leemos el anexo ampliado de este mes
df = pd.read_excel(anx06_final,
                 dtype={'Registro 1/'               : object, 
                        'Fecha de Nacimiento 3/'    : object,
                        'Código Socio 7/'           : object, 
                        'Número de Documento 10/'   : object,
                        'Relación Laboral con la Cooperativa 13/': object, 
                        'Código de Agencia 16/'     : object,
                        'Moneda del crédito 17/'    : object, 
                        'Numero de Crédito 18/'     : object,
                        'Tipo de Crédito 19/'       : object,
                        'Sub Tipo de Crédito 20/'   : object,
                        'Fecha de Desembolso 21/'   : object,
                        'Cuenta Contable 25/'       : object,
                        'Tipo de Producto 43/'      : object,
                        'Fecha de Vencimiento Origuinal del Credito 48/': object,
                        'Fecha de Vencimiento Actual del Crédito 49/'   : object,
                        'Nro Prestamo \nFincore'    : object},
                     skiprows = 2
                     )

#eliminación de filas vacías
df.dropna(subset=['Apellidos y Nombres / Razón Social 2/', 
                  'Fecha de Nacimiento 3/',
                  'Número de Documento 10/',
                  'Domicilio 12/',
                  'Numero de Crédito 18/'], inplace = True, how = 'all')

#limpieza de datos
df['Numero de Crédito 18/']                 = df['Numero de Crédito 18/'].str.strip()
df['Apellidos y Nombres / Razón Social 2/'] = df['Apellidos y Nombres / Razón Social 2/'].str.strip()
df['Número de Documento 10/']               = df['Número de Documento 10/'].str.strip()

print(df[pd.isna(df['Apellidos y Nombres / Razón Social 2/'])].shape[0])
print(df[pd.isna(df['Número de Documento 10/'])].shape[0])
print('si sale más de cero significa que hay nulo en alguna celda')

df = df.rename(columns={'Apellidos y Nombres / Razón Social 2/': 'nombres y apellidos mes actual'})

#%% FILTRADO DE COLUMNAS
#nos quedamos solo con las columnas necesarias
anx = df[['nombres y apellidos mes actual',
          'Fecha de Nacimiento 3/',
          'Número de Documento 10/',
          'Dias de Mora 33/',
          'Clasificación del Deudor con Alineamiento 15/',
          'Nro Prestamo \nFincore',
          'Numero de Crédito 18/'
          ]]

anx = anx.rename(columns={'Nro Prestamo \nFincore': "fincore"})

del df

#%% INTERSECCIÓN ENTRE MES ACTUAL Y MES PASADO
#filtramos el dataframe actual para que solo 
#tenga los números fincore que aparecen el
#mes pasado

df_filtrado = anx[anx['fincore'].isin(df_mes_pasado['Nro_Fincore'])]

#%% UNIÓN ENTRE AMBAS TABLAS

union = df_filtrado.merge(df_mes_pasado, 
                          how      = 'left', 
                          left_on  = ['fincore'], 
                          right_on = ['Nro_Fincore'])

#%%% verificamos nombres diferentes de un mes a otro

nombres_diferentes = union[union['nombres y apellidos mes actual'] != \
                           union['nombres y apellidos mes pasado']]
    
nombres_diferentes = nombres_diferentes[['fincore',
                                         'nombres y apellidos mes actual',
                                         'nombres y apellidos mes pasado'
                                         ]]

#%%% verificamos los documentos
documento_diferente = union[union['Documento mes pasado'] != \
                            union['Número de Documento 10/']]
    
documento_diferente = documento_diferente[['fincore',
                                           'Número de Documento 10/',
                                           'Documento mes pasado'
                                         ]]

#%%% verificamos fecha de nacimiento
#parseo de la fecha
formatos = ['%Y%m%d']
def parse_dates(date_str):
    for formato in formatos:
        try:
            return pd.to_datetime(date_str, format=formato)
        except ValueError:
            pass
    return pd.NaT
union['Fecha de Nacimiento 3/'] = union['Fecha de Nacimiento 3/'].apply(parse_dates)

#verificamos fecha de nacimiento
nacimiento_diferente = union[union['FechaNacimiento mes pasado'] != \
                            union['Fecha de Nacimiento 3/']]
nacimiento_diferente = nacimiento_diferente[['fincore',
                                             'Fecha de Nacimiento 3/',
                                             'FechaNacimiento mes pasado'
                                             ]]

#%%% verificamos días de mora > 31 días:
union['dif días de mora'] = union['Dias de Mora 33/'] - \
                            union['DíasMora mes pasado']

dias_mora = union[union['dif días de mora'] > 31]
dias_mora = dias_mora[['fincore',
                       'Dias de Mora 33/',
                       'DíasMora mes pasado',
                       'dif días de mora']]

#%%% diferencia de clasificación
union['dif clasificacion'] = union['Clasificación del Deudor con Alineamiento 15/'] - \
                             union['Clasificación Alineamiento mes pasado']

dif_clasificacion = union[(union['dif clasificacion'] < -1) |
                          (union['dif clasificacion'] > 1)]

dif_clasificacion = dif_clasificacion[['fincore',
                                       'Clasificación del Deudor con Alineamiento 15/',
                                       'Clasificación Alineamiento mes pasado']]

#%% verificamos cred 18 y nro fincore
def cred18_dif(union):
    if union['Numero de Crédito 18/'] != union['Crédito 18 mes pasado']:
        return 'dif'
    else:
        return ''
union['dif cred 18'] = union.apply(cred18_dif, axis = 1)

dif_cred_18 = union[union['dif cred 18'] == 'dif'][['fincore',
                                                    'Numero de Crédito 18/',
                                                    'Crédito 18 mes pasado']]

#%% concatenamos

x = union[['Nro_Fincore','Clasificación del Deudor con Alineamiento 15/', 
           'Clasificación Alineamiento mes pasado', 'dif clasificacion']]

#%%%
print(nombres_diferentes)
print(documento_diferente)
print(nacimiento_diferente)
print(dias_mora) #este sí es importante
print(dif_clasificacion)
print(dif_cred_18) #este hay que analizarlo, posiblemente hay cambios por alineamiento

