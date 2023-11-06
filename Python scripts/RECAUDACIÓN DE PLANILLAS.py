# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 16:50:14 2023

@author: Joseph Montoya
"""

# =========================================================================== #
#                                                                             #  
#              AUTOMATIZACIÓN DE RECAUDACIÓN DE PLANILLAS                     #
#                                                                             #
# =========================================================================== #

import pandas as pd
import os
import pyodbc

#%%
# FECHA CORTE PARA SQL ========================================================
fecha_corte = '20230930'
# =============================================================================

# DIRECTORIO DE TRABAJO =======================================================
os.chdir('C:\\Users\\sanmiguel38\\Desktop\\RECAUDACIÓN\\2023 SETIEMBRE')
# =============================================================================

# RECAUDACIÓN DEL MES =========================================================
nombre = '09 - SETIEMBRE 2023 (PRELIMINAR).xlsx'
# =============================================================================

# UBICACIÓN DEL ANEXO 06=======================================================
ubi_anx = 'C:\\Users\\sanmiguel38\\Desktop'
# =============================================================================

# NOMBRE DEL ANEXO 06 =========================================================
anexo_06 = 'Rpt_DeudoresSBS Anexo06 - Setiembre 2023 - campos ampliados v04.xlsx'
# =============================================================================
#%%
# AQUÍ AÑADIMOS O QUITAMOS LAS PESTAÑAS DEL EXCEL, en el primero va el nombre de la columna
datos = {'cs': ['Masivo - CS'],
         'ml': ['Masivo - ML'],
         'av': ['Masivo - AV'],
         'kt': ['Masivo - KT'],
         }
datos = pd.DataFrame(datos)

dataframes = {}  # Diccionario para almacenar los DataFrames
# Creación de diccionario donde estarán almacenados los DataFrames
for columna in datos.columns:
    nombre_df = columna  # Utilizamos el nombre de la columna como nombre del DataFrame
    dataframes[nombre_df] = pd.read_excel(io = nombre, 
                                          sheet_name = datos[columna][0], 
                                          skiprows=4, 
                                          dtype={})

# =============================================================================
# cs = pd.read_excel(nombre,
#                    sheet_name = 'Masivo - CS',
#                    skiprows   = 4,
#                    dtype      = {})
# 
# ml = pd.read_excel(nombre,
#                    sheet_name = 'Masivo - ML',
#                    skiprows   = 4,
#                    dtype      = {})
# 
# av = pd.read_excel(nombre,
#                    sheet_name = 'Masivo - AV',
#                    skiprows   = 4,
#                    dtype      = {})
# 
# kt = pd.read_excel(nombre,
#                    sheet_name = 'Masivo - KT',
#                    skiprows   = 4,
#                    dtype      = {})
# 
# =============================================================================
# con el tiempo habría que añadir y/o retirar algunas de estas sheets de excel
# =============================================================================

#%% nos quedamos con las columnas necesarias y luego concatenamos los dataframes
columnas = ['PLANILLA',
            #'PROSEVA',
            'MONTO ENVIADO',
            'MONTO DEL MES',
            'RECIBIDO MASIVO',
            'PAGO INDEPENDIENTE',
            'REINTEGROS',
            'SALDO',
            '% COBRANZA']

# Filtramos las columnas necesarias, aquí también podríamos necesitar añadir o quitar algunas tablas
# al tener nuevos funcionarios o que dejen de trabajar
# df_sheets = [
#              cs[columnas],
#              ml[columnas],
#              av[columnas],
#              kt[columnas], 
#             ]

# Metemos los dataframes en una lista luego de filtrar las columnas necesarias para poder concatenarlos:
dataframes_filtrados = []
for nombre_columna, dataframe in dataframes.items():
    # Filtra las columnas en cada DataFrame
    dataframe_filtrado = dataframe[columnas]
    
    # Agrega el DataFrame filtrado a la lista
    dataframes_filtrados.append(dataframe_filtrado)
    
# Concatenamos
df_concatenado = pd.concat(dataframes_filtrados, 
                           ignore_index = True)

# Mayúsculas
df_concatenado['PLANILLA'] = df_concatenado['PLANILLA'].str.upper()

df_concatenado.to_excel('concatenado.xlsx',
                        index = False)

#%% CONECCIÓN AL SQL
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

base = pd.read_sql_query(f'''
DECLARE @fechacorte as datetime
SET @fechacorte = '{fecha_corte}'
---------------
SELECT 
	Nro_Fincore, CodigoSocio7, NumerodeCredito18, 
	Monedadelcredito17, ApellidosyNombresRazonSocial2,
	Saldodecolocacionescreditosdirectos24, CapitalenCobranzaJudicial30,
	CapitalVencido29, A.NUEVA_PLANILLA, A.PLANILLA,
    CASE
		WHEN A.PLANILLA = 'PLANILLA LIQUIDADOS' THEN A.NUEVA_PLANILLA
		ELSE A.PLANILLA
		END AS 'PLANILLA BIEN',
	a.Departamento, a.[Dpto Negocio],
	Situacion_Credito, Origen_Coopac, 
	P.EMPRESA, P.PLANILLA_CORREGIDA as 'PLANILLA_CORREGIDA',
	a.Departamento

FROM  
	anexos_riesgos2..Anx06_preliminar A

LEFT JOIN Anexos_Riesgos..PLANILLA2 P
	ON (LTRIM(RTRIM(A.NUEVA_PLANILLA)) =  LTRIM(RTRIM(P.NUEVA_PLANILLA)))
	WHERE FechaCorte1 = @fechacorte

''', conn)

del conn

# base = pd.read_excel(ubi_anx + '\\' + anexo_06,
#                      skiprows = 2)

#%% MERGE
df_concatenado.rename(columns={'PLANILLA': 'PLANILLA COBRANZAS'}, inplace = True)

df_resultado = base.merge(df_concatenado[['PLANILLA COBRANZAS', 
                                          'RECIBIDO MASIVO',
                                          'PAGO INDEPENDIENTE',
                                          'REINTEGROS',
                                          '% COBRANZA']], #AÑADIR LAS COLUMNAS QUE PODRÍAN SER NECESARIAS
                         left_on  = ['PLANILLA BIEN'], 
                         right_on = ['PLANILLA COBRANZAS'],
                         how      = 'left')

# vemos qué planillas del reporte de recaudación NO hacen match
# no_match = df_concatenado[~df_concatenado['PLANILLA COBRANZAS'].isin(base['PLANILLA BIEN'])] # coincidencia exacta

base_sin_duplicados = base[['PLANILLA BIEN', 'PLANILLA', 'NUEVA_PLANILLA']].drop_duplicates(subset=['PLANILLA BIEN'])
no_match = df_concatenado.merge(base_sin_duplicados, #AÑADIR LAS COLUMNAS QUE PODRÍAN SER NECESARIAS
                         left_on  = ['PLANILLA COBRANZAS'], 
                         right_on = ['PLANILLA BIEN'],
                         how      = 'left')

no_match = no_match[pd.isna(no_match['PLANILLA BIEN'])]

no_match[['PLANILLA COBRANZAS',
          'MONTO ENVIADO',
          'MONTO DEL MES',
          'RECIBIDO MASIVO',
          'PAGO INDEPENDIENTE',
          'REINTEGROS',
          'SALDO',
          '% COBRANZA']].to_excel('NO HACEN MATCH.xlsx', index = False)

#%% BUSCADOR DE NOMBRE DE LAS PLANILLAS
texto = 'tli alma'
aver = no_match[no_match['PLANILLA COBRANZAS'].str.contains(texto.upper(), 
                                                            na = False)]

#%% VERIFICACIÓN DE LOS QUE NO HACEN MATCH
# investigar = df_resultado[pd.isna(df_resultado['PLANILLA COBRANZAS'])]

# investigar.drop_duplicates(subset = 'PLANILLA BIEN', inplace = True)
# investigar = investigar[(investigar['PLANILLA BIEN'] != 'LIBRE DISPONIBILIDAD') &
#                         (investigar['PLANILLA BIEN'] != 'MICROEMPRESA')         &
#                         (investigar['PLANILLA BIEN'] != 'PEQUEÑA EMPRESA')]

# investigar.to_excel('NO HACEN MATCH.xlsx',
#                     index = False)
#%%
conn = pyodbc.connect('DRIVER=SQL Server;SERVER=(local);UID=sa;Trusted_Connection=Yes;APP=Microsoft Office 2016;WSID=SM-DATOS')

base_final = pd.read_sql_query(f'''
                DECLARE @fechacorte as datetime
                SET @fechacorte = '{fecha_corte}'

                SELECT 
                    haCorte1			as 'FechaCorte',
                    igoSocio7		as 'CodSocio',
                    erodeCredito18	as 'CodCredito',
                    edadelcredito17	as 'CodMoneda',
                    as 'Desc_Envio',
                    as 'Desc_pago',
                    as 'recaudacion',
                    _Fincore as 'Nro_Fincore'

                FROM  anexos_riesgos2..Anx06_preliminar A
                WHERE FechaCorte1 = @fechacorte
''', conn)

del conn

# AQUÍ PONERLE EL RESULTADO DEL OTRO, HACER UN MERGE


