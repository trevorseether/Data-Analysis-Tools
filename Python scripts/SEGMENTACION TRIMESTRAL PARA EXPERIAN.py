# -*- coding: utf-8 -*-
"""
Created on Tue May 16 09:25:02 2023

@author: Joseph Montoya
"""

###############################################################################
##########     NUEVO REPORTE SEGMENTACIÓN     #################################
###############################################################################
# para Experian, la estructura es prácticamente la misma que del reporte de reprogramados
# antes este reporte era mensual, ahora es trimestral
# osea que elaboraremos de marzo, junio, setiembre y diciembre (en el mes siguiente)

#%% importación de módulos
import pandas as pd
import os 
# import pyodbc

#%% FECHA DE CORTE, DIRECTORIO DE TRABAJO

mes = 'DICIEMBRE 2023'
# ubicación
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\SEGMENTACIONES\\diciembre 2023') 
#en esta ubicación debemos poner el archivo de reprogramados que se manda a principio del mes

## donde dice @fechacorte se debe poner el mes ################################
# fecha_corte_sql = '20230930'                                                  #
###############################################################################
#este reporte es trimestral pero solo van los datos del último mes

## REPORTE DE REPROGRAMADOS QUE SE MANDA A EXPERIAN ###########################
repo_reprogramados = 'Diciembre Reprogramados - 2023.xlsx'
###############################################################################

#%% IMPORTACIÓN DEL ANEXO06 DEL SQL

# conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

# QUERY = f'''
# DECLARE @FECHA AS DATETIME
# SET @FECHA = '{fecha_corte_sql}'

# SELECT 
# 	CodigoSocio7 AS 'CODIGO SOCIO',
# 	TipodeDocumento9 AS 'TIPO DOCUMENTO',
# 	NumerodeDocumento10 AS 'NUMERO DOCUMENTO',
# 	TipodeCredito19 AS 'TIPO DE CREDITO',
# 	Saldodecolocacionescreditosdirectos24 - IngresosDiferidos42 as 'DEUDA DIRECTA',
# 	NULL as 'TIPO DE REPROGRAMACION',
# 	Reprogramados52 AS 'DEUDA REPROGRAMADA',
#   SaldosdeCreditosCastigados38

# FROM 
# 	anexos_riesgos2..Anx06_preliminar
# WHERE 
# 	FechaCorte1 = @FECHA
# ORDER BY ApellidosyNombresRazonSocial2           
#                        '''
                       
# df = pd.read_sql_query(QUERY, conn, dtype = {'TIPO DOCUMENTO' : str})
# del conn  #para limpiar el explorador de variables

# df = df[df['SaldosdeCreditosCastigados38'] == 0]
# del df['SaldosdeCreditosCastigados38']

#%% IMPORTACIÓN DEL ANEXO06 DEL EXCEL
ubi = 'C:\\Users\\sanmiguel38\\Desktop\\TRANSICION  ANEXO 6\\2023 DICIEMBRE\\V FINAL'
nom = 'Rpt_DeudoresSBS Anexo06 - Diciembre 2023 - campos ampliados version final.xlsx'

df = pd.read_excel(io = ubi + '\\' + nom, 
                   sheet_name = 'Diciembre 2023',
                   dtype = {'Código Socio 7/'         : str,
                            'Tipo de Documento 9/'    : str,
                            'Número de Documento 10/' : str,
                            'Tipo de Crédito 19/'     : str,
                            'Saldo de colocaciones (créditos directos) 24/' : float,
                            'Ingresos Diferidos 42/'  : float,
                            'Saldo Capital de Créditos Reprogramados 52/' : float,
                            'Saldos de Créditos Castigados 38/'           : float},
                   skiprows = 2)

df = df[df['Saldos de Créditos Castigados 38/'] == 0]

df = df[['Código Socio 7/',
         'Tipo de Documento 9/',
         'Número de Documento 10/',
         'Tipo de Crédito 19/',
         'Saldo de colocaciones (créditos directos) 24/',
         'Ingresos Diferidos 42/',
         'Saldo Capital de Créditos Reprogramados 52/']]

df.dropna(subset = ['Código Socio 7/',
         'Tipo de Documento 9/',
         'Número de Documento 10/',
         'Tipo de Crédito 19/'], 
          inplace = True, 
          how     = 'all')

columnas_rename = {'Código Socio 7/'         : 'CODIGO SOCIO',
                   'Tipo de Documento 9/'    : 'TIPO DOCUMENTO',
                   'Número de Documento 10/' : 'NUMERO DOCUMENTO',
                   'Tipo de Crédito 19/'     : 'TIPO DE CREDITO',
                   'Saldo Capital de Créditos Reprogramados 52/' : 'DEUDA REPROGRAMADA'}

df = df.rename(columns = columnas_rename)

df['Saldo de colocaciones (créditos directos) 24/'] = df['Saldo de colocaciones (créditos directos) 24/'].round(2)
df['Ingresos Diferidos 42/'] = df['Ingresos Diferidos 42/'].round(2)

df['DEUDA DIRECTA'] = df['Saldo de colocaciones (créditos directos) 24/'] - df['Ingresos Diferidos 42/']
df['DEUDA DIRECTA'] = df['DEUDA DIRECTA'].round(2)

print(df['Saldo de colocaciones (créditos directos) 24/'].sum())
print(df['Ingresos Diferidos 42/'].sum())
print(df['DEUDA DIRECTA'].sum())

del df['Saldo de colocaciones (créditos directos) 24/']
del df['Ingresos Diferidos 42/']

#%% DETECCIÓN DE ERRORES
#por si acaso hay que buscar si existe tipo de documento 0
errores= df[df['TIPO DOCUMENTO'] == 0]
#si hay, podemos corregir con un update en la misma base de datos
print(errores)

#%% STRIP DE TEXTO
df['CODIGO SOCIO'] = df['CODIGO SOCIO'].str.strip() 
df['NUMERO DOCUMENTO'] = df['NUMERO DOCUMENTO'].str.strip()

#%% IMPORTACIÓN DE LOS REPROGRAMADOS

reprogramados = pd.read_excel(repo_reprogramados,
                              skiprows = 1,
                              dtype = {'CODIGO SOCIO'    : object,
                                       'TIPO DOCUMENTO'  : str,
                                       'NUMERO DOCUMENTO': object,
                                       'TIPO DE CREDITO' : object})

#merge
para_merge = reprogramados[['CODIGO SOCIO','TIPO DE REPROGRAMACION']]
para_merge = para_merge.rename(columns = {'CODIGO SOCIO': 'cod para merge'})
para_merge = para_merge.rename(columns = {'TIPO DE REPROGRAMACION': 'tipo para merge'})

df_resultado = df.merge(para_merge, 
                         left_on  = ['CODIGO SOCIO'], 
                         right_on = ['cod para merge'],
                         how      = 'left')

df_resultado['TIPO DE REPROGRAMACION'] = df_resultado['tipo para merge']

df_resultado.drop(['cod para merge', 'tipo para merge'], axis=1, inplace=True)

#%% VERIFICACIÓN EL MERGE
#para comprobar si hizo buen match
#si la diferencia es diferente de cero hay que revisar
r = reprogramados['DEUDA REPROGRAMADA'].sum().round(2)
d = df_resultado['DEUDA REPROGRAMADA'].sum().round(2)

print('diferencia: ', r-d)
print('el resultado debe ser cero, sino no han hecho match todos los reprogramados del mes')

#%% ORDENAMIENTO DE COLUMNAS

df_resultado = df_resultado[['CODIGO SOCIO',
                             'TIPO DOCUMENTO',
                             'NUMERO DOCUMENTO',
                             'TIPO DE CREDITO',
                             'DEUDA DIRECTA',
                             'TIPO DE REPROGRAMACION',
                             'DEUDA REPROGRAMADA'
                             ]]
#%% CREACIÓN DEL EXCEL

nombre = 'SEGMENTACION '+ mes + ' Coopac San Miguel - Estructura Experian.xlsx'
try:
    ruta = nombre
    os.remove(ruta)
except FileNotFoundError:
    pass

df_resultado.to_excel(nombre,
                      sheet_name = mes,
                      index = False)


